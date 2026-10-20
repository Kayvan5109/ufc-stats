"""Parse raw Greco1899 CSVs into typed tables.

Each ``parse_*`` function takes the raw file as a DataFrame of strings (see
``read_raw``) and returns a new DataFrame with typed columns. Rows are never
dropped or deduplicated here; that belongs to the quality checks. A value that
is present but in an unexpected format raises ``ParseError`` instead of
silently becoming null. Column definitions live in docs/data-dictionary.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

MISSING_MARKERS = {"", "--", "---"}

# Raw "X of Y" stat columns and the output prefix for each.
LANDED_ATTEMPTED_COLUMNS = {
    "SIG.STR.": "sig_str",
    "TOTAL STR.": "total_str",
    "TD": "td",
    "HEAD": "head",
    "BODY": "body",
    "LEG": "leg",
    "DISTANCE": "distance",
    "CLINCH": "clinch",
    "GROUND": "ground",
}

# Longest names first so "Light Heavyweight" wins over "Heavyweight", etc.
DIVISIONS = [
    "Women's Strawweight",
    "Women's Flyweight",
    "Women's Bantamweight",
    "Women's Featherweight",
    "Light Heavyweight",
    "Super Heavyweight",
    "Heavyweight",
    "Middleweight",
    "Welterweight",
    "Lightweight",
    "Featherweight",
    "Bantamweight",
    "Flyweight",
    "Open Weight",
    "Catch Weight",
]

OUTCOME_CODES = {"W", "L", "D", "NC"}

TIME_FORMAT_PATTERN = re.compile(r"^\d+ Rnd(?: \+ \d*OT)? \((\d+(?:-\d+)*)\)$")


class ParseError(ValueError):
    """A non-missing raw value did not match the expected format."""


def read_raw(path: Path) -> pd.DataFrame:
    """Read a raw CSV with every value as a string and no NA inference."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


# --- value parsers --------------------------------------------------------


def _clean(series: pd.Series) -> pd.Series:
    """Strip whitespace and turn missing markers into NA."""
    stripped = series.astype("string").str.strip()
    return stripped.mask(stripped.isin(MISSING_MARKERS))


def _check_parsed(raw: pd.Series, parsed: pd.Series, column: str) -> None:
    failed = raw.notna() & parsed.isna()
    if failed.any():
        examples = raw[failed].unique()[:5].tolist()
        raise ParseError(f"{column}: {int(failed.sum())} unparseable values, e.g. {examples}")


def _extract_int(series: pd.Series, pattern: str, column: str) -> pd.Series:
    raw = _clean(series)
    parsed = raw.str.extract(f"^{pattern}$", expand=False)
    _check_parsed(raw, parsed, column)
    return pd.to_numeric(parsed).astype("Int64")


def parse_count(series: pd.Series, column: str) -> pd.Series:
    """'1.0' or '1' -> 1."""
    return _extract_int(series, r"(\d+)(?:\.0)?", column)


def parse_landed_attempted(series: pd.Series, column: str) -> tuple[pd.Series, pd.Series]:
    """'9 of 37' -> (9, 37)."""
    raw = _clean(series)
    parts = raw.str.extract(r"^(\d+) of (\d+)$")
    _check_parsed(raw, parts[0], column)
    return pd.to_numeric(parts[0]).astype("Int64"), pd.to_numeric(parts[1]).astype("Int64")


def parse_mmss(series: pd.Series, column: str) -> pd.Series:
    """'4:21' -> 261 seconds."""
    raw = _clean(series)
    parts = raw.str.extract(r"^(\d+):([0-5]\d)$")
    _check_parsed(raw, parts[0], column)
    return (pd.to_numeric(parts[0]) * 60 + pd.to_numeric(parts[1])).astype("Int64")


def parse_height_inches(series: pd.Series, column: str) -> pd.Series:
    """'5\\' 11"' -> 71."""
    raw = _clean(series)
    parts = raw.str.extract(r"""^(\d+)' (\d+)"$""")
    _check_parsed(raw, parts[0], column)
    return (pd.to_numeric(parts[0]) * 12 + pd.to_numeric(parts[1])).astype("Int64")


def parse_date(series: pd.Series, fmt: str, column: str) -> pd.Series:
    raw = _clean(series)
    parsed = pd.to_datetime(raw, format=fmt, errors="coerce")
    _check_parsed(raw, parsed, column)
    return parsed


def url_id(series: pd.Series, kind: str, column: str) -> pd.Series:
    """'http://ufcstats.com/fight-details/c20c949ceba035f3' -> 'c20c949ceba035f3'."""
    raw = _clean(series)
    parsed = raw.str.extract(rf"^https?://(?:www\.)?ufcstats\.com/{kind}-details/([0-9a-f]+)$", expand=False)
    _check_parsed(raw, parsed, column)
    return parsed


def parse_division(series: pd.Series) -> pd.Series:
    """'UFC Interim Light Heavyweight Title Bout' -> 'Light Heavyweight'; NA if no division is named."""
    pattern = "(" + "|".join(re.escape(name) for name in DIVISIONS) + ")"
    return _clean(series).str.extract(pattern, expand=False)


def parse_round_lengths(series: pd.Series) -> pd.Series:
    """'3 Rnd (5-5-5)' -> [5, 5, 5] (minutes); 'No Time Limit' and missing -> None."""

    def one(value: object) -> list[int] | None:
        if pd.isna(value) or value == "No Time Limit":
            return None
        match = TIME_FORMAT_PATTERN.match(value)
        if not match:
            raise ParseError(f"TIME FORMAT: unparseable value {value!r}")
        return [int(minutes) for minutes in match.group(1).split("-")]

    return _clean(series).map(one, na_action=None)


