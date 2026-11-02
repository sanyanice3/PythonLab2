import argparse
import logging
import os
import sys

from .analysis import analyze
from .errors import CliConfigError, StreamStatsError
from .report import report_text


def run(args):
    for path in args.inputs:
        if not os.path.isfile(path):
            raise CliConfigError(f"файл не найден: {path}")
    stats = analyze(args.inputs, args.format, args.skip_invalid)
    text = report_text(stats)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(text)
    else:
        print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="streamstats")
    commands = parser.add_subparsers(dest="command", required=True)
    analyze_parser = commands.add_parser("analyze")
    analyze_parser.add_argument("inputs", nargs="+", metavar="INPUT")
    analyze_parser.add_argument("--format", required=True, help="csv или jsonl")
    analyze_parser.add_argument("--output", metavar="REPORT.json")
    analyze_parser.add_argument("--skip-invalid", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run(args)
    except StreamStatsError as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
