from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel, Field
from qlogix.source.base import SourceBaseContent


class AnalyzeBaseContent(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Analyze(Protocol):
    def run(self, events: list[SourceBaseContent]) -> AnalyzeBaseContent: ...
