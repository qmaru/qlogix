import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.logutil import get_logger


def camel_to_snake(name: str):
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()


logger = get_logger(__name__)


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
            failures: list[Exception] = []

            for sink, future in zip(sinks, futures, strict=False):
                try:
                    future.result()
                except Exception as exc:
                    logger.warning(
                        "recoverable_failure stage=sink sink=%s error=%s",
                        sink.__class__.__name__,
                        exc,
                    )
                    failures.append(exc)

        if failures and len(failures) == len(sinks):
            raise RuntimeError("All sinks failed")

    @abstractmethod
    def write(self, content: AnalyzeBaseContent) -> None:
        pass
