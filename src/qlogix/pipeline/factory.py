from qlogix.analyze.ai import AIAnalyze
from qlogix.config import Filter as FilterType
from qlogix.config import Source as SourceType
from qlogix.filter.base import Filter
from qlogix.source.command import CommandSource
from qlogix.source.file import FileSource
from qlogix.source.http import HTTPSource
from qlogix.source.ssh import SSHSource
from qlogix.source.stdin import StdinSource


def create_sources(configs: list[SourceType]):
    sources = []

    for cfg in configs:
        source_name = cfg.source_name if cfg.source_name else "unknown"

        match cfg.type:
            case "file":
                if not cfg.path:
                    raise ValueError("File source requires 'path'")
                sources.append(FileSource(cfg.path, source_name=source_name))

            case "http":
                if not cfg.url:
                    raise ValueError("HTTP source requires 'url'")
                sources.append(HTTPSource(cfg.url, source_name=source_name))

            case "command":
                if not cfg.command:
                    raise ValueError("Command source requires 'command'")

                if not cfg.shell_type:
                    shell_type = "bash"
                else:
                    shell_type = cfg.shell_type

                sources.append(CommandSource(cfg.command, shell_type, source_name=source_name))

            case "ssh":
                if not cfg.url:
                    raise ValueError("SSH source requires 'url'")

                if not cfg.password and not cfg.private_key:
                    raise ValueError("SSH source requires either 'password' or 'private_key'")

                sources.append(
                    SSHSource(cfg.url, cfg.password, cfg.private_key, source_name=source_name)
                )

            case "stdin":
                sources.append(StdinSource(source_name=source_name))

    return sources


def create_filters(configs: FilterType):
    filters = []

    for plugin in configs.plugins:
        plugin = Filter.load(plugin)
        filters.append(plugin)

    return filters


def create_analyze():
    return AIAnalyze()
