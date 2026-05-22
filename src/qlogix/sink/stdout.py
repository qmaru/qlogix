from qlogix.sink.base import Sink
from qlogix.analyze.base import AnalyzeBaseContent


class StdoutSink(Sink):
    def write(self, content: AnalyzeBaseContent):
        print(content.model_dump_json(ensure_ascii=False))
