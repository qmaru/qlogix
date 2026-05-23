from typing import Any, ClassVar, Protocol

from pydantic import BaseModel

from qlogix.config import SourceType
from qlogix.utils import camel_to_snake

__all__ = ["SourceType"]


class SourceBaseContent(BaseModel):
    source: SourceType
    source_name: str | None
    message: Any


class Source(Protocol):
    name: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not cls.name:
            cls.name = camel_to_snake(cls.__name__)

    def fetch(self) -> list[SourceBaseContent]: ...
