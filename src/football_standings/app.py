"""Application layer: orchestrates the domain for a given use case.

Depends on the domain and the I/O modules, and is the only module that
wires them together. No argument parsing or process-exit logic lives
here; it operates on already-open streams. See docs/app-cli-design.md.
"""

from __future__ import annotations

from typing import TextIO

from football_standings.csv_reader import read_matches
from football_standings.csv_writer import write_standings
from football_standings.domain import compute_standings


def run(input_stream: TextIO, output_stream: TextIO) -> None:
    matches = read_matches(input_stream)
    standings = compute_standings(matches)
    write_standings(output_stream, standings)
