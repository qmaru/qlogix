from qlogix.filter.base import Filter


class PassthroughFilter(Filter):
    def process(self, events: list[dict]) -> list[dict]:
        return events
