from typing import Protocol, Any

from pydantic import BaseModel
from qlogix.config import SourceType

__all__ = ["SourceType"]


class SourceBaseContent(BaseModel):
    source: SourceType
    source_name: str | None
    message: Any


class Source(Protocol):
    def fetch(self) -> list[SourceBaseContent]: ...
