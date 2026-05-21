from qlogix.source.file import FileSource
from qlogix.source.api import APISource
from qlogix.analyze.ai import AIAnalyze
from qlogix.filter.base import Filter
from qlogix.config import Source as SourceType, Filter as FilterType


def create_sources(configs: list[SourceType]):
    sources = []

    for cfg in configs:
        if cfg.type == "file":
            if not cfg.path:
                raise ValueError("File source requires 'path'")
            sources.append(FileSource(cfg.path))

        elif cfg.type == "api":
            if not cfg.url:
                raise ValueError("API source requires 'url'")
            sources.append(APISource(cfg.url))

    return sources


def create_filters(configs: FilterType):
    filters = []

    for plugin in configs.plugins:
        plugin = Filter.load(plugin)
        filters.append(plugin)

    return filters


def create_analyze():
    return AIAnalyze()
