from __future__ import annotations

import json
import logging
import shutil
import tempfile

import numpy as np
import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR
from src.ingest.practice import _schedule

CACHE_DIR = RAW_DIR / "race_laps"
MIN_STINT_LAPS = 8
SLOW_LAP_FACTOR = 1.05
FUEL_EFFECT_S_PER_LAP = 0.055
WET_COMPOUNDS = {"INTERMEDIATE", "WET"}
WET_RACE_SHARE = 0.1


def fetch_race(season: int, race_date: pd.Timestamp, race_id: str) -> dict | None:
    path = CACHE_DIR / f"{race_id}.json"
    if path.exists():
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
        round_number = int(schedule.loc[gaps.idxmin(), "RoundNumber"])
        session = fastf1.get_session(season, round_number, "R")
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        stints = stint_slopes(session.laps)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if not stints:
        return None
    payload = {"race_id": race_id, "stints": stints}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def stint_slopes(laps: pd.DataFrame) -> list[dict]:
    if laps is None or laps.empty:
        return []
    laps = laps.copy()
    laps["seconds"] = laps["LapTime"].dt.total_seconds()
    clean = laps[
        laps["seconds"].notna()
        & laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
        & (laps["TrackStatus"].astype(str) == "1")
        & laps["TyreLife"].notna()
    ]
    out = []
    for (driver, stint), part in clean.groupby(["Driver", "Stint"]):
        part = part[part["seconds"] <= part["seconds"].median() * SLOW_LAP_FACTOR]
        if len(part) < MIN_STINT_LAPS:
            continue
        slope = float(np.polyfit(part["TyreLife"].astype(float), part["seconds"], 1)[0])
        median = float(part["seconds"].median())
        out.append({
            "driver": str(driver),
            "compound": str(part["Compound"].dropna().iloc[0]) if part["Compound"].notna().any() else None,
            "laps": int(len(part)),
            "slope": round(slope, 4),
            "median_lap": round(median, 3),
            "deg_pct_per_lap": round((slope + FUEL_EFFECT_S_PER_LAP) / median * 100.0, 4),
        })
    return out


def table(races: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in races.itertuples(index=False):
        path = CACHE_DIR / f"{row.race_id}.json"
        if not path.exists():
            continue
        stints = json.loads(path.read_text(encoding="utf-8"))["stints"]
        wet = [s for s in stints if s.get("compound") in WET_COMPOUNDS]
        if len(wet) > WET_RACE_SHARE * len(stints):
            continue
        values = [s["deg_pct_per_lap"] for s in stints if s.get("compound") not in WET_COMPOUNDS]
        if len(values) < 5:
            continue
        rows.append({
            "race_id": row.race_id,
            "season": row.season,
            "circuit_id": row.circuit_id,
            "stints": len(values),
            "deg_pct_per_lap": round(float(np.median(values)), 4),
        })
    return pd.DataFrame(rows, columns=["race_id", "season", "circuit_id", "stints", "deg_pct_per_lap"])


def save(frame: pd.DataFrame) -> None:
    frame.to_csv(PROCESSED_DIR / "race_degradation.csv", index=False)


def load() -> pd.DataFrame:
    path = PROCESSED_DIR / "race_degradation.csv"
    if not path.exists():
        return pd.DataFrame(columns=["race_id", "season", "circuit_id", "stints", "deg_pct_per_lap"])
    return pd.read_csv(path)
