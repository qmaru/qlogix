from collections import Counter
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from qlogix.analyze.base import Analyze


class StatsContent(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    total_events: int = 0
    source_counts: dict[str, int] = Field(default_factory=dict)
    summary: str | None = None


class StatsAnalyze(Analyze):
    def run(self, events: list[dict]) -> StatsContent:
        source_counts = Counter(event["source"] for event in events)
        return StatsContent(
            total_events=len(events),
            source_counts=dict(source_counts),
            summary=(f"{len(events)} events from {len(source_counts)} sources"),
        )
