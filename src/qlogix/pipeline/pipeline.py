from qlogix.config import get_filter_config, get_sink_config, get_source_config
from qlogix.logutil import get_logger, log_stage
from qlogix.pipeline.factory import (
    create_ai_analyze,
    create_filters,
    create_passthrough_analyze,
    create_sink,
    create_sources,
)
from qlogix.sink.base import Sink
from qlogix.source.base import SourceBaseContent

logger = get_logger(__name__)


class Pipeline:
    def __init__(self):
        self.sources = create_sources(get_source_config())
        self.filters = create_filters(get_filter_config())
        self.analyze_ai = create_ai_analyze()
        self.analyze_passthrough = create_passthrough_analyze()
        self.sinks = create_sink(get_sink_config())

    def run(self, is_analyze=True):
        events: list[SourceBaseContent] = []

        with log_stage(logger, "sources", source_count=len(self.sources)):
            for source in self.sources:
                source_name = source.__class__.__name__
                try:
                    with log_stage(logger, "source", source=source_name):
                        events.extend(source.fetch())
                except Exception as exc:
                    logger.warning(
                        "recoverable_failure stage=source source=%s error=%s",
                        source_name,
                        exc,
                    )

        with log_stage(logger, "filters", filter_count=len(self.filters), event_count=len(events)):
            for filter_ in self.filters:
                with log_stage(logger, "filter", filter=filter_.__class__.__name__):
                    events = filter_.process(events)

        analyzer_name = self.analyze_ai.__class__.__name__ if is_analyze else self.analyze_passthrough.__class__.__name__
        with log_stage(logger, "analyze", analyzer=analyzer_name, event_count=len(events)):
            if is_analyze:
                content = self.analyze_ai.run(events)
            else:
                content = self.analyze_passthrough.run(events)

        with log_stage(logger, "sinks", sink_count=len(self.sinks)):
            Sink.run(self.sinks, content)
