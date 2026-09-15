import io

from football_standings.csv_writer import write_standings
from football_standings.domain import TeamStanding


def test_single_standing_writes_header_and_one_row():
    standings = [
        TeamStanding("Derby County", won=8, drawn=1, lost=1, goals_for=25, goals_against=10)
    ]
    stream = io.StringIO()

    write_standings(stream, standings)

    lines = stream.getvalue().splitlines()
    assert lines[0] == "Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points"
    assert lines[1] == "1,Derby County,10,8,1,1,25,10,2.50,17"


def test_multiple_standings_number_position_by_input_order():
    standings = [
        TeamStanding("Derby County", won=8, drawn=1, lost=1, goals_for=25, goals_against=10),
        TeamStanding("Everton", won=6, drawn=2, lost=2, goals_for=20, goals_against=15),
    ]
    stream = io.StringIO()

    write_standings(stream, standings)

    lines = stream.getvalue().splitlines()
    assert lines[1].startswith("1,Derby County,")
    assert lines[2].startswith("2,Everton,")


def test_goal_average_is_formatted_to_two_decimal_places():
    standings = [
        TeamStanding("Everton", won=1, drawn=0, lost=0, goals_for=1, goals_against=3)
    ]
    stream = io.StringIO()

    write_standings(stream, standings)

    lines = stream.getvalue().splitlines()
    assert lines[1].endswith(",0.33,2")
