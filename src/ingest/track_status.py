from __future__ import annotations

import json
import logging
import shutil
import tempfile
import warnings

import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR
from src.ingest import practice

FIRST_SEASON = 2018
CACHE_DIR = RAW_DIR / "track_status"
COLUMNS = ["safety_cars", "virtual_safety_cars", "red_flags"]
_CODES = {"4": "safety_cars", "6": "virtual_safety_cars", "5": "red_flags"}


def fetch_race(season: int, race_date: pd.Timestamp, race_id: str) -> dict | None:
    path = CACHE_DIR / f"{race_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    import fastf1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastf1 import api

    fastf1.set_log_level(logging.ERROR)
    schedule = practice._schedule(season)
    dates = pd.to_datetime(schedule["EventDate"]).dt.normalize()
    gaps = (dates - pd.Timestamp(race_date).normalize()).abs()
    if gaps.empty or gaps.min() > pd.Timedelta(days=3):
        return None
    event = schedule.loc[gaps.idxmin()]

    scratch = tempfile.mkdtemp(prefix="fastf1-")
    try:
        fastf1.Cache.enable_cache(scratch)
        session = fastf1.get_session(season, int(event["RoundNumber"]), "R")
        data = api.track_status_data(session.api_path)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    counts = {col: 0 for col in COLUMNS}
    for status in data.get("Status", []):
        key = _CODES.get(str(status))
        if key:
            counts[key] += 1
    payload = {"race_id": race_id, **counts}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def table() -> pd.DataFrame:
    rows = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(CACHE_DIR.glob("*.json"))
    ] if CACHE_DIR.exists() else []
    return pd.DataFrame(rows, columns=["race_id", *COLUMNS])


def save(frame: pd.DataFrame) -> None:
    frame.to_csv(PROCESSED_DIR / "track_status.csv", index=False)


def load() -> pd.DataFrame:
    path = PROCESSED_DIR / "track_status.csv"
    if not path.exists():
        return pd.DataFrame(columns=["race_id", *COLUMNS])
    return pd.read_csv(path)
