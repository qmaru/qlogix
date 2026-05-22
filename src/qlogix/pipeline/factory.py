from qlogix.analyze.ai import AiAnalyze
from qlogix.analyze.passthrough import PassthroughAnalyze
from qlogix.config import Filter as FilterType
from qlogix.config import Sink as SinkType
from qlogix.config import Source as SourceType
from qlogix.filter.base import Filter
from qlogix.sink.base import Sink
from qlogix.sink.file import FileSink
from qlogix.sink.stdout import StdoutSink
from qlogix.sink.telegram import TelegramSink
from qlogix.source.base import Source
from qlogix.source.command import CommandSource
from qlogix.source.file import FileSource
from qlogix.source.http import HTTPSource
from qlogix.source.ssh import SSHSource
from qlogix.source.stdin import StdinSource


def create_sources(configs: list[SourceType]):
    sources: list[Source] = []

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
    return Filter.loads(configs.plugins)


def create_ai_analyze():
    return AiAnalyze()


def create_passthrough_analyze():
    return PassthroughAnalyze()


def create_sink(configs: list[SinkType]) -> list[Sink]:
    sinks: list[Sink] = []

    for config in configs:
        if config.type == "file":
            if not config.path:
                raise ValueError("File sink requires 'path'")
            sinks.append(FileSink(config.path))
        elif config.type == "stdout":
            sinks.append(StdoutSink())
        elif config.type == "telegram":
            sinks.append(TelegramSink(config))

    return sinks
