import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from qlogix.analyze.base import AnalyzeBaseContent


def camel_to_snake(name: str):
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()


class Sink(ABC):
    _registry: dict[str, type["Sink"]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        name = camel_to_snake(cls.__name__.removesuffix("Sink"))
        cls._registry[name] = cls

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._registry)

    @classmethod
    def load(cls, name: str, **kwargs) -> "Sink":
        return cls._registry[name](**kwargs)

    @staticmethod
    def run(sinks: list["Sink"], content: AnalyzeBaseContent) -> None:
        if not sinks:
            return

        with ThreadPoolExecutor(max_workers=len(sinks)) as pool:
            futures = [pool.submit(sink.write, content) for sink in sinks]

            for future in futures:
                future.result()

    @abstractmethod
    def write(self, content: AnalyzeBaseContent) -> None:
        pass
