from __future__ import annotations

import re

import pandas as pd

LAP_STATUS = re.compile(r"^\+\d+ Laps?$")
TIME_RE = re.compile(r"^(?:(\d+):)?(\d+)\.(\d+)$")


def race_id(season, rnd) -> str:
    return f"{int(season)}_{int(rnd):02d}"


def parse_lap_time(value: str | None) -> float | None:
    if not value:
        return None
    m = TIME_RE.match(value.strip())
    if not m:
        return None
    minutes, seconds, frac = m.groups()
    return int(minutes or 0) * 60 + int(seconds) + float(f"0.{frac}")


def classify_status(status: str) -> str:
    if status == "Finished" or status == "Lapped" or LAP_STATUS.match(status):
        return "finished"
    if status in {"Disqualified", "Excluded", "Did not qualify", "Did not prequalify", "Withdrew"}:
        return "excluded"
    if status in {"Accident", "Collision", "Collision damage", "Spun off", "Damage", "Puncture"}:
        return "incident"
    if status in {"Retired", "Did not start"}:
        return "unknown"
    return "mechanical"


def retirement_split(
    frame: pd.DataFrame, causes: pd.DataFrame | None = None
) -> dict[str, float]:
    n = len(frame)
    if not n:
        return {"dnf_rate": None, "incident_rate": None, "mechanical_rate": None, "dsq_rate": None}

    outcome = frame["outcome"]
    dnf = float((~frame["finished"]).mean())
    dsq = float((outcome == "excluded").mean())

    cause_outcome = outcome if causes is None else causes["outcome"]
    incidents = int((cause_outcome == "incident").sum())
    mechanical = int((cause_outcome == "mechanical").sum())
    known = incidents + mechanical
    if known == 0:
        return {"dnf_rate": dnf, "incident_rate": None, "mechanical_rate": None, "dsq_rate": dsq}

    share = incidents / known
    attributable = dnf - dsq
    return {
        "dnf_rate": dnf,
        "incident_rate": attributable * share,
        "mechanical_rate": attributable * (1 - share),
        "dsq_rate": dsq,
    }


def build_races(raw_by_season: dict[int, list[dict]]) -> pd.DataFrame:
    rows = []
    for season, races in raw_by_season.items():
        for r in races:
            circuit = r["Circuit"]
            loc = circuit["Location"]
            rows.append(
                {
                    "race_id": race_id(r["season"], r["round"]),
                    "season": int(r["season"]),
                    "round": int(r["round"]),
                    "race_name": r["raceName"],
                    "date": r["date"],
                    "start_utc": _utc(r.get("date"), r.get("time")),
                    "quali_utc": _utc(
                        (r.get("Qualifying") or {}).get("date"),
                        (r.get("Qualifying") or {}).get("time"),
                    ),
                    "circuit_id": circuit["circuitId"],
                    "circuit_name": circuit["circuitName"],
                    "country": loc["country"],
                    "locality": loc["locality"],
                    "lat": float(loc["lat"]),
                    "lon": float(loc["long"]),
                }
            )
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["season", "round"]).reset_index(drop=True)


def build_results(raw_by_season: dict[int, list[dict]]) -> pd.DataFrame:
    rows = []
    for season, races in raw_by_season.items():
        for r in races:
            rid = race_id(r["season"], r["round"])
            for res in r.get("Results", []):
                status = res["status"]
                outcome = classify_status(status)
                pos_text = res["positionText"]
                rows.append(
                    {
                        "race_id": rid,
                        "season": int(r["season"]),
                        "round": int(r["round"]),
                        "date": r["date"],
                        "circuit_id": r["Circuit"]["circuitId"],
                        "driver_id": res["Driver"]["driverId"],
                        "driver_name": f"{res['Driver']['givenName']} {res['Driver']['familyName']}",
                        "driver_code": res["Driver"].get("code"),
                        "driver_dob": res["Driver"].get("dateOfBirth"),
                        "constructor_id": res["Constructor"]["constructorId"],
                        "constructor_name": res["Constructor"]["name"],
                        "grid": int(res["grid"]),
                        "position": int(res["position"]),
                        "position_text": pos_text,
                        "classified": pos_text.isdigit(),
                        "points": float(res["points"]),
                        "laps": int(res["laps"]),
                        "status": status,
                        "outcome": outcome,
                        "time_millis": _int_or_none(res.get("Time", {}).get("millis")),
                        "finished": outcome == "finished",
                        "fastest_lap_rank": _int_or_none(
                            res.get("FastestLap", {}).get("rank")
                        ),
                    }
                )
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    field = df.groupby("race_id")["grid"].transform("max")
    df["pit_lane_start"] = df["grid"] == 0
    df.loc[df["grid"] == 0, "grid"] = field + 1
    return df.sort_values(["season", "round", "position"]).reset_index(drop=True)


def build_qualifying(raw_by_season: dict[int, list[dict]]) -> pd.DataFrame:
    rows = []
    for season, races in raw_by_season.items():
        for r in races:
            rid = race_id(r["season"], r["round"])
            for q in r.get("QualifyingResults", []):
                times = [parse_lap_time(q.get(k)) for k in ("Q1", "Q2", "Q3")]
                valid = [t for t in times if t]
                rows.append(
                    {
                        "race_id": rid,
                        "season": int(r["season"]),
                        "round": int(r["round"]),
                        "driver_id": q["Driver"]["driverId"],
                        "constructor_id": q["Constructor"]["constructorId"],
                        "quali_position": int(q["position"]),
                        "q1": times[0],
                        "q2": times[1],
                        "q3": times[2],
                        "quali_best": min(valid) if valid else None,
                    }
                )
    if not rows:
        return pd.DataFrame(
            columns=["race_id", "season", "round", "driver_id", "constructor_id",
                     "quali_position", "q1", "q2", "q3", "quali_best", "quali_gap_pct"]
        )
    df = pd.DataFrame(rows)
    pole = df.groupby("race_id")["quali_best"].transform("min")
    df["quali_gap_pct"] = (df["quali_best"] - pole) / pole * 100.0
    return df.sort_values(["season", "round", "quali_position"]).reset_index(drop=True)


def build_sprint(raw_by_season: dict[int, list[dict]]) -> pd.DataFrame:
    rows = []
    for season, races in raw_by_season.items():
        for r in races:
            rid = race_id(r["season"], r["round"])
            for s in r.get("SprintResults", []):
                rows.append(
                    {
                        "race_id": rid,
                        "season": int(r["season"]),
                        "round": int(r["round"]),
                        "driver_id": s["Driver"]["driverId"],
                        "constructor_id": s["Constructor"]["constructorId"],
                        "sprint_position": int(s["position"]),
                        "sprint_grid": int(s["grid"]),
                        "sprint_points": float(s["points"]),
                    }
                )
    if not rows:
        return pd.DataFrame(
            columns=["race_id", "season", "round", "driver_id", "constructor_id",
                     "sprint_position", "sprint_grid", "sprint_points"]
        )
    return pd.DataFrame(rows)


def _utc(day: str | None, time: str | None) -> str | None:
    if not day or not time:
        return None
    return f"{day}T{time}"


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
