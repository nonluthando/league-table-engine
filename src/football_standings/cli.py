"""CLI layer: parses command-line arguments and invokes the application layer.

No calculation or CSV-parsing logic lives here; this module only
translates CLI input/output into a call on app.run, and maps errors to
exit codes. See docs/app-cli-design.md.
"""

from __future__ import annotations

import argparse
import contextlib
import sys
from typing import IO

from football_standings.app import run
from football_standings.csv_reader import CsvReadError
from football_standings.domain import NoMatchesError


def _input_stream(path: str | None) -> contextlib.AbstractContextManager[IO[str]]:
    if path is None:
        return contextlib.nullcontext(sys.stdin)
    return open(path, "r", newline="")


def _output_stream(path: str | None) -> contextlib.AbstractContextManager[IO[str]]:
    if path is None:
        return contextlib.nullcontext(sys.stdout)
    return open(path, "w", newline="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="football-standings",
        description="Compute football league standings from match results.",
    )
    parser.add_argument("--input", "-i", help="input CSV file (default: stdin)")
    parser.add_argument("--output", "-o", help="output CSV file (default: stdout)")
    args = parser.parse_args(argv)

    try:
        with _input_stream(args.input) as input_stream, _output_stream(args.output) as output_stream:
            run(input_stream, output_stream)
    except (CsvReadError, NoMatchesError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
