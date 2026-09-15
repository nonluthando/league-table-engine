# AI Reflection

A running record of how AI assistance was used on this project, and the
non-obvious decisions made along the way. Required submission artefact
per `CLAUDE.md`.

## Milestone 0 — Project scaffolding

- Set up the layered package structure (`cli.py`, `app.py`, `domain.py`,
  `csv_reader.py`, `csv_writer.py`) with module-level docstrings stating
  each layer's responsibility and boundary, but no logic — architecture
  only, per the phased design process in `CLAUDE.md`.
- Configured `pytest` (via `pyproject.toml`, `testpaths = ["tests"]`).
- Configured `ruff` to check only for undefined names, unused
  imports/variables, disorganized imports, and functions that are too
  complex (mccabe), matching `CLAUDE.md`'s explicit instruction that
  ruff is not used for style opinions such as line length.
- No domain rules, CSV schema, output format, or OOD/LLD decisions were
  made at this stage — those are explicitly deferred to later phases.
