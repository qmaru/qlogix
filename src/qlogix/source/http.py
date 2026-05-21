import json
from typing import Any

import httpx

from qlogix.source.base import Source


class HTTPSource(Source):
    def __init__(self, url: str):
        self.url = url

    @staticmethod
    def _normalize(
        data: Any,
    ) -> list[dict]:
        if not isinstance(data, list):
            data = [data]

        return [{"source": "http", "message": item} for item in data]

    def fetch(self) -> list[dict]:
        with httpx.Client(timeout=30) as client:
            response = client.get(self.url)

        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            return self._normalize(response.json())

        if "application/x-ndjson" in content_type:
            return [json.loads(line) for line in response.text.splitlines() if line.strip()]

        return self._normalize(response.text.splitlines())
