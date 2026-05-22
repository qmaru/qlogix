from pathlib import Path

from qlogix.sink.base import Sink
from qlogix.analyze.base import AnalyzeBaseContent


class FileSink(Sink):
    def __init__(self, path: str):
        self.path = Path(path)

    def write(self, content: AnalyzeBaseContent):
        try:
            payload = content.model_dump_json(ensure_ascii=False) + "\n"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(payload)

        except OSError as e:
            raise RuntimeError(f"Failed to write {self.path}: {e}") from e
