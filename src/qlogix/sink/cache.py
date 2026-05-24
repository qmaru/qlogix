import time
from datetime import datetime
from pathlib import Path

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.sink.base import Sink


class CacheSink(Sink):
    def __init__(self, dir: str, ttl_days: int = 3):
        self.path = Path(dir)
        self.ttl = ttl_days * 86400
        self.filename_format = "%Y%m%d-%H%M%S"

        self.path.mkdir(parents=True, exist_ok=True)
        self._gc()

    def write(self, content: AnalyzeBaseContent):
        try:
            ts = datetime.now().strftime(self.filename_format)
            file = self.path / f"{ts}.txt"
            payload = content.model_dump_json(ensure_ascii=False) + "\n"
            file.write_text(payload, encoding="utf-8", newline="\n")

        except OSError as e:
            raise RuntimeError(f"Failed to write cache: {e}") from None

    def _gc(self):
        expire = time.time() - self.ttl

        for file in self.path.glob("*.txt"):
            try:
                if file.stat().st_mtime < expire:
                    file.unlink()
            except FileNotFoundError:
                pass
