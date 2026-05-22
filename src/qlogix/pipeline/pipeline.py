from qlogix.config import get_filter_config, get_sink_config, get_source_config
from qlogix.sink.base import Sink
from qlogix.pipeline.factory import (
    create_ai_analyze,
    create_filters,
    create_passthrough_analyze,
    create_sink,
    create_sources,
)
from qlogix.source.base import SourceBaseContent


class Pipeline:
    def __init__(self):
        self.sources = create_sources(get_source_config())
        self.filters = create_filters(get_filter_config())
        self.analyze_ai = create_ai_analyze()
        self.analyze_passthrough = create_passthrough_analyze()
        self.sinks = create_sink(get_sink_config())

    def run(self, is_analyze=True):
        events: list[SourceBaseContent] = []

        for source in self.sources:
            events.extend(source.fetch())

        for filter_ in self.filters:
            events = filter_.process(events)

        if is_analyze:
            content = self.analyze_ai.run(events)
        else:
            content = self.analyze_passthrough.run(events)

        Sink.run(self.sinks, content)
