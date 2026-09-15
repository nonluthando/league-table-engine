import io

import pytest

from football_standings.cli import main

VALID_CSV = "home_team,away_team,home_goals,away_goals\nDerby County,Everton,2,0\n"


def test_main_reads_and_writes_given_files(tmp_path):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    input_path.write_text(VALID_CSV)

    exit_code = main(["--input", str(input_path), "--output", str(output_path)])

    assert exit_code == 0
    lines = output_path.read_text().splitlines()
    assert lines[0] == "Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points"
    assert lines[1] == "1,Derby County,1,1,0,0,2,0,2.00,2"


def test_main_defaults_to_stdin_and_stdout(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(VALID_CSV))

    exit_code = main([])

    assert exit_code == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points"
    assert out[1] == "1,Derby County,1,1,0,0,2,0,2.00,2"


def test_main_returns_1_and_prints_error_on_malformed_input(monkeypatch, capsys):
    bad_csv = "home_team,away_team,home_goals,away_goals\nDerby County,Man Untied,2,0\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(bad_csv))

    exit_code = main([])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert err.startswith("Error: ")
    assert "Man Untied" in err


def test_main_returns_1_on_missing_input_file(tmp_path, capsys):
    missing_path = tmp_path / "does_not_exist.csv"

    exit_code = main(["--input", str(missing_path)])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert err.startswith("Error: ")


def test_main_exits_2_on_invalid_arguments():
    with pytest.raises(SystemExit) as exc_info:
        main(["--not-a-real-flag"])

    assert exc_info.value.code == 2
