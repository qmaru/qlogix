from collections import defaultdict

from qlogix.filter.base import Filter, FilterType
from qlogix.source.base import SourceBaseContent


class GroupBySourceFilter(Filter):
    stage = FilterType.AGGREGATE

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        groups = defaultdict(list)
        sources = {}

        for event in events:
            source_name = event.source_name or "unknown"
            groups[source_name].append(str(event.message))
            sources.setdefault(source_name, event.source)

        return [
            SourceBaseContent(
                source=sources[source_name], source_name=source_name, message="\n".join(messages)
            )
            for source_name, messages in groups.items()
        ]
