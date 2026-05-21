from qlogix.analyze.ai import AIAnalyze
from qlogix.config import Filter as FilterType
from qlogix.config import Source as SourceType
from qlogix.filter.base import Filter
from qlogix.source.file import FileSource
from qlogix.source.http import HTTPSource


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
            sources.append(HTTPSource(cfg.url))

    return sources


def create_filters(configs: FilterType):
    filters = []

    for plugin in configs.plugins:
        plugin = Filter.load(plugin)
        filters.append(plugin)

    return filters


def create_analyze():
    return AIAnalyze()
