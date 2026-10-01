from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src.ingest.circuits import STREET_CIRCUITS
from src.ingest.tables import retirement_split

DEGRADATION_YEARS = 3


def _scale_1_10(series: pd.Series) -> pd.Series:
    if series.notna().sum() < 2:
        return pd.Series(5.0, index=series.index)
    ranks = series.rank(pct=True)
    return (1 + ranks * 9).round(0).clip(1, 10)


def build_catalogue(
    races: pd.DataFrame,
    results: pd.DataFrame,
    geometry: dict[str, dict],
    raw_geojson: dict[str, dict],
    pitstops: pd.DataFrame | None = None,
    recent_years: int = 12,
    always_include: set[str] | None = None,
    degradation: pd.DataFrame | None = None,
    track_status: pd.DataFrame | None = None,
) -> dict[str, dict]:
    latest_season = int(races["season"].max())
    cutoff = latest_season - recent_years
    always_include = always_include or set()

    recent = results[results["season"] >= cutoff]
    per_circuit = {}

    for cid, grp in recent.groupby("circuit_id"):
        starts = len(grp)
        if starts < 20:
            continue
        gain = grp["grid"] - grp["position"]
        top3_grid = grp[grp["grid"] <= 3]
        pole = grp[grp["grid"] == 1]
        per_circuit[cid] = {
            "volatility": float(gain.abs().mean()),
            "dnf_rate": float((~grp["finished"]).mean()),
            "incident_rate": retirement_split(grp)["incident_rate"],
            "grid_stickiness": float((top3_grid["position"] <= 3).mean()) if len(top3_grid) else np.nan,
            "pole_win_rate": float((pole["position"] == 1).mean()) if len(pole) else np.nan,
            "overtakes_per_race": float(gain[gain > 0].sum() / grp["race_id"].nunique()),
            "starts": starts,
        }

    for cid in always_include:
        if cid not in per_circuit and cid in geometry:
            per_circuit[cid] = {}

    stats = pd.DataFrame(per_circuit).T
    if stats.empty:
        return {}
    for col in ("volatility", "dnf_rate", "incident_rate", "grid_stickiness",
                "pole_win_rate", "overtakes_per_race", "starts"):
        if col not in stats.columns:
            stats[col] = np.nan

    lengths, corners_map = {}, {}
    for cid, geo in raw_geojson.items():
        feature = next(
            (f for f in geo.get("features", []) if f["geometry"]["type"] == "LineString"),
            None,
        )
        if not feature:
            continue
        lengths[cid] = feature["properties"].get("length")
        corners_map[cid] = len(geometry.get(cid, {}).get("corners") or []) or None

    stats["length_m"] = pd.Series(lengths)
    stats["corners"] = pd.Series(corners_map)
    stats["corner_density"] = stats["corners"] / (stats["length_m"] / 1000.0)
    stats["is_street"] = [float(cid in STREET_CIRCUITS) for cid in stats.index]

    winners = recent[recent["position"] == 1]
    stats["laps"] = (
        winners.groupby("circuit_id")["laps"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.median())
        .reindex(stats.index)
    )
    debut = stats["laps"].isna() & stats["length_m"].notna()
    stats.loc[debut, "laps"] = np.ceil(305_000 / stats.loc[debut, "length_m"])
    stats["distance_km"] = (stats["laps"] * stats["length_m"] / 1000.0).round(0)

    difficulty = (
        0.40 * _z(stats["corner_density"])
        + 0.32 * _z(stats["incident_rate"])
        + 0.28 * stats["is_street"]
    )
    stats["track_difficulty"] = _scale_1_10(difficulty)

    stats["deg_window"] = None
    deg_raw = pd.Series(np.nan, index=stats.index)
    if pitstops is not None and not pitstops.empty:
        stops = pitstops.merge(races[["race_id", "circuit_id"]], on="race_id", how="left")
        deg_cutoff = int(stops["season"].max()) - DEGRADATION_YEARS + 1
        stops = stops[stops["season"] >= deg_cutoff]
        per_car = stops.groupby(["circuit_id", "race_id", "driver_id"]).size()
        stats["stops_per_car"] = per_car.groupby("circuit_id").mean().reindex(stats.index)
        distance = stats["distance_km"].replace(0, np.nan)
        by_stops = stats["stops_per_car"] / (distance / 100.0)
        if by_stops.notna().sum() >= 5:
            deg_raw = by_stops.rank(pct=True)
            window = f"{deg_cutoff}-{int(pitstops['season'].max())}"
            stats.loc[by_stops.notna(), "deg_window"] = f"pit stops {window}"
    else:
        stats["stops_per_car"] = np.nan

    if degradation is not None and not degradation.empty:
        lap_cutoff = int(degradation["season"].max()) - DEGRADATION_YEARS + 1
        recent = degradation[degradation["season"] >= lap_cutoff]
        stats["deg_pct_per_lap"] = (
            recent.groupby("circuit_id")["deg_pct_per_lap"].median().reindex(stats.index)
        )
    else:
        stats["deg_pct_per_lap"] = np.nan

    if track_status is not None and not track_status.empty:
        status = track_status.merge(races[["race_id", "circuit_id"]], on="race_id", how="inner")
        stopped = (status["safety_cars"] + status["red_flags"]) > 0
        stats["sc_rate"] = stopped.groupby(status["circuit_id"]).mean().reindex(stats.index)
        stats["sc_races"] = status.groupby("circuit_id").size().reindex(stats.index)
    else:
        stats["sc_rate"] = np.nan
        stats["sc_races"] = np.nan

    if deg_raw.notna().sum() < 5:
        deg_raw = 0.55 * _z(stats["corner_density"]) + 0.45 * _z(stats["length_m"])
        stats["deg_window"] = "estimated from layout"
    stats["tyre_degradation"] = _scale_1_10(deg_raw)

    names = (
        races.drop_duplicates("circuit_id")
        .set_index("circuit_id")[["circuit_name", "country", "locality", "race_name"]]
    )
    last_seen = races.groupby("circuit_id")["season"].max()

    catalogue: dict[str, dict] = {}
    for cid, row in stats.iterrows():
        meta = names.loc[cid].to_dict() if cid in names.index else {}
        entry = {
            "circuit_id": cid,
            "name": meta.get("circuit_name", cid),
            "race_name": meta.get("race_name"),
            "country": meta.get("country"),
            "locality": meta.get("locality"),
            "last_season": int(last_seen.get(cid, 0)),
            "corners": _int(row.get("corners")),
            "length_m": _int(row.get("length_m")),
            "laps": _int(row.get("laps")),
            "distance_km": _int(row.get("distance_km")),
            "track_difficulty": _int(row.get("track_difficulty")) or 5,
            "tyre_degradation": _int(row.get("tyre_degradation")) or 5,
            "is_street": bool(row.get("is_street")),
            "debut": bool(pd.isna(row.get("starts"))),
            "stats": {
                "volatility": _round(row.get("volatility")),
                "dnf_rate": _round(row.get("dnf_rate")),
                "deg_window": row.get("deg_window"),
                "incident_rate": _round(row.get("incident_rate")),
                "grid_stickiness": _round(row.get("grid_stickiness")),
                "pole_win_rate": _round(row.get("pole_win_rate")),
                "overtakes_per_race": _round(row.get("overtakes_per_race"), 1),
                "stops_per_car": _round(row.get("stops_per_car"), 2),
                "deg_pct_per_lap": _round(row.get("deg_pct_per_lap"), 4),
                "starts": _int(row.get("starts")),
                "sc_rate": _round(row.get("sc_rate")),
                "sc_races": _int(row.get("sc_races")),
            },
        }
        if cid in geometry:
            entry["geometry"] = geometry[cid]
        catalogue[cid] = entry

    return catalogue


def _z(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    std = s.std()
    if not std or np.isnan(std):
        return pd.Series(0.0, index=series.index)
    return ((s - s.mean()) / std).fillna(0.0)


def _int(value):
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _round(value, digits: int = 3):
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return None
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def save(catalogue: dict, path) -> None:
    path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=1), encoding="utf-8")
