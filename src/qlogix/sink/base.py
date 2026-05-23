from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar

from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.logutil import get_logger, log_stage
from qlogix.utils import camel_to_snake

logger = get_logger(__name__)


class Sink(ABC):
    key: ClassVar[str] = ""
    name: ClassVar[str] = ""

    _registry: dict[str, type["Sink"]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not cls.key:
            cls.key = camel_to_snake(cls.__name__.removesuffix("Sink"))

        if not cls.name:
            cls.name = camel_to_snake(cls.__name__)

        cls._registry[cls.key] = cls

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._registry)

    @classmethod
    def load(cls, key: str) -> "Sink":
        return cls._registry[key]()

    @staticmethod
    def run(sinks: list["Sink"], content: AnalyzeBaseContent) -> None:
        if not sinks:
            return

        with ThreadPoolExecutor(max_workers=len(sinks)) as pool:
            futures = [pool.submit(sink.write, content) for sink in sinks]
            failures: list[Exception] = []

            for sink, future in zip(sinks, futures, strict=False):
                try:
                    with log_stage(logger, sink.name):
                        future.result()
                except Exception as exc:
                    logger.warning("init failed, sink=%s error=%s", sink.name, exc)
                    failures.append(exc)

        if failures and len(failures) == len(sinks):
            raise RuntimeError("All sinks failed")

    @abstractmethod
    def write(self, content: AnalyzeBaseContent) -> None:
        pass
