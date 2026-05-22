import argparse

from qlogix.analyze import ANALYZE_REGISTRY
from qlogix.analyze.base import AnalyzeBaseContent
from qlogix.analyze.passthrough import PassthroughAnalyze
from qlogix.config import ShellType, SourceType
from qlogix.filter.base import Filter
from qlogix.pipeline.pipeline import Pipeline
from qlogix.sink.base import Sink
from qlogix.sink.file import FileSink
from qlogix.sink.stdout import StdoutSink
from qlogix.sink.telegram import TelegramSink
from qlogix.source.command import CommandSource
from qlogix.source.file import FileSource
from qlogix.source.http import HTTPSource
from qlogix.source.ssh import SSHSource
from qlogix.source.stdin import StdinSource


def add_source_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "source_type", nargs="?", choices=[e.value for e in SourceType], help="Source type"
    )

    parser.add_argument(
        "source_spec", nargs="?", help="Source specification (e.g. file path, URL, command)"
    )

    # common args
    parser.add_argument("--source_name", default="cli", help="Source name")

    # command args
    parser.add_argument(
        "--shell",
        choices=[e.value for e in ShellType],
        default=ShellType.BASH.value,
        help="Shell type for command source",
    )

    # extra args for SSH
    parser.add_argument("--ssh-key", help="SSH private key path for ssh source")
    parser.add_argument("--ssh-password", help="SSH password for ssh source")


def load_events(args: argparse.Namespace):
    if not args.source_type:
        raise ValueError("source_type required")

    if args.source_type == "file":
        return FileSource(args.source_spec, source_name=args.source_name).fetch()

    if args.source_type == "http":
        return HTTPSource(args.source_spec, source_name=args.source_name).fetch()

    if args.source_type == "ssh":
        return SSHSource(
            args.source_spec,
            password=args.ssh_password,
            key=args.ssh_key,
            source_name=args.source_name,
        ).fetch()

    if args.source_type == "command":
        return CommandSource(args.source_spec, args.shell, source_name=args.source_name).fetch()

    if args.source_type == "stdin":
        return StdinSource(source_name=args.source_name).fetch()

    raise ValueError("Invalid source type")


def write_events(content: AnalyzeBaseContent, args: argparse.Namespace):
    if not args.sink_type:
        raise ValueError("sink_type required")

    if args.sink_type == "stdout":
        StdoutSink().write(content)
        return

    if args.sink_type == "file":
        path = args.sink_spec or "output.log"
        FileSink(path).write(content)
        return

    if args.sink_type == "telegram":
        TelegramSink().write(content)
        return

    raise ValueError("Invalid sink type")


def get_parser():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="Run the default pipeline")
    run_parser.add_argument(
        "--no_analyze", action="store_true", help="Run pipeline without analyze"
    )

    source_parser = sub.add_parser("source", help="Fetch events from a source")
    add_source_args(source_parser)

    # Filter manager
    filter_parser = sub.add_parser("filter", help="Apply a filter plugin to events")
    filter_parser.add_argument("--list", action="store_true", help="List available filters")
    filter_parser.add_argument("plugin_name", nargs="?", help="Filter plugin name")
    add_source_args(filter_parser)

    # Analyze subparser with options for AI and stats
    analyze_parser = sub.add_parser("analyze", help="Analyze events using AI or stats")
    analyze_parser.add_argument(
        "analyzer", choices=list(ANALYZE_REGISTRY.keys()), help="Analyzer type"
    )
    add_source_args(analyze_parser)

    # Sink
    sink_parser = sub.add_parser("sink", help="Send events to a sink")
    sink_parser.add_argument("--list", action="store_true", help="List available sinks")
    sink_parser.add_argument("sink_type", nargs="?", help="Sink type")
    add_source_args(sink_parser)
    sink_parser.add_argument("sink_spec", nargs="?", help="Sink specification (e.g. file path)")

    # Pipeline
    pipeline_parser = sub.add_parser("pipeline", help="Manaual pipeline execution")
    add_source_args(pipeline_parser)
    pipeline_parser.add_argument("filter_plugin", nargs="?", help="Filter plugin name")
    pipeline_parser.add_argument(
        "analyzer", nargs="?", choices=list(ANALYZE_REGISTRY.keys()), help="Analyzer type"
    )
    pipeline_parser.add_argument("sink_type", nargs="?", help="Sink type")
    pipeline_parser.add_argument("sink_spec", nargs="?", help="Sink specification (e.g. file path)")

    return parser


def run():
    parser = get_parser()
    args = parser.parse_args()

    match args.command:
        case "run":
            Pipeline().run(is_analyze=not args.no_analyze)

        case "source":
            events = load_events(args)
            for event in events:
                print(event.model_dump_json(indent=2, ensure_ascii=False))

        case "filter":
            if args.list:
                print(*Filter.names(), sep="\n")
                return

            events = load_events(args)
            plugin = Filter.load(args.plugin_name)

            results = plugin.process(events)
            for result in results:
                print(result.model_dump_json(indent=2, ensure_ascii=False))

        case "analyze":
            events = load_events(args)
            result = ANALYZE_REGISTRY[args.analyzer]().run(events)
            print(result.model_dump_json(indent=2, ensure_ascii=False))

        case "sink":
            if args.list:
                print(*Sink.names(), sep="\n")
                return

            events = load_events(args)
            content = PassthroughAnalyze().run(events)
            write_events(content, args)

        case "pipeline":
            events = load_events(args)

            if args.filter_plugin:
                plugin = Filter.load(args.filter_plugin)
                events = plugin.process(events)

            if args.analyzer:
                content = ANALYZE_REGISTRY[args.analyzer]().run(events)
            else:
                content = PassthroughAnalyze().run(events)

            write_events(content, args)

        case _:
            parser.print_help()
