from __future__ import annotations

import time

import pandas as pd
import requests

from src.features.weather import WEATHER_PRESETS
from src.ingest.weather_history import WINDOW_AFTER, WINDOW_BEFORE, wet_index

API = "https://api.open-meteo.com/v1/forecast"
HORIZON = pd.Timedelta(days=15)
RACE_WINDOW = WINDOW_AFTER
CACHE_SECONDS = 3600

DRY_MM = 0.3

_cache: dict[tuple, tuple[float, dict | None]] = {}


def race_weather(lat: float, lon: float, start_utc: str) -> dict | None:
    start = pd.Timestamp(start_utc).tz_convert("UTC")
    now = pd.Timestamp.now(tz="UTC")
    if start + RACE_WINDOW < now or start - now > HORIZON:
        return None

    key = (round(lat, 3), round(lon, 3), start.isoformat())
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]

    try:
        result = _fetch(lat, lon, start)
    except (requests.RequestException, ValueError, KeyError):
        result = None
    _cache[key] = (time.time(), result)
    return result


def _fetch(lat: float, lon: float, start: pd.Timestamp) -> dict | None:
    response = requests.get(
        API,
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation,precipitation_probability,cloud_cover,temperature_2m",
            "start_date": str((start - WINDOW_BEFORE).date()),
            "end_date": str((start + RACE_WINDOW).date()),
            "timezone": "UTC",
        },
        timeout=10,
    )
    response.raise_for_status()
    hourly = pd.DataFrame(response.json()["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"]).dt.tz_localize("UTC")
    window = hourly[
        (hourly["time"] >= (start - WINDOW_BEFORE).floor("h"))
        & (hourly["time"] < start + RACE_WINDOW)
    ]
    if window.empty:
        return None

    rain_mm = float(window["precipitation"].fillna(0).sum())
    chance = float(window["precipitation_probability"].fillna(0).max()) / 100.0
    cloud = float(window["cloud_cover"].fillna(0).mean())
    preset = to_preset(rain_mm, chance, cloud)
    return {
        "source": "open-meteo",
        "rain_mm": round(rain_mm, 1),
        "rain_chance": round(chance, 2),
        "cloud_cover": round(cloud),
        "temperature_c": round(float(window["temperature_2m"].mean()), 1),
        "preset": preset,
        "wet_index": WEATHER_PRESETS[preset],
        "fetched_at": pd.Timestamp.now(tz="UTC").isoformat(),
    }


def to_preset(rain_mm: float, chance: float, cloud_cover: float) -> str:
    if chance < 0.2 or rain_mm < DRY_MM:
        return "cloudy" if cloud_cover >= 70 else "dry"
    expected = chance * float(wet_index(rain_mm))
    return min(WEATHER_PRESETS, key=lambda name: abs(WEATHER_PRESETS[name] - expected))
