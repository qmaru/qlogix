from enum import IntEnum
from typing import ClassVar

from qlogix.source.base import SourceBaseContent
from qlogix.utils import camel_to_snake


class FilterType(IntEnum):
    NONE = 0
    SELECT = 1
    MODIFY = 2
    EXPAND = 3
    REDUCE = 4
    AGGREGATE = 5


class Filter:
    key: ClassVar[str] = ""
    name: ClassVar[str] = ""

    _registry: dict[str, type["Filter"]] = {}

    stage = FilterType.NONE

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not cls.key:
            cls.key = camel_to_snake(cls.__name__.removesuffix("Filter"))

        if not cls.name:
            cls.name = camel_to_snake(cls.__name__)

        cls._registry[cls.key] = cls

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._registry)

    @classmethod
    def load(cls, key: str) -> "Filter":
        return cls._registry[key]()

    @classmethod
    def loads(cls, keys: list[str]) -> list["Filter"]:
        return sorted((cls.load(key) for key in keys), key=lambda f: f.stage)

    def process(self, events: list[SourceBaseContent]) -> list[SourceBaseContent]:
        raise NotImplementedError(f"{self.__class__.__name__}.process() not implemented")
