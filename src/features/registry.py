from __future__ import annotations

import json

import pandas as pd

from src.config import PODIUM_CUTOFF
from src.ingest.tables import retirement_split

RECENT_SEASONS = 3


def build_drivers(results: pd.DataFrame, current_season: int) -> dict[str, dict]:
    out: dict[str, dict] = {}
    recent_cutoff = current_season - RECENT_SEASONS + 1

    for driver_id, grp in results.groupby("driver_id"):
        grp = grp.sort_values(["season", "round"])
        last = grp.iloc[-1]
        classified = grp[grp["classified"]]
        recent = grp[grp["season"] >= recent_cutoff]
        season_now = grp[grp["season"] == current_season]

        out[driver_id] = {
            "driver_id": driver_id,
            "name": last["driver_name"],
            "code": None if pd.isna(last.get("driver_code")) else last.get("driver_code"),
            "dob": None if pd.isna(last.get("driver_dob")) else str(last.get("driver_dob"))[:10],
            "team": last["constructor_id"],
            "team_name": last["constructor_name"],
            "first_season": int(grp["season"].min()),
            "last_season": int(grp["season"].max()),
            "active": bool(last["season"] >= current_season - 1),
            "career": {
                "races": int(len(grp)),
                "wins": int((classified["position"] == 1).sum()),
                "podiums": int((classified["position"] <= PODIUM_CUTOFF).sum()),
                "points": round(float(grp["points"].sum()), 1),
                "poles": int((grp["grid"] == 1).sum()),
                "avg_finish": _round(classified["position"].mean()),
                "dnf_rate": _round((~grp["finished"]).mean()),
            },
            "recent": {
                "seasons": f"{recent_cutoff}-{current_season}",
                "races": int(len(recent)),
                "avg_grid": _round(recent["grid"].mean()),
                "avg_finish": _round(recent[recent["classified"]]["position"].mean()),
                "podium_rate": _round((recent["classified"] & (recent["position"] <= PODIUM_CUTOFF)).mean()),
                "dnf_rate": _round((~recent["finished"]).mean()),
                **{k: _round(v) for k, v in retirement_split(recent, causes=grp).items()
                   if k != "dnf_rate"},
            },
            "season": {
                "races": int(len(season_now)),
                "points": round(float(season_now["points"].sum()), 1),
                "podiums": int((season_now["classified"] & (season_now["position"] <= PODIUM_CUTOFF)).sum()),
                "best_finish": _int(season_now[season_now["classified"]]["position"].min()),
            },
        }
    return out


def build_driver_track_history(
    results: pd.DataFrame, current_season: int, active_only: bool = True
) -> dict[str, dict[str, dict]]:
    df = results
    if active_only:
        active = (
            results.groupby("driver_id")["season"].max()
            >= current_season - RECENT_SEASONS
        )
        df = results[results["driver_id"].isin(active[active].index)]

    history: dict[str, dict[str, dict]] = {}
    for (driver_id, circuit_id), grp in df.groupby(["driver_id", "circuit_id"]):
        classified = grp[grp["classified"]]
        history.setdefault(driver_id, {})[circuit_id] = {
            "races": int(len(grp)),
            "best": _int(classified["position"].min()),
            "avg": _round(classified["position"].mean(), 1),
            "podiums": int((classified["position"] <= PODIUM_CUTOFF).sum()),
            "wins": int((classified["position"] == 1).sum()),
            "dnfs": int((~grp["finished"]).sum()),
            "incidents": int((grp["outcome"] == "incident").sum()),
            "dsqs": int((grp["outcome"] == "excluded").sum()),
            "avg_grid": _round(grp["grid"].mean(), 1),
            "last_season": int(grp["season"].max()),
            "last_result": _int(grp.sort_values("season").iloc[-1]["position"]),
        }
    return history


def build_teams(results: pd.DataFrame, current_season: int) -> dict[str, dict]:
    out: dict[str, dict] = {}
    recent_cutoff = current_season - RECENT_SEASONS + 1

    for constructor_id, grp in results.groupby("constructor_id"):
        classified = grp[grp["classified"]]
        recent = grp[grp["season"] >= recent_cutoff]
        season_now = grp[grp["season"] == current_season]
        out[constructor_id] = {
            "constructor_id": constructor_id,
            "name": grp.iloc[-1]["constructor_name"],
            "active": bool(grp["season"].max() >= current_season - 1),
            "first_season": int(grp["season"].min()),
            "last_season": int(grp["season"].max()),
            "career": {
                "entries": int(len(grp)),
                "wins": int((classified["position"] == 1).sum()),
                "podiums": int((classified["position"] <= PODIUM_CUTOFF).sum()),
            },
            "recent": {
                "avg_finish": _round(recent[recent["classified"]]["position"].mean()),
                "podium_rate": _round((recent["classified"] & (recent["position"] <= PODIUM_CUTOFF)).mean()),
                "dnf_rate": _round((~recent["finished"]).mean()),
                "avg_grid": _round(recent["grid"].mean()),
            },
            "season": {
                "points": round(float(season_now["points"].sum()), 1),
                "podiums": int((season_now["classified"] & (season_now["position"] <= PODIUM_CUTOFF)).sum()),
                "drivers": sorted(season_now["driver_id"].unique().tolist()),
            },
        }
    return out


def save(obj, path) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _round(value, digits: int = 3):
    return None if value is None or pd.isna(value) else round(float(value), digits)


def _int(value):
    return None if value is None or pd.isna(value) else int(value)
