# league-table-engine

A football league standings CLI application: reads match results from a CSV
file and outputs the computed league standings as CSV.

## Status

Milestone 0 — project scaffolding only. No application logic is implemented
yet; the layout below establishes the layered structure the project will
grow into.

## Architecture

```
CLI  ->  Application  ->  Domain
```

CSV input/output is kept as separate infrastructure, isolated from the
domain, so the core standings logic has no dependency on the CLI, CSV, or
filesystem.

```
src/football_standings/
  cli.py         CLI layer: argument parsing, invokes the application layer
  app.py         Application layer: orchestrates the domain for a use case
  domain.py      Domain layer: core league standings model and rules
  csv_reader.py  Reads match results from CSV
  csv_writer.py  Writes standings to CSV
```

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Linting

```bash
ruff check .
```
