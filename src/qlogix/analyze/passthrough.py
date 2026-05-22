from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.source.base import SourceBaseContent


class PassthroughContent(AnalyzeBaseContent):
    events: list[SourceBaseContent]


class PassthroughAnalyze(Analyze[PassthroughContent]):
    def run(self, events: list[SourceBaseContent]) -> PassthroughContent:
        return PassthroughContent(events=events, result="passthrough")
