import re

from qlogix.filter.base import Filter, FilterType
from qlogix.source.base import SourceBaseContent


class NoColorFilter(Filter):
    stage = FilterType.MODIFY

    ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        for event in events:
            event.message = self.ANSI_ESCAPE.sub(
                "",
                str(event.message),
            )

        return events
