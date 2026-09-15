import io

import pytest

from football_standings.csv_reader import (
    CsvReadError,
    MalformedRowError,
    UnknownTeamError,
    read_matches,
)

HEADER = "home_team,away_team,home_goals,away_goals\n"


def test_single_valid_row_produces_one_match():
    stream = io.StringIO(HEADER + "Derby County,Everton,2,0\n")

    matches = read_matches(stream)

    assert len(matches) == 1
    match = matches[0]
    assert match.home_team == "Derby County"
    assert match.away_team == "Everton"
    assert match.home_goals == 2
    assert match.away_goals == 0


def test_multiple_rows_produce_matches_in_order():
    stream = io.StringIO(
        HEADER + "Derby County,Everton,2,0\n" + "Liverpool,Luton Town,1,1\n"
    )

    matches = read_matches(stream)

    assert [(m.home_team, m.away_team) for m in matches] == [
        ("Derby County", "Everton"),
        ("Liverpool", "Luton Town"),
    ]


def test_known_aliases_normalize_to_canonical_names():
    stream = io.StringIO(HEADER + "Wolves,Man City,1,1\n")

    [match] = read_matches(stream)

    assert match.home_team == "Wolverhampton Wanderers"
    assert match.away_team == "Manchester City"


def test_canonical_names_are_case_and_whitespace_insensitive():
    stream = io.StringIO(HEADER + "  derby county , EVERTON ,2,0\n")

    [match] = read_matches(stream)

    assert match.home_team == "Derby County"
    assert match.away_team == "Everton"


def test_unrecognized_team_name_raises_with_row_and_value():
    stream = io.StringIO(HEADER + "Derby County,Man Untied,2,0\n")

    with pytest.raises(UnknownTeamError) as exc_info:
        read_matches(stream)

    message = str(exc_info.value)
    assert "Man Untied" in message
    assert "row 2" in message


def test_wrong_column_count_raises_malformed_row_error():
    stream = io.StringIO(HEADER + "Derby County,Everton,2\n")

    with pytest.raises(MalformedRowError) as exc_info:
        read_matches(stream)

    assert "row 2" in str(exc_info.value)


def test_non_integer_goals_raises_malformed_row_error():
    stream = io.StringIO(HEADER + "Derby County,Everton,two,0\n")

    with pytest.raises(MalformedRowError):
        read_matches(stream)


def test_blank_lines_are_skipped():
    stream = io.StringIO(HEADER + "Derby County,Everton,2,0\n\nLiverpool,Luton Town,1,1\n")

    matches = read_matches(stream)

    assert len(matches) == 2


def test_reader_exceptions_are_csv_read_errors():
    assert issubclass(UnknownTeamError, CsvReadError)
    assert issubclass(MalformedRowError, CsvReadError)
