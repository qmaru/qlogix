import os
import tomllib
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parents[2]

# 环境变量优先
CONFIG_PATH = Path(os.getenv("QLOGIX_CONFIG", ROOT_DIR / "config.toml"))


class SourceType(StrEnum):
    FILE = "file"
    HTTP = "http"
    COMMAND = "command"
    SSH = "ssh"
    STDIN = "stdin"


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


class Config(BaseModel):
    source: list[Source]
    filter: Filter
    analyze: Analyze


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
