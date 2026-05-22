from qlogix.filter.base import Filter
from qlogix.source.base import SourceBaseContent


class PassthroughFilter(Filter):
    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        return events
