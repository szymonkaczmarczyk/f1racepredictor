from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from src.config import DATA_DIR, PODIUM_CUTOFF

LEDGER_DIR = DATA_DIR / "ledger"
MAX_HISTORY = 30


def record(race: dict, result: dict, *, source: str, trigger: str, now: pd.Timestamp) -> bool:
    if now >= pd.Timestamp(race["start_utc"]):
        return False
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "race_id": race["race_id"],
        "season": race["season"],
        "round": race["round"],
        "race_name": race["race_name"],
        "start_utc": race["start_utc"],
        "recorded_at": now.isoformat(),
        "grid_source": source,
        "trigger": trigger,
        "weather": (result.get("conditions") or {}).get("weather"),
        "trained_through": (result.get("model") or {}).get("trained_through"),
        "entries": [
            {
                "driver_id": e["driver_id"],
                "name": e["name"],
                "grid": e["grid"],
                "expected_position": e["expected_position"],
                "p_win": e["p_win"],
                "p_podium": e["p_podium"],
                "p_points": e["p_points"],
            }
            for e in result["entries"]
        ],
    }
    previous = recorded(race["race_id"])
    history = []
    if previous:
        history = previous.pop("history", [])
        if previous["grid_source"] != source or _podium(previous) != _podium(payload):
            history.append(previous)
    payload["history"] = history[-MAX_HISTORY:]
    path = LEDGER_DIR / f"{race['race_id']}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    return True


def recorded(race_id: str) -> dict | None:
    path = LEDGER_DIR / f"{race_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def scorecard(results: pd.DataFrame) -> dict:
    races = []
    for path in sorted(LEDGER_DIR.glob("*.json")) if LEDGER_DIR.exists() else []:
        entry = json.loads(path.read_text(encoding="utf-8"))
        actual = results[results["race_id"] == entry["race_id"]]
        versions = [*entry.get("history", []), entry]
        row = {
            "race_id": entry["race_id"],
            "race_name": entry["race_name"],
            "recorded_at": entry["recorded_at"],
            "grid_source": entry["grid_source"],
            "predicted_podium": _podium_names(entry),
        }
        if actual.empty:
            row["status"] = "pending"
            row["stages"] = [_stage(v) for v in versions]
            races.append(row)
            continue
        on_podium = actual[actual["classified"] & (actual["position"] <= PODIUM_CUTOFF)]
        podium_ids = set(on_podium["driver_id"])
        winner = actual.loc[actual["position"] == 1, "driver_id"]
        winner_id = winner.iloc[0] if len(winner) else None
        row.update({
            "status": "scored",
            "actual_podium": on_podium.sort_values("position")["driver_name"].tolist(),
            **_score(entry, podium_ids, winner_id),
            "grid_podium_hits": len(
                set(actual.sort_values("grid").head(PODIUM_CUTOFF)["driver_id"]) & podium_ids
            ),
            "stages": [{**_stage(v), **_score(v, podium_ids, winner_id)} for v in versions],
        })
        races.append(row)

    scored = [r for r in races if r["status"] == "scored"]
    summary = {"races": len(scored)}
    if scored:
        summary.update({
            "podium_hit_rate": sum(r["podium_hits"] for r in scored) / (PODIUM_CUTOFF * len(scored)),
            "grid_podium_hit_rate": sum(r["grid_podium_hits"] for r in scored) / (PODIUM_CUTOFF * len(scored)),
            "winner_hit_rate": sum(r["winner_hit"] for r in scored) / len(scored),
            "podium_brier": float(np.mean([r["podium_brier"] for r in scored])),
            "by_source": _by_source(scored),
        })
    return {"summary": summary, "races": races[::-1]}


def _podium(entry: dict) -> list[str]:
    ordered = sorted(entry["entries"], key=lambda e: e["expected_position"])
    return [e["driver_id"] for e in ordered[:PODIUM_CUTOFF]]


def _podium_names(entry: dict) -> list[str]:
    ordered = sorted(entry["entries"], key=lambda e: e["expected_position"])
    return [e["name"] for e in ordered[:PODIUM_CUTOFF]]


def _stage(entry: dict) -> dict:
    return {
        "recorded_at": entry["recorded_at"],
        "grid_source": entry["grid_source"],
        "trigger": entry.get("trigger"),
        "predicted_podium": _podium_names(entry),
    }


def _score(entry: dict, podium_ids: set, winner_id: str | None) -> dict:
    top = _podium(entry)
    probs = {e["driver_id"]: e["p_podium"] for e in entry["entries"]}
    y = np.array([float(d in podium_ids) for d in probs])
    p = np.clip(np.array(list(probs.values()), dtype=float), 1e-6, 1 - 1e-6)
    return {
        "podium_hits": len(set(top) & podium_ids),
        "winner_hit": bool(winner_id is not None and top and top[0] == winner_id),
        "podium_brier": float(np.mean((p - y) ** 2)),
    }


def _by_source(scored: list[dict]) -> dict:
    latest: dict[str, list[dict]] = {}
    for race in scored:
        final = {}
        for stage in race["stages"]:
            final[stage["grid_source"]] = stage
        for source, stage in final.items():
            latest.setdefault(source, []).append(stage)
    return {
        source: {
            "races": len(stages),
            "podium_hit_rate": sum(s["podium_hits"] for s in stages) / (PODIUM_CUTOFF * len(stages)),
            "winner_hit_rate": sum(s["winner_hit"] for s in stages) / len(stages),
            "podium_brier": float(np.mean([s["podium_brier"] for s in stages])),
        }
        for source, stages in latest.items()
    }