# --- table parsers --------------------------------------------------------


def parse_events(raw: pd.DataFrame) -> pd.DataFrame:
    location = _clean(raw["LOCATION"])
    return pd.DataFrame(
        {
            "event_id": url_id(raw["URL"], "event", "URL"),
            "event_name": _clean(raw["EVENT"]),
            "event_date": parse_date(raw["DATE"], "%B %d, %Y", "DATE"),
            "location": location,
            "country": location.str.rsplit(",", n=1).str[-1].str.strip(),
            "event_url": _clean(raw["URL"]),
        }
    )


def parse_fight_results(raw: pd.DataFrame) -> pd.DataFrame:
    bout = _clean(raw["BOUT"])
    fighters = bout.str.split(" vs. ", n=1, expand=True)
    _check_parsed(bout, fighters[1], "BOUT")

    outcome = _clean(raw["OUTCOME"])
    outcomes = outcome.str.split("/", n=1, expand=True)
    valid_outcome = outcomes[0].isin(OUTCOME_CODES) & outcomes[1].isin(OUTCOME_CODES)
    _check_parsed(outcome, outcomes[0].where(valid_outcome), "OUTCOME")

    winner = pd.Series(pd.NA, index=raw.index, dtype="string")
    winner = winner.mask(outcomes[0] == "W", fighters[0]).mask(outcomes[1] == "W", fighters[1])

    end_round = parse_count(raw["ROUND"], "ROUND")
    end_time_seconds = parse_mmss(raw["TIME"], "TIME")
    round_lengths = parse_round_lengths(raw["TIME FORMAT"])

    def duration(lengths: list[int] | None, rnd: object, seconds: object) -> object:
        if pd.isna(rnd) or pd.isna(seconds):
            return pd.NA
        if lengths is None:
            return seconds if rnd == 1 else pd.NA
        return sum(lengths[: int(rnd) - 1]) * 60 + seconds

    weight_class = _clean(raw["WEIGHTCLASS"])

    return pd.DataFrame(
        {
            "fight_id": url_id(raw["URL"], "fight", "URL"),
            "event_name": _clean(raw["EVENT"]),
            "bout": bout,
            "fighter_a": fighters[0].str.strip(),
            "fighter_b": fighters[1].str.strip(),
            "outcome_a": outcomes[0],
            "outcome_b": outcomes[1],
            "winner": winner,
            "weight_class": weight_class,
            "division": parse_division(raw["WEIGHTCLASS"]),
            "is_title_bout": weight_class.str.contains("Title|Championship", regex=True).astype("boolean"),
            "method": _clean(raw["METHOD"]),
            "details": _clean(raw["DETAILS"]),
            "end_round": end_round,
            "end_time_seconds": end_time_seconds,
            "time_format": _clean(raw["TIME FORMAT"]),
            "scheduled_rounds": round_lengths.map(lambda x: len(x) if x is not None else pd.NA).astype("Int64"),
            "fight_duration_seconds": pd.Series(
                [duration(*args) for args in zip(round_lengths, end_round, end_time_seconds)],
                index=raw.index,
                dtype="Int64",
            ),
            "referee": _clean(raw["REFEREE"]),
            "fight_url": _clean(raw["URL"]),
        }
    )


def parse_fight_stats(raw: pd.DataFrame) -> pd.DataFrame:
    columns: dict[str, pd.Series] = {
        "event_name": _clean(raw["EVENT"]),
        "bout": _clean(raw["BOUT"]),
        "round": _extract_int(raw["ROUND"], r"Round (\d+)", "ROUND"),
        "fighter": _clean(raw["FIGHTER"]),
        "kd": parse_count(raw["KD"], "KD"),
    }
    for source, prefix in LANDED_ATTEMPTED_COLUMNS.items():
        landed, attempted = parse_landed_attempted(raw[source], source)
        columns[f"{prefix}_landed"] = landed
        columns[f"{prefix}_attempted"] = attempted
    columns["sub_att"] = parse_count(raw["SUB.ATT"], "SUB.ATT")
    columns["rev"] = parse_count(raw["REV."], "REV.")
    columns["ctrl_seconds"] = parse_mmss(raw["CTRL"], "CTRL")
    # SIG.STR. % and TD % are dropped: they are landed / attempted, recomputable above.
    return pd.DataFrame(columns)


def parse_fighter_details(raw: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fighter_id": url_id(raw["URL"], "fighter", "URL"),
            "first_name": _clean(raw["FIRST"]),
            "last_name": _clean(raw["LAST"]),
            "nickname": _clean(raw["NICKNAME"]),
            "fighter_url": _clean(raw["URL"]),
        }
    )


def parse_fighter_tott(raw: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fighter_id": url_id(raw["URL"], "fighter", "URL"),
            "fighter": _clean(raw["FIGHTER"]),
            "height_in": parse_height_inches(raw["HEIGHT"], "HEIGHT"),
            "weight_lbs": _extract_int(raw["WEIGHT"], r"(\d+) lbs\.", "WEIGHT"),
            "reach_in": _extract_int(raw["REACH"], r'(\d+)(?:\.0)?"', "REACH"),
            "stance": _clean(raw["STANCE"]),
            "dob": parse_date(raw["DOB"], "%b %d, %Y", "DOB"),
        }
    )
