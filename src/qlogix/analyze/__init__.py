import re

from qlogix.analyze.ai import AiAnalyze
from qlogix.analyze.base import Analyze
from qlogix.analyze.passthrough import PassthroughAnalyze
from qlogix.analyze.stats import StatsAnalyze

_ANALYZERS: list[type[Analyze]] = [
    AiAnalyze,
    StatsAnalyze,
    PassthroughAnalyze,
]


def class_to_key(cls: type[Analyze]) -> str:
    name = cls.__name__.removesuffix("Analyze")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


ANALYZE_REGISTRY = {class_to_key(cls): cls for cls in _ANALYZERS}
