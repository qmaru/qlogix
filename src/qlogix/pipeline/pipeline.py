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

    def run(self, enable_ai_analyze=True, preview=False):
        events: list[SourceBaseContent] = []
        source_successes = 0
        source_failures = 0

        for source in self.sources:
            try:
                with log_stage(logger, source.name):
                    source_events = source.fetch()
                events.extend(source_events)
                source_successes += 1
            except Exception as exc:
                source_failures += 1
                logger.warning("source failed, source=%s error=%r", source.name, exc)

        logger.info(
            "source summary total=%d succeeded=%d failed=%d events=%d",
            len(self.sources),
            source_successes,
            source_failures,
            len(events),
        )

        if len(events) == 0:
            logger.info("no events fetched from any source")
            return

        for filter_ in self.filters:
            before_count = len(events)
            with log_stage(logger, filter_.name):
                events = filter_.process(events)
            after_count = len(events)
            logger.info(
                "filter summary filter=%s before=%d after=%d dropped=%d",
                filter_.name,
                before_count,
                after_count,
                before_count - after_count,
            )

        if len(events) == 0:
            logger.info("all events filtered out before analyze")
            return

        if preview:
            logger.info(
                "preview mode enabled ai=%s sinks=%s events=%d",
                enable_ai_analyze,
                [sink.name for sink in self.sinks],
                len(events),
            )
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
