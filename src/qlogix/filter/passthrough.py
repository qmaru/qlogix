from qlogix.filter.base import Filter, FilterStage
from qlogix.source.base import SourceBaseContent


class PassthroughFilter(Filter):
    stage = FilterStage.PREPROCESS

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        return events
