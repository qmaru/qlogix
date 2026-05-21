import sys

from qlogix.source.base import Source


class StdinSource(Source):
    def __init__(self):
        pass

    def fetch(self) -> list[dict]:
        return [{"source": "stdin", "message": line} for line in sys.stdin.read().splitlines()]
