# UFC Stats Project

This repository is a research and analytics project focused on UFC fight and fighter data. The goal is to collect public data, analyze fight trends, and generate actionable insights about fighters, styles, strengths, weaknesses, and future matchup opportunities.

## Project goals

- Collect and normalize UFC fight and fighter data from public sources
- Build a reusable data pipeline for recurring refreshes
- Analyze patterns in style, performance, and matchup outcomes
- Derive fighter-level and fight-level insights
- Experiment with predictive baselines for future fights

## Repository structure

- `src/ufc_stats/` – Python package for project logic
- `scripts/` – data collection and ETL scripts
- `data/raw/` – raw downloaded source data
- `data/processed/` – cleaned and transformed datasets
- `notebooks/` – analysis and exploration notebooks
- `PROJECT_DOCUMENT.md` – project brief and workflow requirements
- `AGENTS.md` – canonical rules for AI contributors and reviewers
- `CONTRIBUTING.md` – human and agent contribution flow
- `docs/architecture.md` – repo map and data flow
- `docs/adr/` – architecture decisions and workflow adoption records

## Local environment

This project uses a local virtual environment at `.venv`.

### Create or activate the environment

PowerShell:

```powershell
cd C:\Users\khoob\Projects\ufc-stats
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
cd C:\Users\khoob\Projects\ufc-stats
.venv\Scripts\activate.bat
```

### Verified project commands

```powershell
# install the repo in editable mode
.\.venv\Scripts\python.exe -m pip install -e .

# syntax validation
.\.venv\Scripts\python.exe -m compileall src

# test suite
.\.venv\Scripts\python.exe -m pytest
```

## Getting the data

Raw data comes from the [Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats) CSV mirror of UFCStats.com (see [ADR 0002](docs/adr/0002-data-source.md)). To download the latest snapshot:

```powershell
.\.venv\Scripts\python.exe scripts\collect_data.py
```

This saves the six source CSVs and a `manifest.json` under `data/raw/greco1899/<commit-date>_<sha7>/`:

- Each snapshot is pinned to one upstream commit. Re-running when nothing upstream has changed does nothing.
- If any file's columns differ from what the code expects, the download fails and saves nothing.

## Project workflow

1. Use public fight data sources only unless a legal paid source is later approved.
2. Store raw files under `data/raw/`.
3. Keep cleaned data under `data/processed/`.
4. Document assumptions and data provenance.
5. Prefer reproducible scripts over ad hoc notebook changes.
6. Validate data before building features or models.
7. Follow the agent and PR conventions in [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## First milestone

The first milestone should produce:

- a working ingestion script,
- a cleaned historical UFC dataset,
- a fighter profile summary,
- a simple exploratory notebook,
- and a baseline predictive experiment.

## Notes

This project is intentionally research-first and should prioritize data quality and interpretability before building overly complex models.
