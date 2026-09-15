import io

import pytest

from football_standings.app import run
from football_standings.csv_reader import UnknownTeamError
from football_standings.domain import NoMatchesError


def test_run_reads_computes_and_writes():
    input_stream = io.StringIO(
        "home_team,away_team,home_goals,away_goals\nDerby County,Everton,2,0\n"
    )
    output_stream = io.StringIO()

    run(input_stream, output_stream)

    lines = output_stream.getvalue().splitlines()
    assert lines[0] == "Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points"
    assert lines[1] == "1,Derby County,1,1,0,0,2,0,2.00,2"
    assert lines[2] == "2,Everton,1,0,0,1,0,2,0.00,0"


def test_run_propagates_unknown_team_error():
    input_stream = io.StringIO(
        "home_team,away_team,home_goals,away_goals\nDerby County,Man Untied,2,0\n"
    )
    output_stream = io.StringIO()

    with pytest.raises(UnknownTeamError):
        run(input_stream, output_stream)


def test_run_propagates_no_matches_error():
    input_stream = io.StringIO("home_team,away_team,home_goals,away_goals\n")
    output_stream = io.StringIO()

    with pytest.raises(NoMatchesError):
        run(input_stream, output_stream)
