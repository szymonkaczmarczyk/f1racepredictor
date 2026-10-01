from __future__ import annotations

import math
import mimetypes
import os
import threading
import time
from functools import lru_cache

import pandas as pd
from flask import Flask, jsonify, request

from src import ledger, pipeline
from src.app import security
from src.app.site import site
from src.config import FIRST_SEASON, MODEL_DIR, PROCESSED_DIR
from src.features import prequali, registry
from src.features.weather import WEATHER_PRESETS
from src.ingest import forecast, openf1, practice, schedule
from src.models import backtest, championship
from src.models.predict import Conditions, Entry, Predictor

mimetypes.add_type("application/manifest+json", ".webmanifest")

app = Flask(__name__)
security.install(app)
app.register_blueprint(site)

MAX_ENTRIES = 26
GRID_SOURCES = ("race", "starting_grid", "qualifying", "openf1", "expected_practice", "expected")
SOURCE_RANK = {"expected": 1, "expected_practice": 2, "openf1": 3, "qualifying": 3,
               "starting_grid": 4, "race": 5}
MANUAL_SYNC_COOLDOWN = pd.Timedelta(seconds=60)

AUTO_SYNC = os.environ.get("F1_AUTO_SYNC", "1") != "0"
SYNC_ENDPOINT = os.environ.get("F1_SYNC_ENDPOINT", "1") != "0"
AUTO_SYNC_CHECK_SECONDS = 15 * 60
AUTO_SYNC_STALE_AFTER = pd.Timedelta(hours=12)
AUTO_SYNC_RETRY_AFTER = pd.Timedelta(minutes=30)

_state_lock = threading.RLock()
_predictor: Predictor | None = None
_df_races: pd.DataFrame
_df_results: pd.DataFrame
_df_quali: pd.DataFrame
_df_sprint: pd.DataFrame
_last_auto_attempt: pd.Timestamp | None = None
_scheduler: threading.Thread | None = None


def _data_stamp() -> tuple:
    return tuple(
        path.stat().st_mtime if path.exists() else 0.0
        for path in (pipeline.STATE_PATH, MODEL_DIR / "podium_model.joblib")
    )


_loaded_stamp: tuple | None = None


@app.before_request
def _refresh_after_external_sync():
    if _loaded_stamp is not None and _data_stamp() != _loaded_stamp and not pipeline.is_running():
        _reload()


def _reload() -> None:
    global _predictor, _df_races, _df_results, _df_quali, _df_sprint, _loaded_stamp
    with _state_lock:
        _loaded_stamp = _data_stamp()
        _df_races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
        _df_results = pd.read_csv(PROCESSED_DIR / "results.csv", parse_dates=["date"])
        _df_quali = pd.read_csv(PROCESSED_DIR / "qualifying.csv")
        sprint_path = PROCESSED_DIR / "sprint.csv"
        _df_sprint = (
            pd.read_csv(sprint_path) if sprint_path.exists()
            else pd.DataFrame(columns=["season", "driver_id", "constructor_id", "sprint_points"])
        )
        _predictor = None
        _calendar.cache_clear()
        _drivers.cache_clear()
        _teams.cache_clear()
        _track_history.cache_clear()
        _practice_table.cache_clear()
        backtest.clear()


def predictor() -> Predictor:
    global _predictor
    with _state_lock:
        if _predictor is None:
            _predictor = Predictor.load()
        return _predictor


def latest_season() -> int:
    return int(_df_races["season"].max())


@lru_cache(maxsize=8)
def _calendar(season: int) -> tuple:
    races = _df_races[_df_races["season"] <= season]
    if races.empty:
        return ()
    return tuple(schedule.build_calendar(races, _df_results, _df_quali))


def calendar_for(season: int) -> list[dict]:
    return schedule.with_status(list(_calendar(season)))


@lru_cache(maxsize=8)
def _drivers(season: int) -> dict:
    return registry.build_drivers(_df_results, season)


@lru_cache(maxsize=8)
def _teams(season: int) -> dict:
    return registry.build_teams(_df_results, season)


@lru_cache(maxsize=8)
def _track_history(season: int) -> dict:
    return registry.build_driver_track_history(_df_results, season)


