# Application & CLI Design (Milestone 4)

Records the agreed shape for `app.py` and `cli.py` before any
implementation, following the same spec-first-then-TDD approach used
for the domain and I/O layers (`docs/domain-design.md`,
`docs/csv-io-design.md`).

## `app.py`

Single orchestration function:

```python
def run(input_stream: TextIO, output_stream: TextIO) -> None
```

Responsibility: read matches from `input_stream` (`csv_reader.read_matches`),
compute standings (`domain.compute_standings`), write them to
`output_stream` (`csv_writer.write_standings`). Nothing else.

- No exception handling — `CsvReadError` (and subtypes) and
  `NoMatchesError` propagate up to `cli.py` uncaught.
- No argument parsing, no file opening, no process-exit logic. Per
  CLAUDE.md, `app.py` operates only on already-open streams and is the
  one module that wires `domain.py` and the I/O modules together.

## `cli.py`

Responsibility: argument parsing, opening/closing streams, invoking
`app.run`, and mapping errors to exit codes. No calculation or
CSV-parsing logic lives here.

### Arguments

Using `argparse` (stdlib, no new dependency), explicit flags:

- `--input` / `-i <path>` — input file. Omitted → read from `stdin`.
- `--output` / `-o <path>` — output file. Omitted → write to `stdout`.

Files are opened in text mode via context managers (so they're closed
even on error); `stdin`/`stdout` are used directly when a flag is
omitted, never closed by us.

### Exit codes

- **`0`** — success.
- **`1`** — any caught data/processing error: `CsvReadError` (and its
  subtypes `UnknownTeamError`/`MalformedRowError`), `NoMatchesError`,
  or a file that can't be opened (`OSError`, e.g. `--input` pointing
  at a nonexistent path). The error's message is printed to `stderr`
  as `f"Error: {exc}"`.
- **`2`** — invalid CLI usage (bad/missing arguments) — this is
  `argparse`'s own built-in default when parsing fails; not something
  we implement ourselves.

This scheme was chosen over three alternatives considered: a distinct
exit code per exception type (rejected — nothing in the assignment
needs machine-distinguishable codes, and it adds an implicit contract
to maintain); following the BSD `sysexits.h` convention properly
(rejected — `argparse` already uses `2` for usage errors, not `64`, so
this would mean overriding built-in behavior for a convention few
modern CLI tools actually follow); and collapsing everything to just
`0`/`1` with no usage-error distinction (rejected — that would take
extra code to remove a distinction `argparse` already gives for free).

### Error message format

**Newly decided here, not discussed before:** on any exit-`1` error,
`cli.py` prints `f"Error: {exc}"` to `stderr` — a plain, minimal
prefix, relying on each exception's own message (already
row/value-specific for `csv_reader.py`'s exceptions) to carry the
detail. Flagging this as a small addition rather than assuming it
silently.

## Dependency boundaries

`cli.py` depends only on `app.py` (plus the standard library —
`argparse`, `sys`). `app.py` depends on `domain.py`, `csv_reader.py`,
and `csv_writer.py`. Matches CLAUDE.md's locked dependency direction.
