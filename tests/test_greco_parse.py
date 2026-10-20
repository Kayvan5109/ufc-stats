from io import StringIO

import pandas as pd
import pytest

from ufc_stats.parse.greco import (
    ParseError,
    parse_events,
    parse_fight_results,
    parse_fight_stats,
    parse_fighter_details,
    parse_fighter_tott,
    read_raw,
)

# Small samples copied from the 2026-10-18 snapshot, plus edge cases.
EVENTS_CSV = """EVENT,URL,DATE,LOCATION
UFC Fight Night: Buckley vs. Malott,http://ufcstats.com/event-details/55e94a9b525dcf45,"October 17, 2026","Edmonton, Alberta, Canada"
UFC 2: No Way Out,http://ufcstats.com/event-details/a6a9ab5a824e8f66,"March 11, 1994","Denver, Colorado, USA"
"""

RESULTS_CSV = """EVENT,BOUT,OUTCOME,WEIGHTCLASS,METHOD,ROUND,TIME,TIME FORMAT,REFEREE,DETAILS,URL
UFC Fight Night: Buckley vs. Malott ,Joaquin Buckley vs. Mike Malott,L/W,Welterweight Bout,KO/TKO ,2,2:32,5 Rnd (5-5-5-5-5),Marc Goddard,Knee to Head At Distance ,http://ufcstats.com/fight-details/c20c949ceba035f3
UFC Fight Night: Buckley vs. Malott ,Erin Blanchfield vs. Jasmine Jasudavicius,W/L,UFC Interim Women's Flyweight Title Bout,Decision - Unanimous ,3,5:00,3 Rnd (5-5-5),Jerin Valel,Eric Colon 28 - 29.,http://ufcstats.com/fight-details/16f8c3c83d56a25a
UFC 2: No Way Out ,Royce Gracie vs. Remco Pardoel,D/D,UFC 2 Tournament Title Bout,Submission ,1,1:31,No Time Limit,--,Lapel Choke ,http://ufcstats.com/fight-details/aaaaaaaaaaaaaaaa
UFC 9 ,Ken Shamrock vs. Dan Severn,NC/NC,UFC Superfight Championship Bout,Decision - Split ,2,3:00,1 Rnd + OT (30-5),John McCarthy,,http://ufcstats.com/fight-details/bbbbbbbbbbbbbbbb
"""

STATS_CSV = """EVENT,BOUT,ROUND,FIGHTER,KD,SIG.STR.,SIG.STR. %,TOTAL STR.,TD,TD %,SUB.ATT,REV.,CTRL,HEAD,BODY,LEG,DISTANCE,CLINCH,GROUND
UFC Fight Night: Buckley vs. Malott,Joaquin Buckley vs. Mike Malott,Round 2,Joaquin Buckley,1.0,5 of 16,31%,11 of 22,0 of 2,---,0.0,0.0,0:08,1 of 12,3 of 3,1 of 1,1 of 12,4 of 4,0 of 0
UFC 17: Redemption,Andre Roberts vs. Harry Moskowitz,,,,,,,,,,,,,,,,,
UFC 2: No Way Out,Royce Gracie vs. Remco Pardoel,Round 1,Royce Gracie,0.0,0 of 0,---,3 of 4,1 of 1,100%,1.0,0.0,--,0 of 0,0 of 0,0 of 0,0 of 0,0 of 0,0 of 0
"""

FIGHTER_DETAILS_CSV = """FIRST,LAST,NICKNAME,URL
Danny,Abbadi,The Assassin,http://ufcstats.com/fighter-details/15df64c02b6b0fde
Tom,Aaron,,http://ufcstats.com/fighter-details/93fe7332d16c6ad9
"""

TOTT_CSV = '''FIGHTER,HEIGHT,WEIGHT,REACH,STANCE,DOB,URL
Danny Abbadi,"5' 11""",155 lbs.,"71""",Orthodox,"Jul 03, 1983",http://ufcstats.com/fighter-details/15df64c02b6b0fde
Tom Aaron,--,--,--,,--,http://ufcstats.com/fighter-details/93fe7332d16c6ad9
'''


def raw(text: str) -> pd.DataFrame:
    return read_raw(StringIO(text))


def test_parse_events() -> None:
    events = parse_events(raw(EVENTS_CSV))

    first = events.iloc[0]
    assert first["event_id"] == "55e94a9b525dcf45"
    assert first["event_date"] == pd.Timestamp("2026-10-17")
    assert first["country"] == "Canada"
    assert events["event_date"].iloc[1] == pd.Timestamp("1994-03-11")


