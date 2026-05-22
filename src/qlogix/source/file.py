from pathlib import Path

from qlogix.source.base import Source, SourceBaseContent, SourceType


class FileSource(Source):
    def __init__(self, path: str | Path, source_name: str | None = None):
        self.path = Path(path)
        self.source_name = source_name

    def fetch(self) -> list[SourceBaseContent]:
        with self.path.open("r", encoding="utf-8") as f:
            return [
                SourceBaseContent(
                    source=SourceType.FILE, source_name=self.source_name, message=line.strip()
                )
                for line in f
                if line.strip()
            ]
