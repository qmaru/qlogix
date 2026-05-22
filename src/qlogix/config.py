import os
import tomllib
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

# root dir
ROOT_DIR = Path(__file__).resolve().parents[2]

# env var: QLOGIX_CONFIG, default to ROOT_DIR / "config.toml"
CONFIG_PATH = Path(os.getenv("QLOGIX_CONFIG", ROOT_DIR / "config.toml"))


class SourceType(StrEnum):
    FILE = "file"
    HTTP = "http"
    COMMAND = "command"
    SSH = "ssh"
    STDIN = "stdin"


class SinkType(StrEnum):
    FILE = "file"
    STDOUT = "stdout"
    TELEGRAM = "telegram"


class ShellType(StrEnum):
    CMD = "cmd"
    BASH = "bash"
    POWERSHELL = "powershell"


class AnalyzeProvider(StrEnum):
    OPENAI = "openai"
    GOOGLE = "google"


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

    @model_validator(mode="after")
    def validate_auth(self):
        if not self.password and not self.private_key:
            raise ValueError("must provide password or private_key")

        return self


class StdinSourceConfig(BaseSource):
    type: Literal["stdin"] = "stdin"


Source = Annotated[
    FileSourceConfig | HTTPSourceConfig | CommandSourceConfig | SSHSourceConfig | StdinSourceConfig,
    Field(discriminator="type"),
]


class Filter(BaseModel):
    plugins: list[str] = []


class Analyze(BaseModel):
    provider: AnalyzeProvider
    model: str
    api_key: str | None = None
    base_url: str | None = None
    system_prompt: str = "Analyze logs and provide concise insights."


class FileSinkConfig(BaseModel):
    type: Literal["file"] = "file"
    path: str

    @property
    def unique_key(self):
        return str(Path(self.path).expanduser().resolve())


class StdoutSinkConfig(BaseModel):
    type: Literal["stdout"] = "stdout"

    @property
    def unique_key(self):
        return "stdout"


class TelegramSinkConfig(BaseModel):
    type: Literal["telegram"] = "telegram"
    token: str | None = None  # QLOGIX_TELEGRAM_TOKEN
    chat_id: str | None = None  # QLOGIX_TELEGRAM_CHAT_ID

    @model_validator(mode="before")
    @classmethod
    def load_env(cls, data: dict | None):
        data = data or {}

        data["token"] = data.get("token") or os.getenv("QLOGIX_TELEGRAM_TOKEN")
        data["chat_id"] = data.get("chat_id") or os.getenv("QLOGIX_TELEGRAM_CHAT_ID")

        missing = []

        if not data["token"]:
            missing.append("QLOGIX_TELEGRAM_TOKEN")

        if not data["chat_id"]:
            missing.append("QLOGIX_TELEGRAM_CHAT_ID")

        if missing:
            raise ValueError(f"missing: {', '.join(missing)}")

        return data

    @property
    def unique_key(self) -> str:
        return f"telegram:{self.chat_id}"


Sink = Annotated[
    FileSinkConfig | StdoutSinkConfig | TelegramSinkConfig,
    Field(discriminator="type"),
]


class Config(BaseModel):
    source: list[Source]
    filter: Filter
    analyze: Analyze
    sink: list[Sink]

    @model_validator(mode="after")
    def validate_sink(self):
        seen: set[str] = set()

        for sink in self.sink:
            key = sink.unique_key
            if key in seen:
                raise ValueError(f"Duplicate sink: {key}")
            seen.add(key)

        return self


@lru_cache()
def __load_config() -> Config:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return Config.model_validate(data)


def get_source_config() -> list[Source]:
    return __load_config().source


def get_filter_config() -> Filter:
    return __load_config().filter


def get_analyze_config() -> Analyze:
    return __load_config().analyze


def get_sink_config() -> list[Sink]:
    return __load_config().sink