@lru_cache(maxsize=1)
def _practice_table() -> pd.DataFrame:
    return practice.load()


def _practice_for(race_id: str) -> pd.DataFrame | None:
    table = _practice_table()
    weekend = table[table["race_id"] == race_id]
    return weekend.set_index("driver_id") if not weekend.empty else None


_reload()


def _with_weather(race: dict | None) -> dict | None:
    if race is None:
        return None
    race = dict(race)
    race["weather"] = forecast.race_weather(race["lat"], race["lon"], race["start_utc"])
    return race


@app.get("/api/bootstrap")
def bootstrap():
    season = request.args.get("season", type=int) or latest_season()

    p = predictor()
    cal = calendar_for(season)
    next_race = _with_weather(schedule.next_race(cal)) if season == latest_season() else None

    on_calendar = {}
    for r in cal:
        if r["status"] != "cancelled":
            on_calendar.setdefault(r["circuit_id"], r["round"])
    tracks = []
    for cid, meta in p.catalogue.items():
        tracks.append(
            {
                "circuit_id": cid,
                "name": meta["name"],
                "race_name": meta.get("race_name"),
                "country": meta.get("country"),
                "locality": meta.get("locality"),
                "laps": meta.get("laps"),
                "length_m": meta.get("length_m"),
                "distance_km": meta.get("distance_km"),
                "corners": meta.get("corners"),
                "track_difficulty": meta.get("track_difficulty"),
                "tyre_degradation": meta.get("tyre_degradation"),
                "is_street": meta.get("is_street"),
                "last_season": meta.get("last_season"),
                "on_calendar": cid in on_calendar,
                "round": on_calendar.get(cid),
                "has_map": "geometry" in meta,
                "stats": meta.get("stats", {}),
            }
        )
    tracks.sort(key=lambda t: (not t["on_calendar"], t["round"] or 0, t["name"]))

    drivers = [
        {
            "driver_id": d["driver_id"],
            "name": d["name"],
            "code": d["code"],
            "team": d["team"],
            "team_name": d["team_name"],
            "active": d["active"],
            "last_season": d["last_season"],
            "career": d["career"],
            "recent": d["recent"],
            "season": d["season"],
        }
        for d in _drivers(season).values()
    ]
    drivers.sort(key=lambda d: (not d["active"], -d["last_season"], d["name"]))

    return jsonify(
        {
            "tracks": tracks,
            "drivers": drivers,
            "teams": _teams(season),
            "calendar": cal,
            "next_race": next_race,
            "weather_options": list(WEATHER_PRESETS),
            "sync": {**pipeline.last_state(), "running": pipeline.is_running(),
                     "auto": AUTO_SYNC},
            "model": {
                "trained_through": p.trained_through,
                "seasons": p.seasons,
                "summary": p.report.get("summary", {}),
                "validation": p.report.get("validation", []),
                "validated_through": p.report.get("validated_through"),
                "calibration": p.report.get("calibration", {}),
                "importance": p.report.get("importance", [])[:14],
            },
        }
    )


@app.get("/api/track/<circuit_id>")
def track(circuit_id: str):
    meta = predictor().catalogue.get(circuit_id)
    if not meta:
        return jsonify({"error": "unknown circuit"}), 404
    return jsonify(meta)


@app.get("/api/lineup")
def lineup():
    circuit_id = request.args.get("circuit_id")
    season = request.args.get("season", type=int) or latest_season()
    entries, source, race = _lineup_for(season, circuit_id)
    history = _track_history(season)
    target = circuit_id or (race["circuit_id"] if race else None)
    return jsonify({
        "entries": entries,
        "source": source,
        "track_history": {
            e["driver_id"]: history.get(e["driver_id"], {}).get(target) for e in entries
        },
        "race": {k: race[k] for k in ("race_name", "round", "date", "status", "quali_utc")} if race else None,
    })