def test_parse_fight_results_core_fields() -> None:
    fights = parse_fight_results(raw(RESULTS_CSV))

    first = fights.iloc[0]
    assert first["fight_id"] == "c20c949ceba035f3"
    assert first["event_name"] == "UFC Fight Night: Buckley vs. Malott"
    assert (first["fighter_a"], first["fighter_b"]) == ("Joaquin Buckley", "Mike Malott")
    assert (first["outcome_a"], first["outcome_b"]) == ("L", "W")
    assert first["winner"] == "Mike Malott"
    assert first["method"] == "KO/TKO"
    assert first["details"] == "Knee to Head At Distance"
    assert first["end_time_seconds"] == 152


def test_parse_fight_results_division_and_title() -> None:
    fights = parse_fight_results(raw(RESULTS_CSV))

    assert fights["division"].tolist()[:2] == ["Welterweight", "Women's Flyweight"]
    assert pd.isna(fights["division"].iloc[2])
    assert fights["is_title_bout"].tolist() == [False, True, True, True]


def test_parse_fight_results_draw_and_no_contest_have_no_winner() -> None:
    fights = parse_fight_results(raw(RESULTS_CSV))

    assert fights["winner"].iloc[2:].isna().all()
    assert fights["outcome_a"].tolist()[2:] == ["D", "NC"]
    assert pd.isna(fights["referee"].iloc[2])


def test_parse_fight_results_scheduled_rounds_and_duration() -> None:
    fights = parse_fight_results(raw(RESULTS_CSV))

    # 5 x 5-min rounds, ended 2:32 into round 2 -> 5:00 + 2:32.
    assert fights["scheduled_rounds"].iloc[0] == 5
    assert fights["fight_duration_seconds"].iloc[0] == 452
    assert fights["fight_duration_seconds"].iloc[1] == 900
    # No Time Limit: unknown schedule, duration is the round-1 clock.
    assert pd.isna(fights["scheduled_rounds"].iloc[2])
    assert fights["fight_duration_seconds"].iloc[2] == 91
    # 30-min round + 5-min OT, ended 3:00 into OT.
    assert fights["scheduled_rounds"].iloc[3] == 2
    assert fights["fight_duration_seconds"].iloc[3] == 30 * 60 + 180


def test_parse_fight_stats() -> None:
    stats = parse_fight_stats(raw(STATS_CSV))

    first = stats.iloc[0]
    assert first["round"] == 2
    assert first["kd"] == 1
    assert (first["sig_str_landed"], first["sig_str_attempted"]) == (5, 16)
    assert (first["total_str_landed"], first["total_str_attempted"]) == (11, 22)
    assert (first["td_landed"], first["td_attempted"]) == (0, 2)
    assert first["ctrl_seconds"] == 8
    assert "SIG.STR. %" not in stats.columns and "sig_str_pct" not in stats.columns
    # Missing control time in early events is "--".
    assert pd.isna(stats["ctrl_seconds"].iloc[2])


def test_parse_fight_stats_keeps_empty_rows() -> None:
    stats = parse_fight_stats(raw(STATS_CSV))

    assert len(stats) == 3
    empty = stats.iloc[1]
    assert empty["bout"] == "Andre Roberts vs. Harry Moskowitz"
    assert empty.drop(["event_name", "bout"]).isna().all()


def test_parse_fighter_details() -> None:
    fighters = parse_fighter_details(raw(FIGHTER_DETAILS_CSV))

    assert fighters["fighter_id"].tolist() == ["15df64c02b6b0fde", "93fe7332d16c6ad9"]
    assert fighters["nickname"].iloc[0] == "The Assassin"
    assert pd.isna(fighters["nickname"].iloc[1])


def test_parse_fighter_tott() -> None:
    tott = parse_fighter_tott(raw(TOTT_CSV))

    first = tott.iloc[0]
    assert (first["height_in"], first["weight_lbs"], first["reach_in"]) == (71, 155, 71)
    assert first["stance"] == "Orthodox"
    assert first["dob"] == pd.Timestamp("1983-07-03")
    assert tott.iloc[1].drop(["fighter_id", "fighter"]).isna().all()


@pytest.mark.parametrize(
    ("parser", "text", "column"),
    [
        (parse_fight_stats, STATS_CSV.replace("5 of 16", "5/16"), "SIG.STR."),
        (parse_fight_stats, STATS_CSV.replace("0:08", "8s"), "CTRL"),
        (parse_fight_results, RESULTS_CSV.replace("L/W", "L/X"), "OUTCOME"),
        (parse_fight_results, RESULTS_CSV.replace("3 Rnd (5-5-5)", "3 rounds"), "TIME FORMAT"),
        (parse_events, EVENTS_CSV.replace("October 17, 2026", "2026-10-17"), "DATE"),
        (parse_fighter_tott, TOTT_CSV.replace("155 lbs.", "155kg"), "WEIGHT"),
        (parse_fighter_details, FIGHTER_DETAILS_CSV.replace("ufcstats.com", "example.com", 1), "URL"),
    ],
)
def test_unexpected_format_raises_naming_column(parser, text, column) -> None:
    with pytest.raises(ParseError, match=column):
        parser(raw(text))
