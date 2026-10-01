from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterator

import requests

from src.config import API_BASE, API_PAGE_SIZE, API_SLEEP, RAW_DIR

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "f1racepredictor/1.0"})


class ErgastError(RuntimeError):
    pass


def _cache_path(endpoint: str) -> Path:
    return RAW_DIR / (endpoint.strip("/").replace("/", "_") + ".json")


def _get(url: str, params: dict[str, Any], attempts: int = 7) -> dict:
    delay = 1.0
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = _SESSION.get(url, params=params, timeout=45)
            if response.status_code == 429:
                wait = _retry_after(response, fallback=min(60.0, delay * 4))
                last_error = ErgastError(f"rate limited (429) on {url}")
                time.sleep(wait)
                delay *= 2
                continue
            response.raise_for_status()
            return response.json()
        except ErgastError:
            raise
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
            delay *= 2
    raise ErgastError(f"failed to fetch {url} ({params}): {last_error}")


def _retry_after(response, fallback: float) -> float:
    try:
        return max(1.0, min(300.0, float(response.headers.get("Retry-After", ""))))
    except (TypeError, ValueError):
        return fallback


def fetch(endpoint: str, *, refresh: bool = False) -> dict:
    cache = _cache_path(endpoint)
    if cache.exists() and not refresh:
        return json.loads(cache.read_text(encoding="utf-8"))

    url = f"{API_BASE}/{endpoint.strip('/')}.json"
    first = _get(url, {"limit": API_PAGE_SIZE, "offset": 0})
    mr = first["MRData"]
    total = int(mr.get("total", 0))

    table_key = next(k for k in mr if k.endswith("Table"))
    table = mr[table_key]
    list_key = next(k for k, v in table.items() if isinstance(v, list))

    rows = table[list_key]
    offset = API_PAGE_SIZE
    while offset < total:
        time.sleep(API_SLEEP)
        page = _get(url, {"limit": API_PAGE_SIZE, "offset": offset})
        page_table = page["MRData"][table_key]
        rows.extend(page_table[list_key])
        offset += API_PAGE_SIZE

    if list_key == "Races":
        merged: dict[str, dict] = {}
        for race in rows:
            key = f"{race['season']}_{race['round']}"
            if key in merged:
                for nested in ("Results", "QualifyingResults", "SprintResults", "PitStops", "Laps"):
                    if nested in race:
                        merged[key].setdefault(nested, []).extend(race[nested])
            else:
                merged[key] = race
        rows = list(merged.values())

    table[list_key] = rows
    cache.write_text(json.dumps(mr, ensure_ascii=False), encoding="utf-8")
    time.sleep(API_SLEEP)
    return mr


def races(season: int, **kw) -> list[dict]:
    return fetch(f"{season}/races", **kw)["RaceTable"]["Races"]


def results(season: int, **kw) -> list[dict]:
    return fetch(f"{season}/results", **kw)["RaceTable"]["Races"]


def qualifying(season: int, **kw) -> list[dict]:
    return fetch(f"{season}/qualifying", **kw)["RaceTable"]["Races"]


def sprint(season: int, **kw) -> list[dict]:
    return fetch(f"{season}/sprint", **kw)["RaceTable"]["Races"]



def drivers(season: int, **kw) -> list[dict]:
    return fetch(f"{season}/drivers", **kw)["DriverTable"]["Drivers"]


def constructors(season: int, **kw) -> list[dict]:
    return fetch(f"{season}/constructors", **kw)["ConstructorTable"]["Constructors"]


def seasons(start: int, end: int) -> Iterator[int]:
    return iter(range(start, end + 1))
