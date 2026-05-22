from qlogix.filter.base import Filter, FilterType
from qlogix.source.base import SourceBaseContent


class PassthroughFilter(Filter):
    stage = FilterType.NONE

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        return events
