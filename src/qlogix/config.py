import os
import tomllib
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, ValidationError, model_validator

# root dir
ROOT_DIR = Path(__file__).resolve().parents[2]

CONFIG_NAME = "config.toml"


class Env(BaseModel):
    # main config
    QLOGIX_CONFIG: str | None = None
    # override
    QLOGIX_OPENAI_API_KEY: str | None = None
    QLOGIX_OPENAI_BASE_URL: str | None = None
    QLOGIX_TELEGRAM_TOKEN: str | None = None
    QLOGIX_TELEGRAM_CHAT_ID: str | None = None
    QLOGIX_FILTER_DATE: str | None = None  # YYYY-MM-DD, for today filter plugin
    # compatibility
    OPENAI_BASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None

    @classmethod
    def key(cls, name: str) -> str:
        return cls.model_fields[name].alias or name


env = Env.model_validate(os.environ)


def find_config() -> Path | None:
    candidates = []

    if env.QLOGIX_CONFIG:
        candidates.append(Path(env.QLOGIX_CONFIG))

    candidates.append(Path.cwd() / CONFIG_NAME)
    candidates.append(ROOT_DIR / CONFIG_NAME)

    for path in candidates:
        if path.is_file():
            return path.resolve()

    raise FileNotFoundError(
        f"cannot find {CONFIG_NAME}, searched:\n" + "\n".join(f"  - {p}" for p in candidates)
    )


class SourceType(StrEnum):
    FILE = "file"
    HTTP = "http"
    COMMAND = "command"
    SSH = "ssh"
    STDIN = "stdin"


class SinkType(StrEnum):
    FILE = "file"
    CACHE = "cache"
    STDOUT = "stdout"
    TELEGRAM = "telegram"


class ShellType(StrEnum):
    CMD = "cmd"
    BASH = "bash"
    POWERSHELL = "powershell"


class AnalyzeProvider(StrEnum):
    OPENAI = "openai"


class BaseSource(BaseModel):
    source_name: str | None = None


class FileSourceConfig(BaseSource):
    type: Literal["file"] = "file"
    path: str


class HTTPSourceConfig(BaseSource):
    type: Literal["http"] = "http"
    url: str


class CommandSourceConfig(BaseSource):
    type: Literal["command"] = "command"
    command: str
    shell_type: ShellType = ShellType.BASH


class SSHSourceConfig(BaseSource):
    type: Literal["ssh"] = "ssh"
    url: str
    password: str | None = None
    private_key: str | None = None
    command: str | None = None

    @model_validator(mode="after")
    def validate_auth(self):
        if not self.password and not self.private_key:
            raise ValueError("requires password or private_key")

        return self


class StdinSourceConfig(BaseSource):
    type: Literal["stdin"] = "stdin"


Source = Annotated[
    FileSourceConfig | HTTPSourceConfig | CommandSourceConfig | SSHSourceConfig | StdinSourceConfig,
    Field(discriminator="type"),
]


class Filter(BaseModel):
    plugins: list[str]


class Analyze(BaseModel):
    provider: AnalyzeProvider
    model: str
    api_key: str | None = None
    base_url: str | None = None
    thinking_level: Literal["minimal", "low", "medium", "high"] = "medium"
    system_prompt: str = "Analyze logs and provide concise insights."

    @model_validator(mode="before")
    @classmethod
    def load_env(cls, data: dict[str, Any] | None):
        data = dict(data or {})
        provider = data.get("provider")

        provider = AnalyzeProvider(provider)
        if provider == AnalyzeProvider.OPENAI:
            data["api_key"] = data.get("api_key") or env.QLOGIX_OPENAI_API_KEY or env.OPENAI_API_KEY
            data["base_url"] = (
                data.get("base_url") or env.QLOGIX_OPENAI_BASE_URL or env.OPENAI_BASE_URL
            )

        return data

    @model_validator(mode="after")
    def validate_required(self):
        return self


