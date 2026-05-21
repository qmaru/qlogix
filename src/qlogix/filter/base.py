class Filter:
    _registry: dict[str, type["Filter"]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__name__.removesuffix("Filter").lower()
        cls._registry[name] = cls

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._registry)

    @classmethod
    def load(cls, name: str) -> "Filter":
        return cls._registry[name]()

    def process(self, events: list[dict]) -> list[dict]:
        raise NotImplementedError(f"{self.__class__.__name__}.process() not implemented")
