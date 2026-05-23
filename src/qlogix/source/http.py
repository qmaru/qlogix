import json
from functools import partial
from typing import Any

import httpx

from qlogix.logutil import get_logger, log_external_call
from qlogix.source.base import Source, SourceBaseContent, SourceType

logger = get_logger(__name__)


class HTTPSource(Source):
    def __init__(self, url: str, source_name: str | None = None):
        self.url = url
        self.source_name = source_name

    @staticmethod
    def _normalize(data: Any, source_name: str | None = None) -> list[SourceBaseContent]:
        if not isinstance(data, list):
            data = [data]

        return [
            SourceBaseContent(source=SourceType.HTTP, source_name=source_name, message=item)
            for item in data
        ]

    def fetch(self) -> list[SourceBaseContent]:
        with httpx.Client(timeout=30) as client:
            response = log_external_call(
                logger, "http.get", partial(client.get, self.url, timeout=30)
            )
            response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()

        if "application/json" in content_type or content_type.endswith("+json"):
            return self._normalize(response.json(), self.source_name)

        if "application/x-ndjson" in content_type:
            return self._normalize(
                [json.loads(line) for line in response.text.splitlines() if line.strip()],
                self.source_name,
            )

        return self._normalize(response.text.splitlines(), self.source_name)
