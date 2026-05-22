import argparse
import json

from qlogix.analyze.ai import AIAnalyze
from qlogix.analyze.stats import StatsAnalyze
from qlogix.config import ShellType, SourceType
from qlogix.filter.base import Filter
from qlogix.pipeline.pipeline import Pipeline
from qlogix.source.command import CommandSource
from qlogix.source.file import FileSource
from qlogix.source.http import HTTPSource
from qlogix.source.ssh import SSHSource
from qlogix.source.stdin import StdinSource


def add_source_args(parser):
    parser.add_argument("source_type", nargs="?", choices=[e.value for e in SourceType])

    parser.add_argument(
        "--shell", choices=[e.value for e in ShellType], default=ShellType.BASH.value
    )

    parser.add_argument("target", nargs="?")
    parser.add_argument("--key", help="SSH private key path")
    parser.add_argument("--password", help="SSH password")
    parser.add_argument("--source_name", help="Source name")


def load_events(args):
    if not args.source_type:
        raise ValueError("source_type required")

    if args.source_type == "file":
        return FileSource(args.target, source_name=args.source_name).fetch()

    if args.source_type == "http":
        return HTTPSource(args.target, source_name=args.source_name).fetch()

    if args.source_type == "ssh":
        return SSHSource(args.target, source_name=args.source_name).fetch()

    if args.source_type == "command":
        return CommandSource(args.target, args.shell, source_name=args.source_name).fetch()

    if args.source_type == "stdin":
        return StdinSource(source_name=args.source_name).fetch()

    raise ValueError("Invalid source type")


def get_parser():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("run", help="Run the default pipeline")

    source_parser = sub.add_parser("source")
    add_source_args(source_parser)

    # Filter manager
    filter_parser = sub.add_parser("filter")
    filter_parser.add_argument("--list", action="store_true", help="List available filters")
    filter_parser.add_argument("plugin_name", nargs="?", help="Filter plugin name")
    add_source_args(filter_parser)

    # Analyze subparser with options for AI and stats
    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("analyzer", choices=["ai", "stats"], help="Analyzer type")
    add_source_args(analyze_parser)

    return parser


def run():
    parser = get_parser()
    args = parser.parse_args()

    match args.command:
        case "run":
            result = Pipeline().run()
            print(result.model_dump_json(indent=2))

        case "source":
            events = load_events(args)
            print(json.dumps(events, indent=2))

        case "filter":
            if args.list:
                print(*Filter.names(), sep="\n")
                return

            events = load_events(args)
            plugin = Filter.load(args.plugin_name)

            result = plugin.process(events)
            print(json.dumps(result, indent=2))

        case "analyze":
            events = load_events(args)
            analyzers = {"ai": AIAnalyze, "stats": StatsAnalyze}
            result = analyzers[args.analyzer]().run(events)
            print(result.model_dump_json(indent=2))

        case _:
            parser.print_help()
