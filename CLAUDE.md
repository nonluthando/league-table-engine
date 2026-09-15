# CLAUDE.md

Project instructions for AI assistants working on this repository.

## Purpose and Scope

This project is a command-line application that calculates a football
(soccer) league standings table from match results, built for the SPAN
Digital coding assessment. It reads match data from a CSV file (or stdin),
computes standings according to the rules of the competition in question,
and writes a standings table to a CSV file (or stdout).

The immediate goal is to calculate the English First Division standings
at the 10th week of the 1974/75 season, but the calculation logic itself
should not assume that specific dataset beyond what the rules research
(tracked separately) determines.

This is a small, single-purpose tool. It is not a platform, a service,
or a framework. Scope should stay deliberately narrow: read matches,
compute standings, write a table. Resist adding features, configuration,
or abstraction that the assignment does not ask for.

## Architecture

The application follows a lightweight layered architecture with four
responsibilities, each owned by a single module:

- **CLI layer** (`cli.py`) — argument parsing, opening/closing input and
  output streams, invoking the application layer, and mapping errors to
  exit codes. No calculation or CSV-parsing logic lives here.
- **Application layer** (`app.py`) — a single orchestration entry point
  that composes reading, computing, and writing. No argument parsing or
  process-exit logic lives here; it operates on already-open streams.
- **Domain layer** (`domain.py`) — the core value objects representing
  matches and team standings, plus the pure logic that derives standings
  from matches and ranks them. This layer has no knowledge of CSV, files,
  or the CLI, and performs no I/O.
- **CSV I/O layer** (`csv_reader.py`, `csv_writer.py`) — conversion
  between CSV text and domain objects. Reading and writing are separate
  modules. I/O operates on file-like (text stream) objects rather than
  file paths, so the same code handles files and stdin/stdout uniformly.

This document fixes the *layers and the boundaries between them*. It
deliberately does not fix the internal shape of any layer — see
"Object-Oriented / Low-Level Design (Separate Phase)" below.

### Dependency direction

Dependencies point inward, toward the domain, and never the reverse:

```
cli → app → domain
       app → io → domain
```

- `domain.py` depends on nothing else in this project.
- `csv_reader.py` and `csv_writer.py` depend only on `domain.py`.
- `app.py` depends on `domain.py` and the I/O modules, and is the only
  module that wires them together.
- `cli.py` depends only on `app.py` (plus the standard library for
  argument parsing and process exit).

If a change requires the domain layer to import from `cli.py` or the I/O
modules, that is a signal the design has drifted — stop and reconsider
rather than adding the import.

## Code-Quality Principles

- **Readability first.** Code should be easy to follow without needing
  this file open. Prefer clarity over cleverness.
- **High cohesion, low coupling.** Each module should have one clear
  responsibility (as defined above) and should not reach into another
  layer's concerns.
- **Appropriate abstraction, not speculative generality.** Build for the
  requirements in front of us. Do not introduce interfaces, strategy
  patterns, plugin points, or configuration options for hypothetical
  future needs (other leagues, other seasons, other rule sets) unless
  and until they're actually required.
- **Testability.** Design so that domain logic can be tested without
  files, streams, or the CLI, and so that I/O logic can be tested with
  in-memory text rather than real files.
- **Clear naming.** Names should reflect domain vocabulary (match, team,
  standing, points, rank) rather than generic or technical terms.
- **Immutability where practical.** Domain data should generally not be
  mutated in place once created; prefer deriving new values over
  modifying existing ones. The specific mechanism for this is an LLD
  decision (see below), not fixed here.
- **Type hints.** Use type hints on function signatures and public data
  structures — they document intent and catch category errors during
  code review. They are not enforced by a linter; the test suite is the
  primary safety net.
- **Explicit error handling.** Failure modes (malformed input rows,
  unreadable files, invalid arguments) should be handled deliberately
  with clear exception types and defined exit-code behavior, not left to
  propagate as unhandled stack traces or silently swallowed. The specific
  exception hierarchy is an LLD decision.
- **Avoid over-engineering.** No database, web framework, microservices,
  MVC, Docker, dependency-injection framework, or design pattern that
  isn't earning its place. If in doubt, prefer the simpler option and
  say why in a comment or commit message.

## Testing Expectations

Automated tests are mandatory and must be included in the submission.

- **Domain tests** are the primary test suite: pure unit tests against
  `domain.py` with no I/O, covering standings derivation and ranking
  logic, including edge cases.
