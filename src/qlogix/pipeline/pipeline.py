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
    name = "pipeline"

    def __init__(self):
        self.sources = create_sources(get_source_config())
        self.filters = create_filters(get_filter_config())
        self.analyze_ai = None
        self.analyze_passthrough = create_passthrough_analyze()
        self.sinks = create_sink(get_sink_config())

    def _get_ai_analyze(self):
        if self.analyze_ai is None:
            self.analyze_ai = create_ai_analyze()
        return self.analyze_ai

    def run(self, enable_ai_analyze=True):
        events: list[SourceBaseContent] = []

        for source in self.sources:
            with log_stage(logger, source.name):
                try:
                    with log_stage(logger, source.name):
                        source_events = source.fetch()
                    events.extend(source_events)
                except Exception as exc:
                    logger.warning("source failed, source=%s error=%r", source.name, exc)
        for filter_ in self.filters:
            with log_stage(logger, filter_.name):
                events = filter_.process(events)

        if len(events) == 0:
            logger.info("no events to analyze or sink after filtering")
            return

        if enable_ai_analyze:
            analyzer = self._get_ai_analyze()
            with log_stage(logger, analyzer.name):
                content = analyzer.run(events)
        else:
            with log_stage(logger, self.analyze_passthrough.name):
                content = self.analyze_passthrough.run(events)

        with log_stage(logger, "sink"):
            Sink.run(self.sinks, content)
