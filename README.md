# Football League Standings CLI

## Overview

A command-line tool that computes a football (soccer) league standings
table from match results. It reads match results from a CSV file (or
stdin), computes each team's record and ranks the table according to
1974/75-era English First Division rules, and writes the ranked
standings to a CSV file (or stdout).

The project's built-in dataset is the actual English First Division
results for the opening weeks of the 1974/75 season, but the
calculation logic itself does not assume that specific dataset — it
works for any set of matches between named teams.

## Requirements

- Python 3.9 or later
- No runtime dependencies (`pytest` and `ruff` are only needed for
  development — see Setup)

## Setup

Run from the repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This installs the package in editable mode, registers the
`football-standings` command, and installs the development
dependencies (`pytest`, `ruff`).

## Running the Application

Basic command:

```bash
football-standings --input <input.csv> --output <output.csv>
```

Arguments (both optional):

- `--input` / `-i <path>` — input CSV file. If omitted, matches are
  read from stdin.
- `--output` / `-o <path>` — output CSV file. If omitted, standings are
  written to stdout.

The command can also be run as a module without installing the entry
point:

```bash
python -m football_standings.cli --input <input.csv> --output <output.csv>
```

Using files:

```bash
football-standings --input data/week10_1974_75.csv --output standings.csv
```

Using stdin/stdout:

```bash
football-standings < data/week10_1974_75.csv > standings.csv
```

Example with the supplied historical dataset, printing straight to the
terminal:

```bash
football-standings --input data/week10_1974_75.csv
```

On success the command exits `0`. On a data error (malformed CSV,
unrecognized team name, no matches) it prints `Error: <message>` to
stderr and exits `1`. On invalid command-line usage it exits `2`
(argparse's default behaviour).

## Input Format

CSV with a header row, one row per already-played match:

```
home_team,away_team,home_goals,away_goals
```

Example:

```
home_team,away_team,home_goals,away_goals
Everton,Derby County,0,0
Manchester City,West Ham United,4,0
```

Validation rules:

- Each data row must have exactly 4 columns.
- `home_goals` and `away_goals` must be integers.
- Team names must be one of the 22 recognized 1974/75 First Division
  clubs, or a known alias (e.g. `Man City`, `Wolves`, `Spurs`, `QPR`,
  `Boro`, `Sheff Utd`, `West Ham` — matching is case- and
  whitespace-insensitive). An unrecognized team name is treated as an
  error rather than silently accepted, to catch typos.
- Blank lines are skipped.
- A file with a header but no match rows is an error — the tool
  expects at least one match.

Any validation failure is reported with the offending row number.

## Output Format

CSV with a header row, one row per team, ranked from first to last:

```
Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points
```

Example:

```
Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points
1,Manchester City,14,8,3,3,19,15,1.27,19
2,Liverpool,12,8,1,3,19,8,2.38,17
```

`Goal Average` is `goals for / goals against` (goals against treated as
1 if a team has conceded nothing, to avoid dividing by zero), formatted
to two decimal places. Teams are ranked by Points, then Goal Average,
then Goals For, all descending — the historical First Division
tiebreak order for this era (goal average, not goal difference, which
only replaced it from the 1976/77 season onward).

## Historical Dataset

`data/week10_1974_75.csv` contains English First Division match
results from the start of the 1974/75 season (17 August 1974) through
the end of the season's 10th calendar week (25 October 1974) — 144
matches across all 22 clubs. `data/expected_standings.csv` is the
corresponding verified standings table, computed independently of the
application code and cross-checked against the CLI's actual output.

Points are awarded 2 for a win and 1 for a draw (the pre-1981 English
league scoring system; 3 points for a win was not introduced until the
1981/82 season). Ranking uses points, then goal average, then goals
scored, per the rules actually in force for this competition at the
time.

Sourcing details, cross-checking, and known low-confidence points in
the dataset (none of which affect the computed table) are documented
in `docs/data-sourcing.md`.

## Testing

```bash
pytest
```

The suite covers:

- `test_domain.py` — standings derivation and ranking rules against
  synthetic matches, including immutability and tiebreak ordering.
- `test_csv_reader.py` — parsing, team-name normalization/aliasing,
  and malformed-input handling, against in-memory CSV text.
- `test_csv_writer.py` — output formatting, against in-memory streams.
- `test_app.py` — orchestration of read → compute → write.
- `test_cli.py` — argument parsing, file/stdio handling, and exit
  codes.
- `test_acceptance.py` — runs the full pipeline end-to-end against the
  real `data/week10_1974_75.csv` and checks the result against
  `data/expected_standings.csv`.

## Linting

```bash
ruff check .
```

Configured (in `pyproject.toml`) to catch undefined names, unused
imports/variables, import ordering, and overly complex functions — not
style preferences such as line length.

## Project Structure

```
src/football_standings/
  cli.py         Argument parsing, stream handling, exit codes
  app.py         Orchestrates read -> compute -> write
  domain.py      Core standings model and ranking rules (no I/O)
  csv_reader.py  Parses match CSV into domain objects
  csv_writer.py  Writes standings as CSV
tests/           Automated tests, one file per module above, plus
                 an end-to-end acceptance test
data/            The 1974/75 input dataset and its verified expected
                 output
docs/            Per-layer design records (domain, CSV I/O, app/CLI,
                 data sourcing)
```

## Architecture

The application is layered, with dependencies pointing inward toward
the domain: `cli.py` -> `app.py` -> `domain.py`, and `app.py` also
depends on `csv_reader.py`/`csv_writer.py`, which depend only on
`domain.py`. The domain layer has no knowledge of CSV, files, or the
CLI, so the standings logic can be tested and reused independently of
how matches are read in or the table is written out.

## Design Decisions and Assumptions

- **"The 10th week of the season" is interpreted as a calendar-week
  cutoff** (matches played through 25 October 1974), not "each team's
  10th match" — teams can therefore have differing games-played
  counts in the dataset. See `docs/data-sourcing.md`.
- **Goal average, not goal difference**, is used for ranking, matching
  the rules actually in force in 1974/75 rather than a later or more
  familiar convention.
- **Unrecognized team names are rejected, not guessed at** — a curated
  alias list handles known shorthand, but anything else raises an
  error rather than risking a silent mismatch.
- **Zero runtime dependencies** — the CLI, CSV handling, and domain
  logic are all implemented with the standard library.

## AI-Assisted Development

This project was built with AI assistance, and the following artefacts
document that process:

- [`CLAUDE.md`](CLAUDE.md) — the architecture and working agreement
  the AI assistant follows for this project.
- [`AI_REFLECTION.md`](AI_REFLECTION.md) — a running record of AI
  collaboration and notable decisions made along the way.
- `.claude/` and `ai/` — Claude Code session data and conversation
  history exports for this project.
