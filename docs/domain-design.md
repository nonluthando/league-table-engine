# Domain Design (Milestone 2)

Records the OOD/LLD decisions agreed for the domain layer before any
implementation. This is the "spec" half of Milestone 2's spec-first-
then-TDD approach — `domain.py` should be implementable from this
document without guessing. Open questions are called out explicitly
rather than silently decided.

## `Match`

Immutable value object (frozen dataclass) representing one played
match. This is the sole raw input to the domain — nothing else is
derived from a more primitive source.

Fields:

- `home_team: str`
- `away_team: str`
- `home_goals: int`
- `away_goals: int`

Notes:

- No date, round number, or venue field — the domain has no use for
  them. Which matches are *included* (e.g. "through week 10") is
  decided outside the domain, before a `Match` is ever constructed.
- Win/draw/loss is not stored on `Match`; it is derived by comparing
  `home_goals` and `away_goals` wherever needed.

## `TeamStanding`

Immutable value object (frozen dataclass) representing one team's
aggregated record.

Stored fields (accumulated by folding over a team's matches):

- `team: str`
- `won: int`
- `drawn: int`
- `lost: int`
- `goals_for: int`
- `goals_against: int`

Derived properties (computed from the stored fields above, not
stored):

- `played` = `won + drawn + lost`
- `points` = `won * 2 + drawn * 1` (see Points System below)
- `goal_average` = `goals_for / max(goals_against, 1)` — dividing by
  1 instead of 0 when a team has conceded nothing, rather than
  raising `ZeroDivisionError` (see resolution below; this was
  originally left unresolved and was settled during implementation)

`won`/`drawn`/`lost`/`goals_for`/`goals_against` are stored (not
further derived from a raw match list) because they are already the
irreducible aggregate — the only simpler source is the full match
list itself, which would mean re-scanning every match on every access
(including repeatedly during sorting) and would couple `TeamStanding`
to raw match history it doesn't otherwise need.

## `compute_standings`

```
def compute_standings(matches: Iterable[Match]) -> list[TeamStanding]
```

Responsibility: the single domain entry point. Folds over the given
matches to build one `TeamStanding` per team, then returns them sorted
according to the tiebreak order below (descending).

## Domain exceptions

`compute_standings` raises `NoMatchesError` if given an empty sequence
of matches. This project's real input is always expected to be a
non-empty, already-played set of matches; an empty list is treated as
signaling a likely upstream problem (e.g. an empty or corrupt input
file) rather than a legitimate zero-match state, so it is raised
loudly rather than silently producing an empty table.

## Immutability decisions

Both `Match` and `TeamStanding` are immutable (frozen dataclasses).
Building standings from matches is a fold that produces new
`TeamStanding` values — there is no mutator method that updates a
`TeamStanding` in place with one more match's result.

## Dependency boundaries

`domain.py` has zero imports from `csv_reader.py`, `csv_writer.py`,
`app.py`, or `cli.py`, and performs no I/O. It depends only on the
standard library. This matches CLAUDE.md's locked dependency
direction (`cli -> app -> domain`, `app -> io -> domain`).

## Points system (sourced, Milestone 1)

2 points for a win, 1 point for a draw, 0 points for a loss (the
English rule in force for the 1974/75 season, until the 3-points rule
in 1981/82).

## Tiebreak ordering (sourced, Milestone 1)

Sort order for ranking, all descending:

1. `points`
2. `goal_average`
3. `goals_for`

Sourced from the Wikipedia 1974–75 Football League First Division
article's stated classification rule: "1) Points; 2) Goal average;
3) Goals scored."

No further criterion is applied beyond these three — this was
verified (searched specifically for a "head-to-head"/"matches between
the clubs concerned" rule in the pre-1976 Football League and found
none; the sourced rule is exactly these three, nothing more). If two
teams remain level after all three, no additional invented tiebreak is
applied; in practice this is extremely unlikely to occur at this level
of granularity.

Goal difference (`goals_for - goals_against`) is deliberately **not**
used for ranking and **not** added to the domain: it is not part of
the 1974/75 historical rules (goal difference only replaced goal
average from the 1976/77 season onward), and including it would
misrepresent how this season's table was actually ranked. A possible
future "modern rules" comparison view (3 points for a win, goal
difference instead of goal average) has been raised as an idea for
much later, but is explicitly out of scope now — the table stays
strictly historical.

## CSV schema (input, as agreed)

One row per already-played match, header row included, column names
and order matching `Match`'s field names and order exactly:

```
home_team,away_team,home_goals,away_goals
Derby County,Everton,0,0
Liverpool,Luton Town,2,1
```

Chosen for ease of machine processing (direct mapping onto `Match`'s
fields) rather than for human readability.

## Validation responsibility at the I/O boundary

Validation of raw input (malformed rows, non-numeric goals, etc.)
happens in `csv_reader.py`, not in the domain. `domain.py` currently
has no custom exception type: it trusts that any `Match` handed to it
is already valid, per CLAUDE.md's "only validate at system boundaries"
principle.

## Resolved during implementation

**`goal_average` when `goals_against` is 0.** Writing the first tests
against a clean-sheet scoreline (e.g. 2–0) surfaced that this is a
common case, not a rare edge case, and blocked implementing the sort
key. Resolved: `goal_average = goals_for / max(goals_against, 1)` —
divide by 1 instead of 0, no other special-casing. See `TeamStanding`
above.

## Unresolved / open questions

These are explicitly **not decided** — flagging them rather than
guessing:

1. **Exit codes.** Milestone 2's original scope mentions an exception
   hierarchy "and exit codes," but exit codes are a CLI-layer concern
   that can't really be fixed until the CLI milestone. Not addressed
   here.

## Deferred to file-specific design (not decided here, on purpose)

These aren't open gaps so much as decisions intentionally postponed
until the relevant file is actually being built — consistent with how
the input CSV schema above was agreed just before it was needed,
rather than everything being decided upfront in this document:

1. **Team name identity/matching.** Whether team names are assumed to
   match by exact string equality across rows, or need normalization
   (casing, whitespace). To be decided when `csv_reader.py` is
   designed.
2. **Output CSV column set and order.** Milestone 1 turned up a
   plausible period convention (Position, Club, Played, Won, Drawn,
   Lost, For, Against, Goal Average, Points), never independently
   verified against an actual historical source. To be decided when
   `csv_writer.py` is designed.