def _lineup_for(season: int, circuit_id: str | None) -> tuple[list[dict], str, dict | None]:
    cal = calendar_for(season)
    race = schedule.race_at(cal, circuit_id) if circuit_id else schedule.next_race(cal)

    entries, source = [], "expected"
    if race and race["status"] == "completed":
        entries, source = _race_grid(race["race_id"]), "race"
    elif race and race.get("lineup_source") == "qualifying":
        entries, source = [dict(e) for e in race["lineup"]], "qualifying"
    elif race and race["status"] in ("upcoming", "in_progress") and _quali_finished(race):
        entries = _openf1_grid(race, season)
        source = "openf1" if entries else "expected"

    if source in ("qualifying", "openf1"):
        starting = _starting_grid(race, season)
        if starting:
            entries, source = _apply_starting_grid(entries, starting), "starting_grid"

    if not entries:
        done = [r for r in cal if r["completed"]]
        entries = [dict(e) for e in (done[-1].get("lineup", []) if done else [])]
        weekend = _practice_for(race["race_id"]) if race else None
        if entries and weekend is not None:
            entries = _blend_with_practice(entries, weekend)
            source = "expected_practice"
    if not entries:
        entries = [
            {"driver_id": d["driver_id"], "constructor_id": d["team"]}
            for d in _drivers(season).values()
            if d["active"]
        ][:20]

    for i, e in enumerate(entries, start=1):
        e.setdefault("grid", i)
    return entries, source, race


def _blend_with_practice(entries: list[dict], weekend: pd.DataFrame) -> list[dict]:
    frame = pd.DataFrame(entries)
    frame["history"] = pd.to_numeric(frame["quali_gap_pct"], errors="coerce")
    frame["practice"] = frame["driver_id"].map(weekend["fp_best_gap_pct"])
    z = lambda s: (s - s.mean()) / (s.std() or 1.0)
    score = 0.5 * z(frame["history"]).fillna(z(frame["practice"])) + 0.5 * z(frame["practice"]).fillna(z(frame["history"]))
    gap = (0.5 * frame["history"] + 0.5 * frame["practice"]).fillna(frame["history"]).fillna(frame["practice"])
    frame = frame.assign(score=score, gap=gap).sort_values("score", na_position="last")
    best = frame["gap"].min()
    return [
        {
            "driver_id": r.driver_id,
            "constructor_id": r.constructor_id,
            "grid": i,
            "quali_position": i,
            "quali_gap_pct": None if pd.isna(r.gap) else round(float(r.gap - best), 3),
        }
        for i, r in enumerate(frame.itertuples(index=False), start=1)
    ]


def _race_grid(race_id: str) -> list[dict]:
    ran = _df_results[_df_results["race_id"] == race_id].sort_values("grid")
    quali = _df_quali[_df_quali["race_id"] == race_id].set_index("driver_id")
    out = []
    for i, r in enumerate(ran.itertuples(index=False), start=1):
        q = quali.loc[r.driver_id] if r.driver_id in quali.index else None
        out.append({
            "driver_id": r.driver_id,
            "constructor_id": r.constructor_id,
            "grid": i,
            "quali_position": int(q["quali_position"]) if q is not None else None,
            "quali_gap_pct": float(q["quali_gap_pct"]) if q is not None and pd.notna(q["quali_gap_pct"]) else None,
        })
    return out


def _quali_finished(race: dict) -> bool:
    quali = race.get("quali_utc")
    return bool(quali) and pd.Timestamp(quali) + pd.Timedelta(hours=1) <= schedule.now_utc()


_openf1_cache: dict[str, tuple[float, list[dict]]] = {}
OPENF1_CACHE_SECONDS = 600


@app.post("/api/sync")
def sync():
    if not SYNC_ENDPOINT:
        return jsonify({"error": "sync runs on a schedule on this server"}), 403
    last = pipeline.last_state().get("last_success_utc")
    if last and schedule.now_utc() - pd.Timestamp(last) < MANUAL_SYNC_COOLDOWN:
        return jsonify({"error": "synced less than a minute ago; try again shortly"}), 429
    try:
        state = _run_sync()
    except pipeline.SyncBusy as exc:
        return jsonify({"error": str(exc)}), 409
    except pipeline.SyncFailed as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify({"success": True, **state})


def _run_sync(full_validation: bool = False) -> dict:
    state = pipeline.run(full_validation=full_validation)
    _reload()
    return state


