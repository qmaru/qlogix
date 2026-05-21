from pathlib import Path

from qlogix.source.base import Source


class FileSource(Source):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def fetch(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8") as f:
            return [{"source": "file", "message": line.strip()} for line in f if line.strip()]
