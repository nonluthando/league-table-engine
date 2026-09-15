"""CSV output adapter: writes league standings to a CSV destination.

Kept separate from the domain so the output format can change without
touching domain logic. See docs/csv-io-design.md for the agreed
schema. Operates on file-like (text stream) objects, never file
paths. Does not sort — the caller passes already-ranked standings.
"""

from __future__ import annotations

import csv
from typing import TextIO

from football_standings.domain import TeamStanding

_HEADER = [
    "Position",
    "Team",
    "Played",
    "Won",
    "Drawn",
    "Lost",
    "For",
    "Against",
    "Goal Average",
    "Points",
]


def write_standings(stream: TextIO, standings: list[TeamStanding]) -> None:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(_HEADER)

    for position, standing in enumerate(standings, start=1):
        writer.writerow(
            [
                position,
                standing.team,
                standing.played,
                standing.won,
                standing.drawn,
                standing.lost,
                standing.goals_for,
                standing.goals_against,
                f"{standing.goal_average:.2f}",
                standing.points,
            ]
        )