def _auto_sync_due(now: pd.Timestamp) -> bool:
    if _last_auto_attempt is not None and now - _last_auto_attempt < AUTO_SYNC_RETRY_AFTER:
        return False
    last = pipeline.last_state().get("last_success_utc")
    if last is None or now - pd.Timestamp(last) > AUTO_SYNC_STALE_AFTER:
        return True
    return schedule.needs_sync(list(_calendar(latest_season())), now)


def _auto_sync_loop() -> None:
    global _last_auto_attempt
    while True:
        now = schedule.now_utc()
        try:
            if _auto_sync_due(now) and not pipeline.is_running():
                _last_auto_attempt = now
                state = _run_sync()
                app.logger.warning("auto-sync: %s", state)
        except pipeline.SyncBusy:
            pass
        except Exception as exc:
            app.logger.warning("auto-sync failed: %s", exc)
        try:
            _auto_record(schedule.now_utc())
        except Exception as exc:
            app.logger.warning("auto-record failed: %s", exc)
        time.sleep(AUTO_SYNC_CHECK_SECONDS)


def start_background_sync() -> None:
    global _scheduler
    if not AUTO_SYNC or _scheduler is not None:
        return
    _scheduler = threading.Thread(target=_auto_sync_loop, name="auto-sync", daemon=True)
    _scheduler.start()


def _cached_openf1(key: str, fetch, race: dict, season: int):
    hit = _openf1_cache.get(key)
    if hit and time.time() - hit[0] < OPENF1_CACHE_SECONDS:
        return hit[1]
    try:
        value = fetch(race, season)
    except LookupError:
        return None
    except Exception:
        app.logger.warning("OpenF1 %s unavailable for %s", key, race["race_id"])
        return None
    _openf1_cache[key] = (time.time(), value)
    return value


def _openf1_grid(race: dict, season: int) -> list[dict]:
    entries = _cached_openf1(f"{race['race_id']}:quali", _fetch_openf1_grid, race, season)
    return [dict(e) for e in entries or []]


def _starting_grid(race: dict, season: int) -> dict[str, int]:
    return dict(_cached_openf1(f"{race['race_id']}:start", _fetch_starting_grid, race, season) or {})


def _past_qualifying(race: dict, season: int) -> dict:
    session = openf1.qualifying_session(pd.Timestamp(race["start_utc"]), season)
    if session is None:
        raise LookupError(f"no qualifying session on OpenF1 for {race['race_name']} {season}")
    if pd.Timestamp(session["date_start"]) > schedule.now_utc():
        raise LookupError(f"qualifying for {race['race_name']} has not happened yet "
                          f"(starts {session['date_start']})")
    return session


def _openf1_drivers(session_key: int, season: int) -> dict[int, dict]:
    drivers_data = openf1.get("drivers", session_key=session_key)
    num_to_code = {d["driver_number"]: d["name_acronym"] for d in drivers_data if d.get("name_acronym")}
    code_to_drv = {}
    for d_id, d in sorted(_drivers(season).items(), key=lambda kv: kv[1]["last_season"]):
        if d.get("code"):
            code_to_drv[d["code"].upper()] = {
                "driver_id": d_id, "constructor_id": d["team"], "name": d["name"]
            }
    return {
        num: code_to_drv[code.upper()]
        for num, code in num_to_code.items()
        if code.upper() in code_to_drv
    }


def _fetch_starting_grid(race: dict, season: int) -> dict[str, int]:
    session = _past_qualifying(race, season)
    positions = openf1.starting_grid(session["session_key"])
    if not positions:
        raise LookupError("starting grid not published yet on OpenF1")
    by_number = _openf1_drivers(session["session_key"], season)
    return {
        by_number[num]["driver_id"]: pos for num, pos in positions.items() if num in by_number
    }


def _apply_starting_grid(entries: list[dict], starting: dict[str, int]) -> list[dict]:
    back = len(entries) + 1
    ordered = sorted(
        entries,
        key=lambda e: (starting.get(e["driver_id"], back), int(e.get("grid") or back)),
    )
    return [{**e, "grid": i} for i, e in enumerate(ordered, start=1)]


