# Data dictionary

This page defines the columns of the typed tables produced by `ufc_stats.parse.greco` from the raw source files ([ADR 0002](adr/0002-data-source.md)).

## General rules

- **Missing values.** Empty strings, `--` and `---` become null. All text is stripped of surrounding whitespace.
- **Integers allow nulls.** Integer columns use pandas `Int64`, which can hold nulls, so a missing value never turns into `0`.
- **Bad values fail loudly.** If a value is present but not in the expected format, the parser raises `ParseError` and names the column. It never quietly becomes null.
- **IDs come from UFCStats URLs.** `event_id`, `fight_id` and `fighter_id` are the 16-character hex code at the end of each UFCStats URL.
- **Nothing is dropped.** Parsing removes no rows and merges no duplicates. Known source problems are handled by the quality checks (issue #8).

## events (`ufc_event_details.csv`)

| Column | Type | Notes |
|---|---|---|
| `event_id` | string | From `URL` |
| `event_name` | string | |
| `event_date` | datetime | Source format `October 17, 2026` |
| `location` | string | `City, Region, Country` as given |
| `country` | string | Last comma-separated part of `location` |
| `event_url` | string | UFCStats event page |

## fights (`ufc_fight_results.csv`)

| Column | Type | Notes |
|---|---|---|
| `fight_id` | string | From `URL` |
| `event_name` | string | Joins to `events.event_name`. The source has no event ID here. |
| `bout` | string | `Fighter A vs. Fighter B` |
| `fighter_a`, `fighter_b` | string | Split from `bout`. These are names, not IDs. |
| `outcome_a`, `outcome_b` | string | `W`, `L`, `D` (draw), or `NC` (no contest) |
| `winner` | string | Name of the fighter with `W`; null for draws and no contests |
| `weight_class` | string | Raw label, e.g. `UFC Interim Lightweight Title Bout` |
| `division` | string | Weight class only, e.g. `Lightweight`. Null when the label names none (early tournaments, Superfights). |
| `is_title_bout` | boolean | `weight_class` contains "Title" or "Championship" |
| `method` | string | e.g. `KO/TKO`, `Submission`, `Decision - Unanimous` |
| `details` | string | How the fight ended (e.g. `Rear Naked Choke`), or the judges' scores for decisions |
| `end_round` | Int64 | Round the fight ended in |
| `end_time_seconds` | Int64 | Clock time within `end_round` |
| `time_format` | string | Raw, e.g. `3 Rnd (5-5-5)` or `1 Rnd + OT (12-3)` |
| `scheduled_rounds` | Int64 | Number of periods in `time_format`, overtime included. Null for `No Time Limit`. |
| `fight_duration_seconds` | Int64 | Full minutes of the rounds before `end_round`, plus `end_time_seconds`. For `No Time Limit` fights, only known if the fight ended in round 1. |
| `referee` | string | |
| `fight_url` | string | UFCStats fight page |

## fight_stats (`ufc_fight_stats.csv`)

There is one row per fighter per round.

| Column | Type | Notes |
|---|---|---|
| `event_name`, `bout` | string | Join to `fights` on these two columns. The source has no fight ID here. |
| `round` | Int64 | From `Round N` |
| `fighter` | string | Name, not an ID |
| `kd` | Int64 | Knockdowns |
| `sig_str_landed`, `sig_str_attempted` | Int64 | Significant strikes |
| `total_str_landed`, `total_str_attempted` | Int64 | All strikes |
| `td_landed`, `td_attempted` | Int64 | Takedowns |
| `head_*`, `body_*`, `leg_*` | Int64 | Significant strikes by where they landed |
| `distance_*`, `clinch_*`, `ground_*` | Int64 | Significant strikes by position |
| `sub_att` | Int64 | Submission attempts |
| `rev` | Int64 | Reversals |
| `ctrl_seconds` | Int64 | Control time. Null (`--`) for many early events. |

The source columns `SIG.STR. %` and `TD %` are left out on purpose: each is just landed ÷ attempted, which can be recalculated from the columns above.

## fighter_details (`ufc_fighter_details.csv`)

| Column | Type | Notes |
|---|---|---|
| `fighter_id` | string | From `URL` |
| `first_name`, `last_name`, `nickname` | string | |
| `fighter_url` | string | UFCStats fighter page |

## fighter_tott (`ufc_fighter_tott.csv`)

"Tott" is "tale of the tape": the fighter's physical measurements.

| Column | Type | Notes |
|---|---|---|
| `fighter_id` | string | From `URL` |
| `fighter` | string | Full name as shown on the page |
| `height_in` | Int64 | From `5' 11"` |
| `weight_lbs` | Int64 | Last listed weight, from `155 lbs.` |
| `reach_in` | Int64 | From `72"` |
| `stance` | string | `Orthodox`, `Southpaw`, `Switch`, `Open Stance` or `Sideways` |
| `dob` | datetime | Source format `Jul 03, 1983` |

## Known gaps

- **No IDs in the stats or fight files.** `fights` and `fight_stats` refer to fighters only by name, and some names belong to more than one fighter. Matching names to `fighter_id` happens in the build step (issue #9), which reports names it can't match instead of guessing.
- **Not in the source at all:** fighter nationality, team or camp, event venue, and a fight's position on the card.
