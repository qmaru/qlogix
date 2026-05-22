from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.source.base import SourceBaseContent


class AIContent(AnalyzeBaseContent):
    analysis: str


class PassthroughContent(AnalyzeBaseContent):
    events: list[SourceBaseContent]


class PassthroughAnalyze(Analyze):
    def run(self, events: list[SourceBaseContent]) -> AnalyzeBaseContent:
        return PassthroughContent(events=events)
