from __future__ import annotations

import pandas as pd

from src.ingest import openf1
from src.ingest.weather_history import race_start

RACE_DURATION = pd.Timedelta(hours=3)

EXPECTED_GRID_SESSIONS = 3


def now_utc() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def build_calendar(
    races: pd.DataFrame,
    results: pd.DataFrame,
    quali: pd.DataFrame,
    meetings: list[dict] | None = None,
) -> list[dict]:
    season = int(races["season"].max())
    season_races = races[races["season"] == season].sort_values("round")
    if meetings is None:
        meetings = openf1.cached_meetings(season)
    run = set(results["race_id"].unique())

    completed = season_races[season_races["race_id"].isin(run)]
    last_id = completed.iloc[-1]["race_id"] if not completed.empty else None
    last_lineup = _last_lineup(results, quali, last_id) if last_id else []

    out = []
    for row in season_races.itertuples(index=False):
        start = _start(row)
        meeting = openf1.meeting_for(start, meetings) if meetings else None
        entry = {
            "race_id": row.race_id,
            "season": season,
            "round": int(row.round),
            "race_name": row.race_name,
            "circuit_id": row.circuit_id,
            "circuit_name": row.circuit_name,
            "country": row.country,
            "locality": row.locality,
            "lat": float(row.lat),
            "lon": float(row.lon),
            "date": str(row.date.date()),
            "start_utc": start.isoformat(),
            "quali_utc": _iso(getattr(row, "quali_utc", None)),
            "completed": bool(row.race_id in run),
            "cancelled": bool(meeting and meeting.get("is_cancelled")),
        }
        if row.race_id == last_id:
            entry["lineup"] = last_lineup
        elif not entry["completed"]:
            race_quali = quali[quali["race_id"] == row.race_id].sort_values("quali_position")
            if not race_quali.empty:
                entry["lineup"] = _quali_lineup(race_quali)
                entry["lineup_source"] = "qualifying"
        out.append(entry)
    return out


def with_status(calendar: list[dict], now: pd.Timestamp | None = None) -> list[dict]:
    now = now or now_utc()
    out = []
    for race in calendar:
        race = dict(race)
        start = pd.Timestamp(race["start_utc"])
        if race["completed"]:
            status = "completed"
        elif race.get("cancelled"):
            status = "cancelled"
        elif start + RACE_DURATION <= now:
            status = "awaiting_results"
        elif start <= now:
            status = "in_progress"
        else:
            status = "upcoming"
        race["status"] = status
        out.append(race)
    return out


def next_race(calendar: list[dict], now: pd.Timestamp | None = None) -> dict | None:
    for race in with_status(calendar, now):
        if race["status"] in ("upcoming", "in_progress"):
            return race
    return None


def race_at(calendar: list[dict], circuit_id: str, now: pd.Timestamp | None = None) -> dict | None:
    here = [r for r in with_status(calendar, now) if r["circuit_id"] == circuit_id]
    pending = [r for r in here if r["status"] in ("upcoming", "in_progress")]
    if pending:
        return pending[0]
    return here[-1] if here else None


def needs_sync(calendar: list[dict], now: pd.Timestamp | None = None) -> bool:
    now = now or now_utc()
    for race in with_status(calendar, now):
        if race["status"] == "awaiting_results":
            return True
        quali = race.get("quali_utc")
        if (
            race["status"] == "upcoming"
            and quali
            and pd.Timestamp(quali) + pd.Timedelta(hours=2) <= now
            and race.get("lineup_source") != "qualifying"
        ):
            return True
    return False


def _last_lineup(results: pd.DataFrame, quali: pd.DataFrame, race_id: str) -> list[dict]:
    field = results[results["race_id"] == race_id].sort_values("grid")
    history = quali[
        quali["driver_id"].isin(field["driver_id"]) & (quali["race_id"] <= race_id)
    ].sort_values(["season", "round"])
    gaps = history.groupby("driver_id")["quali_gap_pct"].apply(
        lambda s: s.dropna().tail(EXPECTED_GRID_SESSIONS).median()
    )
    order = field.assign(gap=field["driver_id"].map(gaps)).sort_values(
        ["gap", "grid"], na_position="last"
    )
    best = order["gap"].min()
    return [
        {
            "driver_id": r.driver_id,
            "constructor_id": r.constructor_id,
            "grid": i,
            "quali_position": i,
            "quali_gap_pct": None if pd.isna(r.gap) else round(float(r.gap - best), 3),
        }
        for i, r in enumerate(order.itertuples(index=False), start=1)
    ]


def _quali_lineup(race_quali: pd.DataFrame) -> list[dict]:
    return [
        {
            "driver_id": r.driver_id,
            "constructor_id": r.constructor_id,
            "grid": int(r.quali_position),
            "quali_position": int(r.quali_position),
            "quali_gap_pct": float(r.quali_gap_pct) if pd.notna(r.quali_gap_pct) else None,
        }
        for r in race_quali.itertuples(index=False)
    ]


def _start(row) -> pd.Timestamp:
    return race_start(row)


def _iso(value) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return pd.Timestamp(value).tz_convert("UTC").isoformat()
