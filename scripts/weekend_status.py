from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("F1_AUTO_SYNC", "0")

import pandas as pd

from src import ledger, pipeline
from src.app import server
from src.config import PROCESSED_DIR, ROOT
from src.ingest import practice, schedule


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report what the automation has fetched and recorded for one race weekend."
    )
    parser.add_argument("--race", help="race id such as 2026_16 (default: the next race)")
    parser.add_argument("--record", action="store_true",
                        help="also write the ledger entry now if the grid has improved")
    args = parser.parse_args()

    now = schedule.now_utc()
    season = server.latest_season()
    calendar = server.calendar_for(season)
    race = (
        next((r for r in calendar if r["race_id"] == args.race), None)
        if args.race else schedule.next_race(calendar, now)
    )
    if race is None:
        raise SystemExit("no such race on the calendar")

    if args.record:
        server._auto_record(now)

    entries, source, _ = server._lineup_for(season, race["circuit_id"])
    cached = practice.CACHE_DIR / f"{race['race_id']}.json"
    weekend = json.loads(cached.read_text(encoding="utf-8")) if cached.exists() else None
    recorded = ledger.recorded(race["race_id"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv", usecols=["race_id"])
    card = next(
        (r for r in ledger.scorecard(server._df_results)["races"] if r["race_id"] == race["race_id"]),
        None,
    )

    report = {
        "now_utc": now.isoformat(),
        "race": {k: race.get(k) for k in ("race_id", "race_name", "circuit_id", "quali_utc", "start_utc", "status")},
        "sync": pipeline.last_state(),
        "sync_running": pipeline.is_running(),
        "sync_log_errors": _log_errors(),
        "practice_sessions": sorted(weekend["sessions"]) if weekend else [],
        "practice_rows_in_table": int((server._practice_table()["race_id"] == race["race_id"]).sum()),
        "grid": {
            "source": source,
            "top": [f"{e['grid']}. {e['driver_id']}" for e in entries[:6]],
            "cars": len(entries),
        },
        "ledger": None if recorded is None else {
            k: recorded.get(k) for k in ("recorded_at", "grid_source", "trigger", "weather", "trained_through")
        } | {"podium": [e["name"] for e in sorted(recorded["entries"], key=lambda e: e["expected_position"])[:3]]},
        "results_in": bool((results["race_id"] == race["race_id"]).any()),
        "scorecard": card,
        "app_processes": _app_processes(),
        "code_changed_utc": _code_mtime(),
    }
    print(json.dumps(report, indent=1, ensure_ascii=False, default=str))


def _log_errors(lines: int = 400) -> list[str]:
    if not pipeline.LOG_PATH.exists():
        return []
    tail = pipeline.LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]
    flags = ("Traceback", "Error", "failed", "exit ")
    return [line for line in tail if any(f in line for f in flags)][-15:]


def _app_processes() -> list[dict]:
    try:
        out = subprocess.run(["ps", "-axo", "pid=,lstart=,command="], capture_output=True, text=True).stdout
    except OSError:
        return []
    found = []
    for line in out.splitlines():
        if "run_app.py" in line or "src.app.server" in line or "gunicorn" in line:
            parts = line.split()
            started = pd.Timestamp(" ".join(parts[1:6])).tz_localize(datetime.now().astimezone().tzinfo)
            found.append({"pid": int(parts[0]), "started_utc": started.tz_convert("UTC").isoformat(),
                          "command": " ".join(parts[6:])[:120]})
    return found


def _code_mtime() -> str:
    newest = max(p.stat().st_mtime for p in (ROOT / "src").rglob("*.py"))
    return pd.Timestamp(newest, unit="s", tz="UTC").isoformat()


if __name__ == "__main__":
    main()