- **I/O tests** exercise `csv_reader.py` and `csv_writer.py` against
  in-memory text streams, not real files, including malformed-input
  handling.
- **Application tests** exercise `app.py`'s orchestration directly,
  independent of argument parsing.
- **CLI tests** cover argument parsing and exit-code behavior.
- **Acceptance test** runs the full pipeline end-to-end against the
  real data fixtures in `data/` and checks the output against a
  verified expected result.

Tests should be fast, deterministic, and runnable without network
access or external services. These are boundaries the tests should
respect; the specific test cases and fixtures are worked out per-module
as each layer's LLD is defined.

## Development Workflow and Documentation

- Keep commits small and focused; commit messages should explain *why*
  a change was made when it isn't obvious from the diff.
- Update `README.md` as setup/run instructions change — it must remain
  accurate enough for someone to clone the repo and run the tool with
  no other context.
- Document non-obvious assumptions (e.g. interpretations of ambiguous
  requirements) where the decision is made — in code comments, README,
  or `AI_REFLECTION.md` as appropriate — rather than leaving them
  implicit.
- **Automated tooling checks:** The test/CI step must include:
  - `ruff check` to catch practical code-quality issues: undefined names,
    unused imports/variables, disorganized imports, and functions that
    are genuinely too complex to reason about. Ruff is not used for
    style opinions (line length, blank lines, naming conventions) — only
    for issues that actually signal a problem.
  Ruff must pass before code is considered ready for review.
- Do not commit installed packages or virtual environment contents.
- Required AI-collaboration artifacts (`CLAUDE.md`, `.claude/`, `ai/`,
  `AI_REFLECTION.md`) must be kept up to date and included in the
  submission; they are not optional.

## Constraints from the Assignment

These constraints come directly from the assessment brief and should
guide all implementation decisions:

- Solution language must be one of: Java, Python, Golang, C# (.NET Core
  on Linux), or Scala. This project uses Python.
- Input and output should be text CSV files, supplied either via
  stdin/stdout or via filenames on the command line.
- The actual input file(s) used and the resulting output must be
  included in the submission (under `data/`).
- Automated tests must be included in the submission.
- If third-party libraries are used via a package manager, the
  installed packages themselves must not be committed — only the
  dependency declaration (e.g. `pyproject.toml`).
- Any non-trivial setup steps required to run the solution must be
  documented in `README.md`.
- The target environment is Unix-like (macOS); implementation should
  use platform-agnostic constructs where possible.
- The solution should be "production-ready" in spirit: appropriately
  tested, with explicit error handling, and without unnecessary
  scope or complexity for what the assignment actually asks for.

## Design Process: Architecture vs. OOD/LLD vs. Domain Rules

This project's design is worked through in distinct phases, and this
file only governs the first:

1. **Architecture (this document — locked).** Layers, module
   boundaries, dependency direction, engineering principles, testing
   boundaries, tooling. Changing this requires deliberate discussion,
   not incidental drift during implementation.
2. **Object-Oriented / Low-Level Design (separate phase, not yet
   done).** Within the architecture fixed above, this covers: the exact
   fields and shape of domain objects (e.g. how a match or a team
   standing is represented), whether/where to use constructs like
   dataclasses, enums, or other structures, function and method
   signatures at each layer boundary, the exception type hierarchy, and
   any other implementation-level design choices. This is worked out
   and agreed *before* writing the corresponding code, but it is not
   part of this file — it does not need to be re-litigated if it
   changes, since it doesn't affect the architecture.
3. **Domain / historical rules research (separate phase, not yet
   done).** Points-per-win, the ranking/tiebreak criteria, the CSV
   schemas, and the output column format. See "Explicitly Out of Scope"
   below.

An AI assistant working on this project should treat a request to "start
implementing" as a signal to check whether phases 2 and 3 have actually
been agreed for the part in question — not to infer reasonable-sounding
defaults on the fly.

## Explicitly Out of Scope (For Now)

The following are intentionally not yet decided and should not be
assumed or hard-coded until addressed as a separate step:

- Points awarded per win/draw/loss.
- The tiebreak criteria used for ranking (e.g. goal average vs. goal
  difference) and any further tiebreak order.
- The exact output column set and format ("conventional format" is
  specified by the assignment but not defined).
- The exact input CSV schema (column names and order).
- All OOD/LLD decisions described in "Design Process" above (exact
  domain object shape, function signatures, use of dataclasses/enums,
  exception hierarchy, etc.).

Do not hard-code assumptions about any of the above while working on
architecture, scaffolding, or non-domain-rule code.
