import httpx

from qlogix.source.base import Source


class APISource(Source):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch(self) -> list[dict]:
        response = httpx.get(self.api_url)
        response.raise_for_status()
        return [{"source": "api", "message": item} for item in response.json()]