def _fetch_openf1_grid(race: dict, season: int) -> list[dict]:
    session = _past_qualifying(race, season)
    results_data = openf1.get("session_result", session_key=session["session_key"])
    if not results_data:
        raise LookupError("qualifying results not available yet on OpenF1")
    by_number = _openf1_drivers(session["session_key"], season)

    best_times = {}
    for res in results_data:
        duration = res.get("duration")
        if duration and isinstance(duration, list):
            valid_times = [float(t) for t in duration if t is not None]
            if valid_times:
                best_times[res.get("driver_number")] = min(valid_times)
    pole_time = min(best_times.values()) if best_times else None

    out_entries = []
    for res in results_data:
        num = res.get("driver_number")
        pos = res.get("position")
        drv = by_number.get(num)
        if not drv or pos is None:
            continue
        gap_pct = None
        if pole_time and num in best_times:
            gap_pct = round((best_times[num] - pole_time) / pole_time * 100.0, 3)
        out_entries.append({
            "driver_id": drv["driver_id"],
            "constructor_id": drv["constructor_id"],
            "name": drv["name"],
            "grid": pos,
            "quali_position": pos,
            "quali_gap_pct": gap_pct,
        })

    out_entries.sort(key=lambda x: x["grid"])

    seen = {e["driver_id"] for e in out_entries}
    if race["completed"]:
        ran = _df_results[_df_results["race_id"] == race["race_id"]]
        field = ran[["driver_id", "constructor_id"]].to_dict(orient="records")
    else:
        done = [r for r in calendar_for(season) if r["completed"] and r.get("lineup")]
        field = done[-1]["lineup"] if done else []
    for e in field:
        if e["driver_id"] not in seen:
            info = _drivers(season).get(e["driver_id"], {})
            out_entries.append({
                "driver_id": e["driver_id"],
                "constructor_id": e["constructor_id"],
                "name": info.get("name", e["driver_id"]),
                "grid": len(out_entries) + 1,
                "quali_position": None,
                "quali_gap_pct": None,
            })
    return out_entries


@app.get("/api/driver/<driver_id>")
def driver(driver_id: str):
    season = request.args.get("season", type=int) or latest_season()
    info = _drivers(season).get(driver_id)
    if not info:
        return jsonify({"error": "unknown driver"}), 404
    return jsonify({**info, "tracks": _track_history(season).get(driver_id, {})})


@app.post("/api/predict")
def predict():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "expected a JSON object"}), 400
    raw_entries = body.get("entries")
    if not isinstance(raw_entries, list) or not raw_entries:
        return jsonify({"error": "no entries"}), 400
    if len(raw_entries) > MAX_ENTRIES:
        return jsonify({"error": f"at most {MAX_ENTRIES} cars"}), 400

    season = _int_or_none(body.get("season")) or latest_season()
    if not FIRST_SEASON <= season <= latest_season():
        return jsonify({"error": "unknown season"}), 400
    circuit_id = body.get("circuit_id")
    weather = body.get("weather", "dry")
    if weather not in WEATHER_PRESETS:
        return jsonify({"error": "unknown weather"}), 400

    p = predictor()
    if not isinstance(circuit_id, str) or circuit_id not in p.catalogue:
        return jsonify({"error": "unknown circuit"}), 400
    error = _entries_error(raw_entries, _drivers(season), _teams(season))
    if error:
        return jsonify({"error": error}), 400

    source = body.get("grid_source")
    base = body.get("base_source") if source == "what_if" else source
    result, race = _run_prediction(season, circuit_id, weather, raw_entries, body, source=base)
    if race and race["status"] == "upcoming" and source in GRID_SOURCES:
        ledger.record(race, result, source=source, trigger="predict", now=schedule.now_utc())
    return jsonify(result)


