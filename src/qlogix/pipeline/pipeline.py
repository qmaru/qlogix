from qlogix.config import get_filter_config, get_source_config
from qlogix.pipeline.factory import create_analyze, create_filters, create_sources
from qlogix.source.base import SourceBaseContent


class Pipeline:
    def __init__(self):
        self.sources = create_sources(get_source_config())
        self.filters = create_filters(get_filter_config())
        self.analyze = create_analyze()

    def run(self, is_analyze=True):
        events: list[SourceBaseContent] = []

        for source in self.sources:
            events.extend(source.fetch())

        for filter_ in self.filters:
            events = filter_.process(events)

        if is_analyze:
            return self.analyze.run(events)

        return events
