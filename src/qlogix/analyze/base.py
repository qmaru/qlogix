from datetime import UTC, datetime
from typing import Protocol, TypeVar

from pydantic import BaseModel, Field

from qlogix.source.base import SourceBaseContent


class AnalyzeBaseContent(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result: str


T = TypeVar("T", bound=AnalyzeBaseContent, covariant=True)


class Analyze(Protocol[T]):
    def run(self, events: list[SourceBaseContent]) -> T: ...
