from __future__ import annotations

import json
import time

import pandas as pd
import requests

from src.config import RAW_DIR

API_BASE = "https://api.openf1.org/v1"
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "f1racepredictor/1.0"})


def get(endpoint: str, attempts: int = 4, **params) -> list[dict]:
    delay = 1.0
    for attempt in range(attempts):
        response = _SESSION.get(f"{API_BASE}/{endpoint}", params=params, timeout=30)
        if response.status_code == 429 and attempt < attempts - 1:
            try:
                delay = max(delay, float(response.headers.get("Retry-After", "")))
            except ValueError:
                pass
            time.sleep(min(delay, 10.0))
            delay *= 2
            continue
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    return []


def meetings(season: int, *, refresh: bool = False) -> list[dict]:
    cache = RAW_DIR / f"openf1_meetings_{season}.json"
    if cache.exists() and not refresh:
        return json.loads(cache.read_text(encoding="utf-8"))
    rows = get("meetings", year=season)
    cache.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def cached_meetings(season: int) -> list[dict]:
    cache = RAW_DIR / f"openf1_meetings_{season}.json"
    if not cache.exists():
        return []
    try:
        return json.loads(cache.read_text(encoding="utf-8"))
    except ValueError:
        return []


def meeting_for(race_start: pd.Timestamp, rows: list[dict]) -> dict | None:
    best, best_gap = None, pd.Timedelta(days=4)
    for row in rows:
        if "Testing" in (row.get("meeting_name") or ""):
            continue
        end = pd.Timestamp(row.get("date_end") or row.get("date_start"))
        end = end.tz_convert("UTC") if end.tzinfo else end.tz_localize("UTC")
        gap = abs(end - race_start)
        if gap < best_gap:
            best, best_gap = row, gap
    return best


_SESSIONS_TTL = 600.0
_sessions_cache: dict[int, tuple[float, list[dict]]] = {}


def qualifying_session(race_start: pd.Timestamp, season: int) -> dict | None:
    hit = _sessions_cache.get(season)
    if hit and time.time() - hit[0] < _SESSIONS_TTL:
        sessions = hit[1]
    else:
        sessions = get("sessions", year=season, session_name="Qualifying")
        _sessions_cache[season] = (time.time(), sessions)
    window_start = race_start - pd.Timedelta(days=4)
    best = None
    for s in sessions:
        start = pd.Timestamp(s["date_start"]).tz_convert("UTC")
        if window_start <= start <= race_start and (best is None or start > best[0]):
            best = (start, s)
    return best[1] if best else None


def starting_grid(session_key: int) -> dict[int, int]:
    rows = get("starting_grid", session_key=session_key)
    return {
        int(r["driver_number"]): int(r["position"])
        for r in rows
        if r.get("driver_number") is not None and r.get("position") is not None
    }
