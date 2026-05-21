from qlogix.analyze.base import Analyze


class StatsAnalyze(Analyze):
    def run(self, events: list[dict]) -> str:
        return f"total events: {len(events)}"