def _run_prediction(season: int, circuit_id: str, weather: str, raw_entries: list,
                    options: dict | None = None,
                    keep_positions: bool = False,
                    source: str | None = None) -> tuple[dict, dict | None]:
    options = options or {}
    p = predictor()
    cal = calendar_for(season)
    race = schedule.race_at(cal, circuit_id)
    rounds = max((r["round"] for r in cal), default=0)

    past = backtest.context(race) if race and race["status"] == "completed" else None
    p_season = Predictor(
        bundle={
            "models": past["models"] if past else p.models,
            "features": past.get("features", p.features) if past else p.features,
            "grid_priors": past["grid_priors"] if past else p.grid_priors,
            "blend_weights": p.blend_weights,
            "prequali": None if past else p.prequali,
            "trained_through": past["trained_through"] if past else p.trained_through,
            "seasons": p.seasons,
        },
        store=past["store"] if past else p.store,
        catalogue=p.catalogue,
        drivers=past["drivers"] if past else _drivers(season),
        teams=past["teams"] if past else _teams(season),
        track_history=past["track_history"] if past else _track_history(season),
        report=p.report,
    )

    entries = [
        Entry(
            driver_id=e["driver_id"],
            constructor_id=e.get("constructor_id") or p_season.drivers.get(e["driver_id"], {}).get("team", ""),
            grid=int(e.get("grid") or i + 1),
            quali_gap_pct=_float_or_none(e.get("quali_gap_pct")),
            quali_position=_int_or_none(e.get("quali_position")),
        )
        for i, e in enumerate(raw_entries)
    ]
    conditions = Conditions(
        circuit_id=circuit_id,
        weather=weather,
        tyre_degradation=_float_or_none(options.get("tyre_degradation")),
        track_difficulty=_float_or_none(options.get("track_difficulty")),
        laps=_int_or_none(options.get("laps")),
        distance_km=_float_or_none(options.get("distance_km")),
        season=season,
        round_norm=race["round"] / rounds if race and rounds else 0.5,
        date=pd.Timestamp(race["date"]) if race else None,
        practice=_practice_for(race["race_id"]) if race else None,
    )
    pre_qualifying = (
        source in prequali.PRE_QUALIFYING_SOURCES
        and not (race and race["status"] == "completed")
    )
    result = p_season.predict(entries, conditions, keep_positions=keep_positions,
                              pre_qualifying=pre_qualifying)
    if race:
        result["race"] = {k: race[k] for k in ("race_name", "round", "date", "start_utc", "status")}
    if past:
        result["mode"] = "backtest"
        for row in result["entries"]:
            row["actual"] = past["actual"].get(row["driver_id"])
    return result, race


@app.get("/api/championship")
def championship_outlook():
    return jsonify(_championship(latest_season(), _loaded_stamp))


@lru_cache(maxsize=2)
def _championship(season: int, stamp: tuple | None) -> dict:
    cal = calendar_for(season)
    left = [r for r in cal if r["status"] in ("upcoming", "in_progress")]
    sprints, sprints_known = _sprint_weekends(season, left)
    ran = _df_results[_df_results["season"] == season]
    sprint_rows = _df_sprint[_df_sprint["season"] == season]
    standings = ran.groupby("driver_id")["points"].sum().add(
        sprint_rows.groupby("driver_id")["sprint_points"].sum(), fill_value=0.0
    ).to_dict()
    team_standings = ran.groupby("constructor_id")["points"].sum().add(
        sprint_rows.groupby("constructor_id")["sprint_points"].sum(), fill_value=0.0
    ).to_dict()

    races, teams = [], {}
    for race in left:
        entries, source, _ = _lineup_for(season, race["circuit_id"])
        weather = (forecast.race_weather(race["lat"], race["lon"], race["start_utc"]) or {}).get("preset", "dry")
        result, _ = _run_prediction(season, race["circuit_id"], weather, entries,
                                    keep_positions=True, source=source)
        drivers = [e["driver_id"] for e in entries]
        teams.update({e["driver_id"]: e.get("constructor_id") or _drivers(season).get(e["driver_id"], {}).get("team") for e in entries})
        races.append(championship.SimulatedRace(
            drivers=drivers, positions=result["positions"], gone=result["gone"],
            sprint=race["race_id"] in sprints,
        ))
    for driver_id in standings:
        teams.setdefault(driver_id, ran.loc[ran["driver_id"] == driver_id, "constructor_id"].iloc[-1])

    out = championship.outlook(standings, races, teams, team_standings)
    names, team_names = _drivers(season), _teams(season)
    for row in out["drivers"]:
        info = names.get(row["id"], {})
        row.update({"name": info.get("name", row["id"]), "code": info.get("code"),
                    "team_name": team_names.get(teams.get(row["id"]), {}).get("name")})
        row["team_id"] = teams.get(row["id"])
    for row in out["teams"]:
        row["name"] = team_names.get(row["id"], {}).get("name", row["id"])
    out.update({"season": season, "sprints_known": sprints_known,
                "next_races": [r["race_name"] for r in left]})
    return out


