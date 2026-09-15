# MILESTONES.md

Milestone plan for the football league standings CLI (SPAN Digital coding
assessment). Each milestone is a checkpoint with explicit pass criteria;
see `CLAUDE.md` for the architecture, code-quality principles, and the
phased design process (architecture -> OOD/LLD -> domain rules ->
implementation) that these milestones follow.

## Milestone 0 — Project & AI-artifact scaffolding ✅ COMPLETE

Create the repo structure, directories, stub files, and configuration.
Nothing runs yet.

**Pass criteria:** directory structure and stub module files match
CLAUDE.md's architecture; `pyproject.toml` is valid and configures
pytest and ruff; `ruff check` passes on the stub code; `pytest` can be
invoked without import/setup errors; required AI-collaboration
artefacts (`CLAUDE.md`, `.claude/`, `ai/`, `AI_REFLECTION.md`) exist.

## Milestone 1 — Domain & historical rules research

Research and document the 1974/75 English First Division rules:

- Points awarded per win/draw/loss
- Tiebreak criteria (full order, not just the first rule)
- Output column set and order
- Input CSV schema

**Pass criteria:** all domain rules documented with sources; no code
written yet.

## Milestone 2 — OOD/LLD design & domain layer implementation

Combines the low-level design step with building the pure calculation
core, using a spec-first-then-TDD approach: agree the shape explicitly
before writing tests or code (so nothing is inferred on the fly), then
implement test-by-test against that agreed shape.

Design to agree and document first:

- Domain object shapes (`Match`, `TeamStanding` — fields, types,
  immutability approach)
- Function signature for standings derivation/ranking
- Exception hierarchy and exit codes
- Verify consistency with CLAUDE.md's dependency direction

Then implement, test-first:

- `domain.py` with standings derivation and ranking logic
- Comprehensive unit tests in `test_domain.py`, against a small
  synthetic fixture (invented teams/matches) — not the real 1974/75
  dataset, which is sourced separately in Milestone 5
- `ruff check` passes
- Zero imports from I/O or CLI layers

**Pass criteria:** shape/signatures documented so someone else could
implement the same thing without guessing; all domain tests pass; no
I/O anywhere in `domain.py`.

## Milestone 3 — I/O layer implementation

Implement CSV reading and writing:

- `csv_reader.py` — parse CSV to `Match` objects, validate, raise
  exceptions on malformed rows
- `csv_writer.py` — write `TeamStanding` objects to CSV format
- Unit tests using in-memory streams (`io.StringIO`), not real files,
  against the same synthetic fixture as Milestone 2 — not the real
  1974/75 dataset
- Both operate on file-like objects only (no path-opening)

**Pass criteria:** reader/writer tests pass; `ruff check` passes.

## Milestone 4 — Application & CLI layer implementation

Wire everything together into a runnable tool:

- `app.py` — single orchestration function (reader -> domain -> writer)
- `cli.py` — argument parsing, stream opening/closing, error-to-exit-code
  mapping
- `test_app.py` and `test_cli.py` — test orchestration and CLI behavior,
  against the same synthetic fixture
- Tool runs end-to-end (file args and stdin/stdout modes)
- Malformed input produces non-zero exit code with sensible error
  message

**Pass criteria:** tool runs against synthetic input end-to-end; `ruff
check` passes everywhere.

## Milestone 5 — Real match-data sourcing & verification

Source and fully verify the actual assignment dataset, independent of
and after the software itself is built and tested:

- Create `data/week10_1974_75.csv`, sourced from historical records,
  covering all matches through the 10th round of the 1974/75 season
- Create `data/expected_standings.csv` reflecting verified historical
  standings at that point
- Cross-check both against multiple independent sources; document
  sources and any unresolved discrepancies

**Pass criteria:** both files exist, are complete, and are verified
against cited historical sources.

## Milestone 6 — Acceptance validation against real data

Prove correctness against the assignment target:

- `test_acceptance.py` — runs full pipeline against
  `data/week10_1974_75.csv`
- Output matches `data/expected_standings.csv`
- Any discrepancy investigated and documented

**Pass criteria:** acceptance test passes, or mismatch is understood
and documented.

## Milestone 7 — Submission polish

Finalize everything for submission:

- `README.md` complete with setup and run instructions
- `AI_REFLECTION.md` written (real AI disagreement/decision moment)
- `.claude/` and `ai/` folders populated with session data and
  conversation exports
- Full test suite passes from a clean clone
- `ruff check` passes on entire project
- Final read-through against PDF requirements

**Pass criteria:** reviewer can clone, follow README, get a working
tool with all mandatory AI artifacts present.
