"""Domain layer: core league standings model and rules.

This module must remain free of any dependency on the CLI, CSV, or
filesystem so the domain stays usable from any future interface (CLI,
API, UI) without rewriting it. See docs/domain-design.md for the
agreed shape and rationale.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


class NoMatchesError(Exception):
    """Raised when compute_standings is given no matches to process."""


@dataclass(frozen=True)
class Match:
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int


@dataclass(frozen=True)
class TeamStanding:
    team: str
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int

    @property
    def played(self) -> int:
        return self.won + self.drawn + self.lost

    @property
    def points(self) -> int:
        return self.won * 2 + self.drawn

    @property
    def goal_average(self) -> float:
        return self.goals_for / max(self.goals_against, 1)


def _outcome(goals_for: int, goals_against: int) -> tuple[int, int, int]:
    """Return (won, drawn, lost) as 0/1 flags for one side of a match."""
    if goals_for > goals_against:
        return (1, 0, 0)
    if goals_for < goals_against:
        return (0, 0, 1)
    return (0, 1, 0)


def compute_standings(matches: Iterable[Match]) -> list[TeamStanding]:
    matches = list(matches)
    if not matches:
        raise NoMatchesError("compute_standings requires at least one match")

    totals: dict[str, list[int]] = {}

    def add(team: str, goals_for: int, goals_against: int) -> None:
        won, drawn, lost = _outcome(goals_for, goals_against)
        record = totals.setdefault(team, [0, 0, 0, 0, 0])
        record[0] += won
        record[1] += drawn
        record[2] += lost
        record[3] += goals_for
        record[4] += goals_against

    for match in matches:
        add(match.home_team, match.home_goals, match.away_goals)
        add(match.away_team, match.away_goals, match.home_goals)

    standings = [
        TeamStanding(
            team=team,
            won=won,
            drawn=drawn,
            lost=lost,
            goals_for=goals_for,
            goals_against=goals_against,
        )
        for team, (won, drawn, lost, goals_for, goals_against) in totals.items()
    ]

    standings.sort(key=lambda s: (s.points, s.goal_average, s.goals_for), reverse=True)
    return standings
