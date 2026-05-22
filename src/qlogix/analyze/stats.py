from collections import Counter

from pydantic import Field
from pydantic_ai import result

from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.source.base import SourceBaseContent


class StatsContent(AnalyzeBaseContent):
    total_events: int = 0
    source_counts: dict[str | None, int] = Field(default_factory=dict)


class StatsAnalyze(Analyze[StatsContent]):
    def run(self, events: list[SourceBaseContent]) -> StatsContent:
        source_counts = Counter(event.source_name for event in events)
        return StatsContent(
            total_events=len(events),
            source_counts=dict(source_counts),
            result=(f"{len(events)} events from {len(source_counts)} sources"),
        )
