# Data Sourcing (Milestone 5)

Documents how `data/week10_1974_75.csv` and `data/expected_standings.csv`
were compiled and verified, per CLAUDE.md's requirement to document
non-obvious assumptions and interpretations where they're decided.

## Scope interpretation: "the 10th week of the season"

CLAUDE.md's Purpose and Scope section left "the 10th week" ambiguous
between two readings: each team's 10th match played, or a fixed
calendar window from the season's start. This was resolved (2026-09-16,
user decision) as **calendar weeks**: the season started Saturday 17
August 1974; Week 10 runs 19–25 October 1974. The dataset therefore
includes every First Division league match played **on or before
Friday 25 October 1974**, regardless of how many matches each team has
played as a result. Under this reading, games-played is *not* equal
across teams — some clubs had more midweek fixtures than others in the
window (see "Games played per team" below) — which is expected, not an
error.

## Sources used

No single source publishes a ready-made "table after week 10" snapshot
for this season; the final table (e.g. RSSSF, `rsssf.org/engpaul/FLA/
1974-75.html`) only gives end-of-season aggregates. The match-by-match
dataset was reconstructed primarily from:

- Individual clubs' "1974–75 [Club] F.C. season" Wikipedia articles
  (dated, chronological results tables) — the primary source for the
  14 of 22 clubs that have one.
- For the 8 clubs without a dedicated Wikipedia season article
  (Ipswich Town, Sheffield United, Burnley, Wolverhampton Wanderers,
  Coventry City, Newcastle United, Tottenham Hotspur, Chelsea): fan-run
  historical archives — `clarets-mad.co.uk` and `uptheclarets.com`
  (Burnley), `bounder.friardale.co.uk` (Chelsea), `prideofanglia.com`
  (Ipswich), `nufc-history.co.uk` (Newcastle), `thfcdb.com` (Tottenham,
  manually checked by the user), `wolvescompletehistory.co.uk` (Wolves,
  lower confidence — search-snippet corroboration only, direct fetch
  failed), and search-surfaced `11v11.com` match-report pages and
  `svenskafans.com` round-by-round recaps (both block direct fetching;
  content obtained via search-result snippets only).
- Several sites that would have been useful cross-checks were
  unreachable entirely: `worldfootball.net`, `soccerway.com`,
  `footballsite.co.uk` (TLS errors), and the Wayback Machine (blocked
  by the fetch tool regardless of snapshot availability).

Two matches (Coventry City v Burnley, 31 Aug; Tottenham Hotspur v
Burnley, 5 Oct) had no verifiable score from any automated source and
were resolved by the user manually checking `uptheclarets.com` and
`thfcdb.com` directly.

## A genuine, unexpected fixture-scheduling pattern

Several club pairs play each other twice within the same week in late
August (e.g. 21 and 27/28 Aug): Derby County v Coventry City,
Manchester City v Tottenham Hotspur, Leeds United v Queens Park
Rangers, and Burnley v Chelsea. Initially suspected as a data-extraction
duplication artifact, this was independently confirmed (via
`svenskafans.com`, `11v11.com`, and direct Wikipedia inspection showing
both dates clearly under separate "First Division match details"
sections) to be a real fixture-list convention of that era: clubs were
scheduled for reciprocal home/away fixtures days apart early in the
season. Both matches in each pair are included as genuine, separate
results.

## Known unresolved discrepancies (documented, not blocking)

- **Newcastle United v Sheffield United** also shows the same
  twice-in-a-week pattern (21 Aug, 2–2; 27 Aug, 2–1). Included on the
  strength of the pattern established by the four confirmed pairs
  above, but — unlike those four — this pair was not independently
  re-confirmed against a second source. Lower confidence than the
  confirmed pairs.
- **Sheffield United v Derby County, 15 October**: sources disagree on
  venue (one source has Derby County at home 2–1, another has
  Sheffield United at home 1–2 Derby). Does not affect the standings
  table, since `compute_standings` aggregates by team regardless of
  home/away.
- **Birmingham City v Leicester City**: Birmingham's own Wikipedia
  page dates this 1–1 draw 28 August; Leicester's dates it 27 August.
  Same match (same attendance, 24,018, on both pages); neither cites a
  source. Does not affect the standings table — `Match` has no date
  field (see `docs/domain-design.md`), so the match counts in the
  table regardless of which day it happened.
- Most matches in the dataset are **single-sourced** (typically one
  Wikipedia editor's account, or one fan-archive page) rather than
  independently double-verified. True two-source verification was only
  done for the specific matches flagged as suspicious during this
  process. Full independent re-verification of all 144 matches was
  judged impractical given source availability (see "Sources used"
  above — several major cross-check sites were unreachable).

## Games played per team (as of the 25 Oct 1974 cutoff)

Ranges from 11 (Leicester City) to 15 (Luton Town), reflecting the
calendar-week scope interpretation above rather than a fixed
games-played count.

## `data/expected_standings.csv` derivation

Computed via a script deliberately independent of `domain.py` (a
separate, from-scratch aggregation over `data/week10_1974_75.csv`),
so that Milestone 6's acceptance test is a genuine check of the domain
logic rather than the code validating itself. Cross-checked against
the actual CLI's output on the same input and found identical.
