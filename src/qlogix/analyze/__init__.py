from qlogix.analyze.base import Analyze
from qlogix.analyze.passthrough import PassthroughAnalyze
from qlogix.analyze.stats import StatsAnalyze
from qlogix.analyze.ai import AIAnalyze


ANALYZE_REGISTRY: dict[str, type[Analyze]] = {
    "ai": AIAnalyze,
    "stats": StatsAnalyze,
    "passthrough": PassthroughAnalyze,
}
