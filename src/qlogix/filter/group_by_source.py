from collections import defaultdict

from qlogix.filter.base import Filter
from qlogix.source.base import SourceBaseContent


class GroupBySourceFilter(Filter):
    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        groups = defaultdict(list)
        sources = {}

        for event in events:
            source_name = event.source_name or "unknown"
            groups[source_name].append(event.message)
            sources.setdefault(source_name, event.source)

        return [
            SourceBaseContent(
                source=sources[source_name], source_name=source_name, message=messages
            )
            for source_name, messages in groups.items()
        ]