class FileSinkConfig(BaseModel):
    type: Literal["file"] = "file"
    path: str

    @property
    def unique_key(self):
        return str(Path(self.path).expanduser().resolve())


class CacheSinkConfig(BaseModel):
    type: Literal["cache"] = "cache"
    dir: str
    ttl_days: int

    @property
    def unique_key(self):
        return str(Path(self.dir).expanduser().resolve())


class StdoutSinkConfig(BaseModel):
    type: Literal["stdout"] = "stdout"

    @property
    def unique_key(self):
        return "stdout"


class TelegramSinkConfig(BaseModel):
    type: Literal["telegram"] = "telegram"
    token: str | None = None  # QLOGIX_TELEGRAM_TOKEN
    chat_id: str | None = None  # QLOGIX_TELEGRAM_CHAT_ID
    title: str | None = None  # Optional title for the sink

    @model_validator(mode="before")
    @classmethod
    def load_env(cls, data: dict | None):
        data = data or {}

        data["token"] = data.get("token") or Env.QLOGIX_TELEGRAM_TOKEN
        data["chat_id"] = data.get("chat_id") or Env.QLOGIX_TELEGRAM_CHAT_ID

        return data

    @model_validator(mode="after")
    def validate_model(self):
        self.validate_required()
        return self

    def validate_required(self):
        missing = []

        if not self.token:
            missing.append("token or env QLOGIX_TELEGRAM_TOKEN")

        if not self.chat_id:
            missing.append("chat_id or env QLOGIX_TELEGRAM_CHAT_ID")

        if missing:
            raise ValueError("requires " + ", ".join(missing))

    @property
    def unique_key(self) -> str:
        return f"telegram:{self.chat_id}"


Sink = Annotated[
    FileSinkConfig | CacheSinkConfig | StdoutSinkConfig | TelegramSinkConfig,
    Field(discriminator="type"),
]


class Config(BaseModel):
    source: list[Source]
    filter: Filter
    analyze: Analyze | None = None
    sink: list[Sink]

    @model_validator(mode="after")
    def validate_config(self):
        if not self.source:
            raise ValueError("at least one source entry is required")

        if not self.sink:
            raise ValueError("at least one sink entry is required")

        seen: set[str] = set()

        for sink in self.sink:
            key = sink.unique_key
            if key in seen:
                raise ValueError(f"Duplicate sink: {key}")
            seen.add(key)

        return self


class ConfigLoadError(ValueError):
    pass


@lru_cache()
def _load_config() -> Config:
    config_path = find_config()
    if not config_path:
        raise FileNotFoundError(f"cannot find config file: {CONFIG_NAME}")

    with config_path.open("rb") as f:
        data = tomllib.load(f)

    try:
        return Config.model_validate(data)
    except ValidationError as exc:
        lines = [f"invalid config: {config_path}"]

        for item in exc.errors(include_url=False):
            parts: list[str] = []
            for loc in item["loc"]:
                if isinstance(loc, int):
                    if parts:
                        parts[-1] = f"{parts[-1]}[{loc}]"
                    else:
                        parts.append(f"[{loc}]")
                else:
                    parts.append(str(loc))

            msg = str(item["msg"])
            if msg.startswith("Value error, "):
                msg = msg.removeprefix("Value error, ")
            elif msg == "Field required":
                msg = "is required"

            lines.append(f"- {'.'.join(parts) if parts else '<root>'}: {msg}")

        raise ConfigLoadError("\n".join(lines)) from None


def get_source_config() -> list[Source]:
    return _load_config().source


def get_filter_config() -> Filter:
    return _load_config().filter


def get_analyze_config() -> Analyze:
    config = _load_config()

    if config.analyze is None:
        raise ConfigLoadError(
            "missing analyze config: add analyze section or run qlogix-cli run --no_ai"
        )

    return config.analyze


def get_sink_config() -> list[Sink]:
    config = _load_config()

    if config.sink is None:
        return []

    return config.sink
