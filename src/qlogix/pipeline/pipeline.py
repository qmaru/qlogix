from qlogix.config import get_filter_config, get_source_config
from qlogix.pipeline.factory import create_analyze, create_filters, create_sources


class Pipeline:
    def __init__(self):
        self.sources = create_sources(get_source_config())
        self.filters = create_filters(get_filter_config())
        self.analyze = create_analyze()

    def run(self):
        events = []

        for source in self.sources:
            events.extend(source.fetch())

        for filter_ in self.filters:
            events = filter_.process(events)

        return self.analyze.run(events)
