from qlogix.filter.base import Filter, FilterStage
from qlogix.source.base import SourceBaseContent


class DedupFilter(Filter):
    stage = FilterStage.REDUCE

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        seen = set()

        return [
            event
            for event in events
            if (msg := str(event.message)) not in seen and not seen.add(msg)
        ]
