from datetime import UTC, datetime
from typing import ClassVar, Protocol, TypeVar

from pydantic import BaseModel, Field

from qlogix.source.base import SourceBaseContent
from qlogix.utils import camel_to_snake


class AnalyzeBaseContent(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result: str


T = TypeVar("T", bound=AnalyzeBaseContent, covariant=True)


class Analyze(Protocol[T]):
    name: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not cls.name:
            cls.name = camel_to_snake(cls.__name__)

    def run(self, events: list[SourceBaseContent]) -> T: ...
