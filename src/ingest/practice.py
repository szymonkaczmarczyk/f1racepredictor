from __future__ import annotations

import json
import logging
import shutil
import tempfile

import numpy as np
import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR
from src.features.build import PRACTICE_COLUMNS

FIRST_PRACTICE_SEASON = 2018
CACHE_DIR = RAW_DIR / "practice"
SESSIONS = ("FP1", "FP2", "FP3")
MIN_STINT_LAPS = 5
SLOW_LAP_FACTOR = 1.07


def fetch_weekend(season: int, race_date: pd.Timestamp, race_id: str, *, refresh: bool = False) -> dict | None:
    path = CACHE_DIR / f"{race_id}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))

    import fastf1

    fastf1.set_log_level(logging.ERROR)
    scratch = tempfile.mkdtemp(prefix="fastf1-")
    try:
        fastf1.Cache.enable_cache(scratch)
        schedule = _schedule(season)
        dates = pd.to_datetime(schedule["EventDate"]).dt.tz_localize(None).dt.normalize()
        gaps = (dates - pd.Timestamp(race_date).normalize()).abs()
        if gaps.empty or gaps.min() > pd.Timedelta(days=3):
            return None
        event = schedule.loc[gaps.idxmin()]
        sessions = {}
        for name in SESSIONS:
            try:
                session = fastf1.get_session(season, int(event["RoundNumber"]), name)
                session.load(laps=True, telemetry=False, weather=False, messages=False)
                summary = summarise(session.laps)
            except Exception:
                continue
            if summary:
                sessions[name] = summary
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if not sessions:
        return None
    payload = {"race_id": race_id, "event": str(event["EventName"]), "sessions": sessions}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def _schedule(season: int) -> pd.DataFrame:
    path = CACHE_DIR / f"schedule_{season}.json"
    if path.exists():
        return pd.read_json(path)
    import fastf1

    frame = pd.DataFrame(fastf1.get_event_schedule(season, include_testing=False))
    frame = frame[["RoundNumber", "EventName", "EventDate"]].copy()
    frame["EventDate"] = pd.to_datetime(frame["EventDate"]).dt.strftime("%Y-%m-%d")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_json(path, orient="records")
    return frame


def summarise(laps: pd.DataFrame) -> dict:
    if laps is None or laps.empty:
        return {}
    laps = laps.copy()
    laps["seconds"] = laps["LapTime"].dt.total_seconds()
    clean = laps[
        laps["seconds"].notna()
        & laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
        & (laps["TrackStatus"].astype(str) == "1")
        & (laps["Deleted"] != True)
    ]
    out = {}
    for driver, own in laps.groupby("Driver"):
        timed = own["seconds"].dropna()
        entry = {
            "team": str(own["Team"].dropna().iloc[0]) if own["Team"].notna().any() else None,
            "best": float(timed.min()) if len(timed) else None,
            "long_run": None,
            "long_run_laps": 0,
        }
        runs = []
        for _, stint in clean[clean["Driver"] == driver].groupby("Stint"):
            times = stint["seconds"]
            times = times[times <= times.median() * SLOW_LAP_FACTOR]
            if len(times) >= MIN_STINT_LAPS:
                runs.append((float(times.median()), len(times)))
        if runs:
            pace, count = min(runs)
            entry["long_run"], entry["long_run_laps"] = pace, count
        out[str(driver)] = entry
    return out


def weekend_features(payload: dict | None, code_to_driver: dict[str, str]) -> pd.DataFrame:
    if not payload:
        return pd.DataFrame(columns=["driver_id", *PRACTICE_COLUMNS])
    best: dict[str, float] = {}
    long_run: dict[str, float] = {}
    team_of: dict[str, str] = {}
    for session in payload["sessions"].values():
        for code, stats in session.items():
            driver = code_to_driver.get(code.upper())
            if driver is None:
                continue
            team_of[driver] = stats.get("team") or team_of.get(driver)
            if stats.get("best"):
                best[driver] = min(best.get(driver, np.inf), stats["best"])
            if stats.get("long_run"):
                long_run[driver] = min(long_run.get(driver, np.inf), stats["long_run"])
    rows = []
    top = min(best.values()) if best else None
    top_run = min(long_run.values()) if long_run else None
    team_run: dict[str, float] = {}
    for driver, pace in long_run.items():
        team = team_of.get(driver)
        team_run[team] = min(team_run.get(team, np.inf), pace)
    for driver in set(best) | set(long_run):
        team = team_of.get(driver)
        rows.append({
            "driver_id": driver,
            "fp_best_gap_pct": _gap(best.get(driver), top),
            "fp_longrun_gap_pct": _gap(long_run.get(driver), top_run),
            "fp_team_longrun_gap_pct": _gap(team_run.get(team), top_run),
        })
    return pd.DataFrame(rows, columns=["driver_id", *PRACTICE_COLUMNS])


def table(races: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    frames = []
    codes = results.dropna(subset=["driver_code"])
    for row in races.itertuples(index=False):
        path = CACHE_DIR / f"{row.race_id}.json"
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        here = codes[codes["race_id"] == row.race_id]
        if here.empty:
            here = codes[codes["season"] == row.season].sort_values("date").drop_duplicates("driver_code", keep="last")
        mapping = {str(c).upper(): d for c, d in zip(here["driver_code"], here["driver_id"])}
        frame = weekend_features(payload, mapping)
        frame.insert(0, "race_id", row.race_id)
        frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=["race_id", "driver_id", *PRACTICE_COLUMNS])
    return pd.concat(frames, ignore_index=True)


def save(frame: pd.DataFrame) -> None:
    frame.to_csv(PROCESSED_DIR / "practice.csv", index=False)


def load() -> pd.DataFrame:
    path = PROCESSED_DIR / "practice.csv"
    if not path.exists():
        return pd.DataFrame(columns=["race_id", "driver_id", *PRACTICE_COLUMNS])
    return pd.read_csv(path)


def _gap(value: float | None, best: float | None) -> float | None:
    if value is None or best is None or not np.isfinite(value) or best <= 0:
        return None
    return round((value - best) / best * 100.0, 3)
