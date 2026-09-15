# CSV I/O Design (Milestone 3)

Records the agreed shape for `csv_reader.py` and `csv_writer.py`
before any implementation, following the same spec-first-then-TDD
approach used for the domain layer (`docs/domain-design.md`). Both
files operate on file-like (text stream) objects, never file paths,
per CLAUDE.md, and depend only on `domain.py` — never on `app.py` or
`cli.py`.

## Input CSV schema (already agreed, `docs/domain-design.md`)

```
home_team,away_team,home_goals,away_goals
Derby County,Everton,0,0
```

Header row, snake_case, column order matching `Match`'s field order
exactly. Restated here for context; the authoritative record is
`docs/domain-design.md`.

## `csv_reader.py`

Responsibility: parse CSV rows into `Match` objects, validating
structure and team names, and raising a specific exception on
failure. This is where all input validation happens — `domain.py`
trusts any `Match` it receives.

### Team name normalization

For each of `home_team`/`away_team`:

1. Strip leading/trailing whitespace.
2. Casefold (case-insensitive comparison).
3. Look up the result against the alias table below. If it matches a
   canonical name or a listed alias, use the canonical name. If it
   matches nothing, raise `UnknownTeamError`.

This is deliberately **not** substring/fuzzy matching — only exact
matches (post-normalization) against an explicit, curated list. A
fragment like "Manchester" is not treated as an alias for anything,
even though only one Manchester club happens to be in this season's
list — accepting it would rely on that coincidence rather than a
genuine, independently-recognized shorthand, and wouldn't generalize
safely.

### Alias table

Scoped only to the 22 clubs actually in the 1974/75 First Division —
this is not a general team-name-resolution system for other
leagues/seasons, which would be speculative generality beyond what
this project needs.

| Canonical name | Known aliases |
|---|---|
| Manchester City | Man City |
| Wolverhampton Wanderers | Wolves |
| Tottenham Hotspur | Spurs |
| Queens Park Rangers | QPR |
| Middlesbrough | Boro |
| Sheffield United | Sheff Utd |
| West Ham United | West Ham |
| Derby County | *(full name only)* |
| Liverpool | *(full name only)* |
| Ipswich Town | *(full name only)* |
| Everton | *(full name only)* |
| Stoke City | *(full name only)* |
| Leeds United | *(full name only)* |
| Burnley | *(full name only)* |
| Coventry City | *(full name only)* |
| Newcastle United | *(full name only)* |
| Arsenal | *(full name only)* |
| Birmingham City | *(full name only)* |
| Leicester City | *(full name only)* |
| Luton Town | *(full name only)* |
| Chelsea | *(full name only)* |
| Carlisle United | *(full name only)* |

The seven aliases above are the ones independently confirmed as
genuine, long-standing shorthand (Wikipedia-sourced for Man City,
Wolves, Spurs, QPR; well-established football-knowledge for Boro,
Sheff Utd, West Ham). A broader web search attempting to find
abbreviations for the remaining 15 clubs produced unreliable,
apparently partly-fabricated results (it included "Wrexham," a club
not even in this dataset) and was discarded rather than used. Those
15 clubs are full-name-only until/unless a genuinely verified alias
turns up.

### Exceptions

- **`UnknownTeamError`** — raised when a team name (after
  normalization) matches nothing in the canonical/alias list.
  Message format: identifies the offending raw value and row number,
  e.g.:

  ```
  UnknownTeamError: "Man Untied" (row 7) is not a recognized First
  Division club or known alias — check for a typo.
  ```

- **`MalformedRowError`** — raised for structural problems (wrong
  column count, non-integer goals). Also row-specific, e.g.:

  ```
  MalformedRowError: row 12 has 3 columns, expected 4.
  ```

Both exceptions share a common base class, `CsvReadError`, so callers
in `app.py`/`cli.py` can catch "any CSV read problem" (e.g. to map it
to one exit code) without enumerating each concrete type — the same
pattern as `json.JSONDecodeError` inheriting from `ValueError`.
`UnknownTeamError` and `MalformedRowError` both inherit from
`CsvReadError`.

### Blank lines

Blank lines are skipped when reading, not treated as malformed rows.

## `csv_writer.py`

Responsibility: write a `list[TeamStanding]` (already sorted by
`compute_standings`) to CSV in the agreed output format.

### Output CSV schema

Header row, full words, explicit position column, one row per team in
the order given (writer does not re-sort):

```
Position,Team,Played,Won,Drawn,Lost,For,Against,Goal Average,Points
1,Derby County,10,8,1,1,25,10,2.50,17
```

`Goal Average` is formatted to 2 decimal places.

## Unresolved / open questions

1. **Encoding.** Not discussed — assumed to be a minor implementation
   detail (e.g. UTF-8) rather than a design decision needing sign-off.
