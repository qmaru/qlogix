import sys

from qlogix.source.base import Source


class StdinSource(Source):
    def __init__(self, source_name: str | None = None):
        self.source_name = source_name

    def fetch(self) -> list[dict]:
        return [
            {"source": "stdin", "source_name": self.source_name, "message": line}
            for line in sys.stdin.read().splitlines()
        ]