def _sprint_weekends(season: int, races: list[dict]) -> tuple[set[str], bool]:
    try:
        sessions = openf1.get("sessions", year=season, session_name="Sprint")
    except Exception:
        return set(), False
    found = set()
    for race in races:
        start = pd.Timestamp(race["start_utc"])
        for session in sessions:
            when = pd.Timestamp(session["date_start"]).tz_convert("UTC")
            if start - pd.Timedelta(days=3) <= when <= start and not session.get("is_cancelled"):
                found.add(race["race_id"])
    return found, True


@app.get("/api/ledger")
def ledger_scorecard():
    return jsonify(ledger.scorecard(_df_results))


LEDGER_OPEN_BEFORE = pd.Timedelta(days=7)


def _auto_record(now: pd.Timestamp) -> None:
    season = latest_season()
    race = schedule.next_race(calendar_for(season), now)
    if race is None or race["status"] != "upcoming":
        return
    start = pd.Timestamp(race["start_utc"])
    if start - now > LEDGER_OPEN_BEFORE:
        return
    existing = ledger.recorded(race["race_id"])
    entries, source, _ = _lineup_for(season, race["circuit_id"])
    if existing and not _improves(existing, source, entries):
        return
    weather = (forecast.race_weather(race["lat"], race["lon"], race["start_utc"]) or {}).get("preset", "dry")
    result, _ = _run_prediction(season, race["circuit_id"], weather, entries, source=source)
    ledger.record(race, result, source=source, trigger="auto", now=now)


def _improves(existing: dict, source: str, entries: list[dict]) -> bool:
    before = SOURCE_RANK.get(existing["grid_source"], 0)
    after = SOURCE_RANK.get(source, 0)
    if after != before:
        return after > before
    if source != "starting_grid":
        return False
    recorded = {e["driver_id"]: e["grid"] for e in existing["entries"]}
    return recorded != {e["driver_id"]: e["grid"] for e in entries}


def _entries_error(raw_entries: list, drivers: dict, teams: dict) -> str | None:
    seen = set()
    for i, e in enumerate(raw_entries, start=1):
        if not isinstance(e, dict):
            return f"entry {i} is not an object"
        driver_id = e.get("driver_id")
        if not isinstance(driver_id, str) or driver_id not in drivers:
            return f"entry {i}: unknown driver"
        if driver_id in seen:
            return f"entry {i}: driver listed twice"
        seen.add(driver_id)
        team = e.get("constructor_id")
        if team not in (None, "") and (not isinstance(team, str) or team not in teams):
            return f"entry {i}: unknown team"
        grid = e.get("grid")
        if grid not in (None, "") and not (_int_or_none(grid) and 1 <= _int_or_none(grid) <= MAX_ENTRIES):
            return f"entry {i}: grid must be 1-{MAX_ENTRIES}"
        position = e.get("quali_position")
        if position not in (None, "") and not (_int_or_none(position) and 1 <= _int_or_none(position) <= MAX_ENTRIES):
            return f"entry {i}: quali_position must be 1-{MAX_ENTRIES}"
        gap = e.get("quali_gap_pct")
        if gap not in (None, "") and (_float_or_none(gap) is None or not 0 <= _float_or_none(gap) <= 20):
            return f"entry {i}: quali_gap_pct must be 0-20"
    return None


def _float_or_none(value):
    try:
        number = None if value is None or value == "" else float(value)
    except (TypeError, ValueError):
        return None
    return number if number is None or math.isfinite(number) else None


def _int_or_none(value):
    try:
        return None if value is None or value == "" else int(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    predictor()
    start_background_sync()
    app.run(host="127.0.0.1", port=int(os.environ.get("F1_PORT", "5050")), debug=False)


if __name__ == "__main__":
    main()
