import time
from pathlib import Path

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.sink.base import Sink
from qlogix.utils import DateFormat, get_current_date


class CacheSink(Sink):
    def __init__(self, dir: str, ttl_days: int = 3):
        self.path = Path(dir)
        self.ttl = ttl_days * 86400

        self.path.mkdir(parents=True, exist_ok=True)
        self._gc()

    def write(self, content: AnalyzeBaseContent):
        try:
            ts = get_current_date().strftime(DateFormat.FILENAME)
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
