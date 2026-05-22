import sys

from qlogix.source.base import Source, SourceBaseContent, SourceType


class StdinSource(Source):
    def __init__(self, source_name: str | None = None):
        self.source_name = source_name

    def fetch(self) -> list[SourceBaseContent]:
        return [
            SourceBaseContent(source=SourceType.STDIN, source_name=self.source_name, message=line)
            for line in sys.stdin.read().splitlines()
        ]
