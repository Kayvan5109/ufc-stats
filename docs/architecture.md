# Architecture

This document gives the project map and defines the repo boundaries used by contributors and agents.

## Repository layout

```text
ufc-stats/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── task.yml
│   ├── workflows/
│   │   └── ci.yml
│   ├── CODEOWNERS
│   ├── labels.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── adr/
│   │   ├── 0000-template.md
│   │   └── 0001-agent-workflow.md
│   └── architecture.md
├── notebooks/
├── scripts/
│   └── collect_data.py
├── src/
│   └── ufc_stats/
│       ├── __init__.py
│       ├── config.py
│       └── ingest/
│           └── greco.py
├── .gitignore
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── PROJECT_DOCUMENT.md
├── README.md
├── pyproject.toml
└── .venv/  # local environment only; not tracked
```

## Module map

- `src/ufc_stats/config.py` stores project-level paths for the repo, raw data, processed data, scripts, and notebooks.
- `src/ufc_stats/ingest/greco.py` downloads pinned, checksummed snapshots of the source CSVs (see [ADR 0002](adr/0002-data-source.md)).
- `scripts/collect_data.py` is the command-line entry point for downloading a snapshot.
- `data/raw/` stores unmodified snapshots downloaded from public sources.
- `data/processed/` stores cleaned or derived datasets created after validation.
- `notebooks/` holds exploratory analysis and reporting notebooks.

## Data flow

1. Acquire raw source data from approved public site(s).
2. Save raw snapshots under `data/raw/` with source metadata.
3. Validate schema, duplicates, and missing values.
4. Transform rows into normalized records for fighters, fights, and events.
5. Write processed artifacts to `data/processed/`.
6. Run notebook or script-based analysis and reporting from the processed layer.

## Constraints

- Respect site terms, robots.txt, and legal usage boundaries.
- Prefer reproducible scripts over ad hoc notebook work.
- Keep raw and processed data separated.
- Avoid editing CI config, release scripts, or dependency declarations for unrelated work.
- Treat source data as traceable evidence; do not silently discard data quality problems.

## Ownership and review boundaries

- High-risk paths are named in [CODEOWNERS](../.github/CODEOWNERS).
- Repo-level process rules live in [AGENTS.md](../AGENTS.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).
- Uncertain or evolving implementation decisions should be documented in an ADR under `docs/adr/`.

> TODO(human): verify the exact final data source and pipeline architecture once source selection is locked in.
