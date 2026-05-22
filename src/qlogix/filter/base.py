import re
from enum import IntEnum

from qlogix.source.base import SourceBaseContent


class FilterType(IntEnum):
    NONE = 0
    SELECT = 1
    MODIFY = 2
    EXPAND = 3
    REDUCE = 4
    AGGREGATE = 5


def camel_to_snake(name: str):
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    return name.lower()


class Filter:
    _registry: dict[str, type["Filter"]] = {}

    stage = FilterType.NONE

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = camel_to_snake(cls.__name__.removesuffix("Filter"))
        cls._registry[name] = cls

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._registry)

    @classmethod
    def load(cls, name: str) -> "Filter":
        return cls._registry[name]()

    @classmethod
    def loads(cls, names: list[str]) -> list["Filter"]:
        return sorted((cls.load(name) for name in names), key=lambda f: f.stage)

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        raise NotImplementedError(f"{self.__class__.__name__}.process() not implemented")
