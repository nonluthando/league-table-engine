import dataclasses

import pytest

from football_standings.domain import (
    Match,
    NoMatchesError,
    TeamStanding,
    compute_standings,
)


def test_compute_standings_raises_on_empty_matches():
    try:
        compute_standings([])
    except NoMatchesError:
        pass
    else:
        raise AssertionError("expected NoMatchesError")


def test_single_match_home_win_produces_standings_for_both_teams():
    matches = [Match("Derby County", "Everton", 2, 0)]

    standings = compute_standings(matches)

    assert [s.team for s in standings] == ["Derby County", "Everton"]

    derby, everton = standings
    assert derby.won == 1
    assert derby.drawn == 0
    assert derby.lost == 0
    assert derby.goals_for == 2
    assert derby.goals_against == 0
    assert derby.played == 1
    assert derby.points == 2

    assert everton.won == 0
    assert everton.drawn == 0
    assert everton.lost == 1
    assert everton.goals_for == 0
    assert everton.goals_against == 2
    assert everton.played == 1
    assert everton.points == 0


def test_draw_gives_both_teams_one_point():
    matches = [Match("Derby County", "Everton", 1, 1)]

    standings = compute_standings(matches)
    by_team = {s.team: s for s in standings}

    assert by_team["Derby County"].drawn == 1
    assert by_team["Derby County"].points == 1
    assert by_team["Everton"].drawn == 1
    assert by_team["Everton"].points == 1


def test_away_win_credits_away_team_with_the_win():
    matches = [Match("Derby County", "Everton", 0, 3)]

    standings = compute_standings(matches)
    by_team = {s.team: s for s in standings}

    assert by_team["Everton"].won == 1
    assert by_team["Everton"].points == 2
    assert by_team["Derby County"].lost == 1
    assert by_team["Derby County"].points == 0


def test_accumulates_across_multiple_matches_home_and_away():
    matches = [
        Match("Derby County", "Everton", 2, 0),
        Match("Liverpool", "Derby County", 1, 1),
        Match("Derby County", "Stoke City", 0, 1),
    ]

    standings = compute_standings(matches)
    derby = next(s for s in standings if s.team == "Derby County")

    assert derby.played == 3
    assert derby.won == 1
    assert derby.drawn == 1
    assert derby.lost == 1
    assert derby.goals_for == 2 + 1 + 0
    assert derby.goals_against == 0 + 1 + 1
    assert derby.points == 1 * 2 + 1 * 1


def test_standings_are_sorted_points_then_goal_average_then_goals_for():
    matches = [
        # Team T: 2 pts, goal_average 5/max(0,1) = 5.0 -> ranks 1st
        Match("Team T", "Loser1", 5, 0),
        # Team P and Team R both finish on 2 pts with goal_average 2.0
        # (4/2 == 2/1), separated only by goals_for (4 > 2).
        Match("Team P", "Loser2", 4, 2),
        Match("Team R", "Loser3", 2, 1),
    ]

    standings = compute_standings(matches)
    winners = [s.team for s in standings if s.won == 1]

    assert winners == ["Team T", "Team P", "Team R"]


def test_match_is_immutable():
    match = Match("Derby County", "Everton", 1, 0)

    with pytest.raises(dataclasses.FrozenInstanceError):
        match.home_goals = 2


def test_team_standing_is_immutable():
    standing = TeamStanding("Derby County", won=1, drawn=0, lost=0, goals_for=1, goals_against=0)

    with pytest.raises(dataclasses.FrozenInstanceError):
        standing.won = 2
