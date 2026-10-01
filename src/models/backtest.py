from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache

import joblib
import pandas as pd

from src.config import MODEL_DIR, PROCESSED_DIR
from src.features import registry
from src.features.build import build_dataset
from src.features.weather import estimate_wet_index
from src.ingest import weather_history
from src.models import grid_prior
from src.models import train as T

HEADS_DIR = MODEL_DIR / "backtest"


def clear() -> None:
    _tables.cache_clear()
    _features.cache_clear()
    heads_before.cache_clear()
    state_before.cache_clear()


@lru_cache(maxsize=1)
def _tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, dict]:
    races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv", parse_dates=["date"])
    quali = pd.read_csv(PROCESSED_DIR / "qualifying.csv")
    wet = weather_history.load()
    if wet.empty:
        wet = estimate_wet_index(results)
    catalogue = json.loads((PROCESSED_DIR / "circuit_catalogue.json").read_text(encoding="utf-8"))
    return races, results, quali, wet, catalogue


@lru_cache(maxsize=1)
def _features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["date"])


@lru_cache(maxsize=4)
def heads_before(season: int) -> dict:
    source = PROCESSED_DIR / "features.csv"
    stat = source.stat()
    key = hashlib.sha1(
        f"{stat.st_mtime_ns}:{stat.st_size}:{','.join(T.FEATURES)}".encode()
    ).hexdigest()[:12]
    path = HEADS_DIR / f"heads_{season}_{key}.joblib"
    if path.exists():
        try:
            return joblib.load(path)
        except Exception:
            path.unlink(missing_ok=True)

    dataset = _features()
    train = dataset[dataset["season"] < season]
    heads = {
        "models": T.fit_all_heads(train),
        "grid_priors": {t: grid_prior.build_prior(train, t) for t in T.TARGETS},
        "trained_through": str(train["date"].max().date()),
        "features": list(T.FEATURES),
    }
    HEADS_DIR.mkdir(parents=True, exist_ok=True)
    for stale in HEADS_DIR.glob(f"heads_{season}_*.joblib"):
        stale.unlink(missing_ok=True)
    tmp = path.with_suffix(".tmp")
    joblib.dump(heads, tmp, compress=3)
    os.replace(tmp, path)
    return heads


@lru_cache(maxsize=16)
def state_before(race_id: str) -> dict:
    races, results, quali, wet, catalogue = _tables()
    race_date = races.loc[races["race_id"] == race_id, "date"].iloc[0]
    season = int(race_date.year)
    before = results[results["date"] < race_date]
    _, store = build_dataset(before, quali, races, catalogue, wet_index=wet)
    actual = results[results["race_id"] == race_id]
    return {
        "store": store,
        "drivers": registry.build_drivers(before, season),
        "teams": registry.build_teams(before, season),
        "track_history": registry.build_driver_track_history(before, season),
        "actual": {
            r.driver_id: {"position": int(r.position), "classified": bool(r.classified),
                          "status": r.status}
            for r in actual.itertuples(index=False)
        },
    }


def context(race: dict) -> dict:
    return {**heads_before(int(race["season"])), **state_before(race["race_id"])}
