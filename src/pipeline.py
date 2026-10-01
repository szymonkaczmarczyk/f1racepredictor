from __future__ import annotations

import fcntl
import json
import subprocess
import sys
import time
from contextlib import contextmanager

import joblib
import pandas as pd

from src.config import CURRENT_SEASON, DATA_DIR, MODEL_DIR, PROCESSED_DIR, ROOT

LOCK_PATH = DATA_DIR / ".sync.lock"
STATE_PATH = DATA_DIR / "sync_state.json"
LOG_PATH = DATA_DIR / "sync.log"


class SyncBusy(RuntimeError):
    pass


class SyncFailed(RuntimeError):
    pass


def run(*, full_validation: bool = False) -> dict:
    with _lock():
        started = time.time()
        before = _results_summary()

        _step("01_fetch_data.py")
        _step("01b_fetch_pitstops.py", "--from-season", str(CURRENT_SEASON))
        _step("01c_fetch_practice.py", "--from-season", str(CURRENT_SEASON), "--refresh-upcoming")
        _step("01d_fetch_race_laps.py", "--from-season", str(CURRENT_SEASON))
        _step("01e_fetch_track_status.py", "--from-season", str(CURRENT_SEASON))
        _step("02_build_features.py")

        after = _results_summary()
        trained = _trained_through()
        retrain = "none"
        if full_validation:
            _step("03_train.py")
            retrain = "full"
        elif trained is None or (after["last_date"] and after["last_date"] > trained):
            _step("03_train.py", "--quick")
            retrain = "quick"

        state = {
            "last_success_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "seconds": round(time.time() - started, 1),
            "new_races": after["races"] - before["races"],
            "results_through": after["last_race"],
            "retrain": retrain,
            "trained_through": _trained_through(),
        }
        STATE_PATH.write_text(json.dumps(state, indent=1), encoding="utf-8")
        return state


def last_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def is_running() -> bool:
    try:
        with open(LOCK_PATH, "a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(handle, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True


@contextmanager
def _lock():
    handle = open(LOCK_PATH, "a")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise SyncBusy("a sync is already running")
    try:
        yield
    finally:
        fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()


def _step(script: str, *args: str) -> None:
    command = [sys.executable, str(ROOT / "scripts" / script), *args]
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"\n=== {pd.Timestamp.now(tz='UTC').isoformat()} {script} {' '.join(args)}\n")
        log.flush()
        done = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    if done.returncode != 0:
        raise SyncFailed(f"{script} failed (exit {done.returncode}); see {LOG_PATH.name}")


def _results_summary() -> dict:
    path = PROCESSED_DIR / "results.csv"
    if not path.exists():
        return {"races": 0, "last_race": None, "last_date": None}
    results = pd.read_csv(path, usecols=["race_id", "date"], parse_dates=["date"])
    return {
        "races": int(results["race_id"].nunique()),
        "last_race": str(results["race_id"].max()),
        "last_date": str(results["date"].max().date()),
    }


def _trained_through() -> str | None:
    path = MODEL_DIR / "podium_model.joblib"
    if not path.exists():
        return None
    return joblib.load(path).get("trained_through")
