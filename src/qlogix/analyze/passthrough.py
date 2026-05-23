import json

from qlogix.analyze.base import Analyze, AnalyzeBaseContent
from qlogix.source.base import SourceBaseContent


class PassthroughContent(AnalyzeBaseContent):
    events: list[SourceBaseContent]


class PassthroughAnalyze(Analyze[PassthroughContent]):
    def run(self, events: list[SourceBaseContent]) -> PassthroughContent:
        result = [event.model_dump() for event in events]
        return PassthroughContent(
            events=events,
            result=json.dumps(result, indent=2, ensure_ascii=False),
        )
