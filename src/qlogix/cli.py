import argparse

from qlogix.analyze.ai import AIAnalyze
from qlogix.analyze.stats import StatsAnalyze
from qlogix.filter.base import Filter
from qlogix.pipeline.pipeline import Pipeline
from qlogix.source.command import CommandSource
from qlogix.source.file import FileSource
from qlogix.source.http import HTTPSource
from qlogix.source.ssh import SSHSource
from qlogix.source.stdin import StdinSource


def add_source_args(parser):
    parser.add_argument(
        "source_type",
        choices=["file", "ssh", "http", "command", "stdin"],
    )

    parser.add_argument(
        "--shell", choices=["default", "powershell", "cmd", "bash"], default="default"
    )

    parser.add_argument("--key", help="SSH private key path")
    parser.add_argument("--password", help="SSH password")

    parser.add_argument("target", nargs="?")


def load_events(args):
    if args.source_type == "file":
        return FileSource(args.target).fetch()

    if args.source_type == "http":
        return HTTPSource(args.target).fetch()

    if args.source_type == "ssh":
        return SSHSource(args.target).fetch()

    if args.source_type == "command":
        return CommandSource(args.target, args.shell).fetch()

    if args.source_type == "stdin":
        return StdinSource().fetch()

    raise ValueError("Invalid source type")


def get_parser():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="command")

    source_parser = sub.add_parser("source")
    add_source_args(source_parser)

    # Filter manager
    filter_parser = sub.add_parser("filter")
    add_source_args(filter_parser)
    filter_parser.add_argument("--list", action="store_true", help="List available filters")
    filter_parser.add_argument("plugin_name", nargs="?", help="Filter plugin name")

    # Analyze subparser with options for AI and stats
    analyze_parser = sub.add_parser("analyze")
    add_source_args(analyze_parser)
    analyze_parser.add_argument("analyzer", choices=["ai", "stats"], help="Analyzer type")

    return parser


def run():
    parser = get_parser()
    args = parser.parse_args()

    match args.command:
        case None:
            print(Pipeline().run())

        case "source":
            print(load_events(args))

        case "filter":
            if args.list:
                print(*Filter.names(), sep="\n")
                return

            events = load_events(args)
            plugin = Filter.load(args.plugin_name)
            print(plugin.process(events))

        case "analyze":
            events = load_events(args)

            analyzers = {
                "ai": AIAnalyze,
                "stats": StatsAnalyze,
            }

            result = analyzers[args.analyzer]().run(events)
            print(result)
