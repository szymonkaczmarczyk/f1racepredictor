from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
import requests

from src.config import PROCESSED_DIR, RAW_DIR

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
RECENT = "https://api.open-meteo.com/v1/forecast"
CACHE_DIR = RAW_DIR / "weather"

WINDOW_BEFORE = pd.Timedelta(hours=1)
WINDOW_AFTER = pd.Timedelta(hours=2)
FULL_WET_MM = 4.0
ARCHIVE_LAG = pd.Timedelta(days=6)

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "f1racepredictor/1.0"})


def wet_index(rain_mm: float | np.ndarray) -> float | np.ndarray:
    return np.clip(np.asarray(rain_mm, dtype=float) / FULL_WET_MM, 0.0, 1.0)


def race_start(row) -> pd.Timestamp:
    value = getattr(row, "start_utc", None)
    if isinstance(value, str) and value:
        return pd.Timestamp(value).tz_convert("UTC")
    local_hour = 14.0 - float(row.lon) / 15.0
    return pd.Timestamp(row.date).tz_localize("UTC") + pd.Timedelta(hours=local_hour)


def update(races: pd.DataFrame, *, sleep: float = 0.15) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    now = pd.Timestamp.now(tz="UTC")
    fetched = failed = 0
    for row in races.itertuples(index=False):
        start = race_start(row)
        if start > now:
            continue
        path = CACHE_DIR / f"{row.race_id}.json"
        if path.exists():
            continue
        try:
            hourly = _fetch(float(row.lat), float(row.lon), start, now)
        except (requests.RequestException, ValueError, KeyError) as exc:
            failed += 1
            if "429" in str(exc):
                print("  weather: rate limited; re-run later to continue")
                break
            continue
        if hourly is None:
            continue
        path.write_text(json.dumps(hourly), encoding="utf-8")
        fetched += 1
        time.sleep(sleep)
    if fetched or failed:
        print(f"  weather: {fetched} races fetched" + (f", {failed} failed" if failed else ""))
    return table(races)


def table(races: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in races.itertuples(index=False):
        path = CACHE_DIR / f"{row.race_id}.json"
        if not path.exists():
            continue
        hourly = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
        hourly["time"] = pd.to_datetime(hourly["time"]).dt.tz_localize("UTC")
        start = race_start(row)
        window = hourly[
            (hourly["time"] >= (start - WINDOW_BEFORE).floor("h"))
            & (hourly["time"] < start + WINDOW_AFTER)
        ]
        rain = float(window["precipitation"].fillna(0).sum())
        rows.append({
            "race_id": row.race_id,
            "start_utc": start.isoformat(),
            "rain_mm": round(rain, 2),
            "wet_index": round(float(wet_index(rain)), 3),
        })
    return pd.DataFrame(rows, columns=["race_id", "start_utc", "rain_mm", "wet_index"])


def save(frame: pd.DataFrame) -> None:
    frame.to_csv(PROCESSED_DIR / "race_weather.csv", index=False)


def load() -> pd.Series:
    path = PROCESSED_DIR / "race_weather.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    frame = pd.read_csv(path)
    return pd.Series(frame["wet_index"].to_numpy(), index=frame["race_id"].to_numpy())


def _fetch(lat: float, lon: float, start: pd.Timestamp, now: pd.Timestamp) -> dict | None:
    recent = now - start < ARCHIVE_LAG
    response = _SESSION.get(
        RECENT if recent else ARCHIVE,
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation",
            "start_date": str((start - pd.Timedelta(days=1)).date()),
            "end_date": str((start + pd.Timedelta(days=1)).date()),
            "timezone": "UTC",
        },
        timeout=30,
    )
    response.raise_for_status()
    hourly = response.json()["hourly"]
    if not any(v is not None for v in hourly.get("precipitation", [])):
        return None
    return hourly
