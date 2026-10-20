# 0002: Use the Greco1899 UFCStats CSV mirror as the primary data source

- Status: Accepted (owner decision, 2026-10-19)

## Context

[PROJECT_DOCUMENT.md](../../PROJECT_DOCUMENT.md) §16 left the primary source of truth open. The project needs fighter, event, fight, and round-by-round fight statistics from a public, $0 source that we can use without breaking site terms.

UFCStats.com (the official UFC statistics site) is the standard source for this data. It has no `robots.txt`, but as of 2026-10-19 every page, including `/statistics/events/completed`, returns a JavaScript proof-of-work "Checking your browser…" challenge to non-browser clients. Scraping it from a script would mean solving or bypassing that challenge. That is an access control the site added on purpose, so we will not circumvent it.

[Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats) is a public GitHub repository that scrapes UFCStats and publishes the results as CSV files. A scheduled job refreshes the files (commits show weekly refreshes; the latest checked is commit `3e2f3db` from 2026-10-18, which includes the 2026-10-17 event). It publishes:

| File | Contents |
|---|---|
| `ufc_event_details.csv` | `EVENT, URL, DATE, LOCATION` |
| `ufc_fight_details.csv` | `EVENT, BOUT, URL` |
| `ufc_fight_results.csv` | `EVENT, BOUT, OUTCOME, WEIGHTCLASS, METHOD, ROUND, TIME, TIME FORMAT, REFEREE, DETAILS, URL` |
| `ufc_fight_stats.csv` | per round, per fighter: `KD, SIG.STR., SIG.STR. %, TOTAL STR., TD, TD %, SUB.ATT, REV., CTRL, HEAD, BODY, LEG, DISTANCE, CLINCH, GROUND` |
| `ufc_fighter_details.csv` | `FIRST, LAST, NICKNAME, URL` |
| `ufc_fighter_tott.csv` | `FIGHTER, HEIGHT, WEIGHT, REACH, STANCE, DOB, URL` |

Every row carries the original UFCStats URL, so each record can be traced back to its source page.

### Alternatives considered

- **Scrape UFCStats directly with plain HTTP.** Rejected: blocked by the bot challenge, and bypassing it conflicts with the project's terms-of-use principle.
- **Scrape UFCStats by driving a real browser (e.g. Playwright).** Not chosen for now. It is slow and fragile, and it still works around a control meant to deter automated access. Revisit only by a new ADR if the mirror stops updating.
- **Kaggle UFC datasets.** Often stale, need an account and API key, and usually ship pre-aggregated features instead of per-round stats.
- **Tapology, Sherdog, FightMatrix.** Useful later for metadata that UFCStats lacks (camp, nationality, rankings), but they have weaker per-fight statistics and their own scraping restrictions.

## Decision

- Greco1899/scrape_ufc_stats is the primary raw data source for Milestone 1.
- **Pin every snapshot to a source commit.** Download files from `raw.githubusercontent.com/Greco1899/scrape_ufc_stats/<commit-sha>/<file>`, never from a moving branch name.
- **Snapshot layout:** `data/raw/greco1899/<commit-date>_<sha7>/` contains the six CSVs exactly as downloaded, plus a `manifest.json` that records:
  - the source repo, full commit SHA, commit date, and retrieval timestamp
  - each file's URL, byte size, and sha256
- **Raw snapshots are immutable.** We never edit a snapshot in place. Cleaning happens downstream and writes to `data/processed/`.
- **Check the schema on download.** Each file's header row is compared with the columns listed above, and any mismatch stops the download. If the upstream format changes, we update the expected columns in a reviewed PR.
- Raw data stays out of git (`data/raw/` is gitignored). We use the files locally for research and do not redistribute them.

## Consequences

- **We can start immediately** with full history and per-round stats, without writing or maintaining a scraper.
- **We depend on one maintainer.** If the mirror stops updating, existing snapshots stay usable but new events stop arriving. Mitigation: keep every downloaded snapshot, and keep the browser-based option above as a documented fallback.
- **The data is second-hand.** The mirror's scraper can introduce errors that UFCStats doesn't have. Mitigation: validation checks in the processing stage, plus spot-checking a sample against the UFCStats URLs on each row.
- **Licensing.** The repository is GPL-3.0, which covers its code. The CSVs are factual statistics scraped from UFCStats. Using them locally for research is low-risk. Publishing derived datasets later would need its own review.
- **Cleaning work is required.** Values like `9 of 37`, `---` and `--` for missing values, trailing spaces in event names, and string dates must be parsed and normalized. This is tracked in separate parser and validation issues.
- **The data is incomplete for some PROJECT_DOCUMENT.md §5 fields.** It has no fighter nationality, team/camp, or event venue (only location), and no card position. These may need a secondary source later.
