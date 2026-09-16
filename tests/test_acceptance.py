import io
from pathlib import Path

from football_standings.app import run

DATA_DIR = Path(__file__).parent.parent / "data"


def test_week10_1974_75_standings_match_expected():
    with open(DATA_DIR / "week10_1974_75.csv") as input_stream:
        output_stream = io.StringIO()
        run(input_stream, output_stream)

    expected = (DATA_DIR / "expected_standings.csv").read_text()

    assert output_stream.getvalue() == expected
