from typing import Protocol


class Analyze(Protocol):
    def run(self, events: list[dict]) -> str: ...
