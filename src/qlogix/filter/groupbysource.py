from collections import defaultdict

from qlogix.filter.base import Filter


class GroupBySourceFilter(Filter):
    def process(self, events: list[dict]) -> list[dict]:
        groups = defaultdict(list)

        for event in events:
            source_name = event.get("source_name", "unknown")
            groups[source_name].append(event["message"])

        return [
            {"source_name": source_name, "messages": messages}
            for source_name, messages in groups.items()
        ]
