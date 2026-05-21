from qlogix.filter.base import Filter


class DedupFilter(Filter):
    def process(self, events: list[dict]) -> list[dict]:
        seen = set()

        return [
            event
            for event in events
            if (msg := str(event["message"])) not in seen and not seen.add(msg)
        ]
