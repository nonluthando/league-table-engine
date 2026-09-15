"""CSV input adapter: reads match results from a CSV source.

Kept separate from the domain so the input format can change without
touching domain logic. See docs/csv-io-design.md for the agreed shape
and rationale. Operates on file-like (text stream) objects, never
file paths.
"""

from __future__ import annotations

import csv
from typing import TextIO

from football_standings.domain import Match

CANONICAL_TEAMS = [
    "Derby County",
    "Liverpool",
    "Ipswich Town",
    "Everton",
    "Stoke City",
    "Sheffield United",
    "Middlesbrough",
    "Manchester City",
    "Leeds United",
    "Burnley",
    "Queens Park Rangers",
    "Wolverhampton Wanderers",
    "West Ham United",
    "Coventry City",
    "Newcastle United",
    "Arsenal",
    "Birmingham City",
    "Leicester City",
    "Tottenham Hotspur",
    "Luton Town",
    "Chelsea",
    "Carlisle United",
]

_ALIASES = {
    "man city": "Manchester City",
    "wolves": "Wolverhampton Wanderers",
    "spurs": "Tottenham Hotspur",
    "qpr": "Queens Park Rangers",
    "boro": "Middlesbrough",
    "sheff utd": "Sheffield United",
    "west ham": "West Ham United",
}

_CANONICAL_BY_KEY = {team.casefold(): team for team in CANONICAL_TEAMS}


class CsvReadError(Exception):
    """Base class for csv_reader.py failures."""


class UnknownTeamError(CsvReadError):
    """Raised when a team name cannot be normalized to a known club."""


class MalformedRowError(CsvReadError):
    """Raised when a row's structure or values are invalid."""


def _normalize_team(raw: str, row_number: int) -> str:
    key = raw.strip().casefold()
    if key in _ALIASES:
        return _ALIASES[key]
    if key in _CANONICAL_BY_KEY:
        return _CANONICAL_BY_KEY[key]
    raise UnknownTeamError(
        f'"{raw}" (row {row_number}) is not a recognized First Division '
        "club or known alias — check for a typo."
    )


def _parse_goals(raw: str, row_number: int) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise MalformedRowError(
            f'row {row_number} has an invalid goals value: "{raw}"'
        ) from exc


def read_matches(stream: TextIO) -> list[Match]:
    matches = []
    reader = csv.reader(stream)
    next(reader, None)  # header row

    for row_number, row in enumerate(reader, start=2):
        if not row:
            continue
        if len(row) != 4:
            raise MalformedRowError(
                f"row {row_number} has {len(row)} columns, expected 4"
            )
        home_raw, away_raw, home_goals_raw, away_goals_raw = row
        home_team = _normalize_team(home_raw, row_number)
        away_team = _normalize_team(away_raw, row_number)
        home_goals = _parse_goals(home_goals_raw, row_number)
        away_goals = _parse_goals(away_goals_raw, row_number)
        matches.append(Match(home_team, away_team, home_goals, away_goals))

    return matches
