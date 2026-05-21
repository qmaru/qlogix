import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parents[2]

# 环境变量优先
CONFIG_PATH = Path(os.getenv("QLOGIX_CONFIG", ROOT_DIR / "config.toml"))


class Source(BaseModel):
    type: Literal["file", "api"]
    path: str | None = None
    url: str | None = None


class Filter(BaseModel):
    plugins: list[str] = []


class Analyze(BaseModel):
    provider: Literal["openai", "google"]
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
