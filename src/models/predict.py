from __future__ import annotations

import json
from dataclasses import dataclass, field

import joblib
import numpy as np
import pandas as pd

from src.config import MODEL_DIR, PROCESSED_DIR
from src.features.build import FEATURES, add_race_relative_features, with_practice, year_fraction
from src.features.weather import WEATHER_PRESETS
from src.models import grid_prior
from src.models.simulate import simulate_race


@dataclass
class Entry:
    driver_id: str
    constructor_id: str
    grid: int
    quali_gap_pct: float | None = None
    quali_position: int | None = None


@dataclass
class Conditions:
    circuit_id: str
    weather: str = "dry"
    tyre_degradation: float | None = None
    track_difficulty: float | None = None
    laps: int | None = None
    distance_km: float | None = None
    season: int | None = None
    round_norm: float = 0.5
    date: pd.Timestamp | None = None
    practice: pd.DataFrame | None = None
    extras: dict = field(default_factory=dict)


class Predictor:
    def __init__(self, bundle: dict, store, catalogue: dict, drivers: dict, teams: dict,
                 track_history: dict, report: dict | None = None):
        self.models = bundle["models"]
        self.features = list(bundle.get("features") or FEATURES)
        self.grid_priors = bundle.get("grid_priors", {})
        self.blend_weights = bundle.get("blend_weights", {})
        self.prequali = bundle.get("prequali")
        self.trained_through = bundle.get("trained_through")
        self.seasons = bundle.get("seasons")
        self.store = store
        self.catalogue = catalogue
        self.drivers = drivers
        self.teams = teams
        self.track_history = track_history
        self.report = report or {}
        self._incident_baseline: float | None = None

    @classmethod
    def load(cls) -> "Predictor":
        bundle = joblib.load(MODEL_DIR / "podium_model.joblib")
        store = joblib.load(MODEL_DIR / "feature_store.joblib")
        read = lambda name: json.loads((PROCESSED_DIR / name).read_text(encoding="utf-8"))
        report_path = MODEL_DIR / "validation_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        return cls(
            bundle,
            store,
            read("circuit_catalogue.json"),
            read("drivers.json"),
            read("teams.json"),
            read("driver_track_history.json"),
            report,
        )

    def build_frame(self, entries: list[Entry], conditions: Conditions) -> pd.DataFrame:
        track = self.catalogue.get(conditions.circuit_id, {})
        wet = WEATHER_PRESETS.get(conditions.weather, 0.0)
        season = conditions.season or (self.seasons[1] if self.seasons else 2026)
        field_size = max(len(entries), 2)
        laps = conditions.laps or track.get("laps")
        distance = conditions.distance_km or track.get("distance_km")
        deg = wet_adjusted_degradation(
            _pick(conditions.tyre_degradation, track.get("tyre_degradation")), wet
        )
        difficulty = _pick(conditions.track_difficulty, track.get("track_difficulty"))
        date = conditions.date if conditions.date is not None else pd.Timestamp(f"{season}-07-01")

        self.store.start_season(season)
        rows = []
        for entry in entries:
            feats = self.store.entry_features(
                driver_id=entry.driver_id,
                constructor_id=entry.constructor_id,
                circuit_id=conditions.circuit_id,
                season=season,
                year_frac=year_fraction(date),
                date=date,
                grid=int(entry.grid),
                field_size=field_size,
                round_norm=conditions.round_norm,
                quali_position=float(entry.quali_position or entry.grid),
                quali_gap_pct=entry.quali_gap_pct,
                reached_q3=1.0 if (entry.quali_position or entry.grid) <= 10 else 0.0,
                pit_lane_start=False,
                laps=float(laps) if laps else None,
                distance_km=float(distance) if distance else None,
                tyre_degradation=deg,
                track_difficulty=difficulty,
                is_wet=wet,
            )
            feats["driver_id"] = entry.driver_id
            feats["constructor_id"] = entry.constructor_id
            rows.append(feats)

        frame = add_race_relative_features(with_practice(pd.DataFrame(rows), conditions.practice))
        for col in dict.fromkeys([*FEATURES, *self.features]):
            if col not in frame.columns:
                frame[col] = np.nan
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
        return frame

    def reliability_rates(self, entries: list[Entry], frame: pd.DataFrame) -> np.ndarray:
        decayed = _column(frame, "team_form_dnf_rate")
        out = []
        for i, entry in enumerate(entries):
            measured = (
                (self.teams.get(entry.constructor_id, {}) or {}).get("recent", {}) or {}
            ).get("dnf_rate")
            fast = None if decayed is None else decayed[i]
            values = [v for v in (fast, measured) if v is not None and np.isfinite(v)]
            out.append(float(np.mean(values)) if values else np.nan)
        return np.array(out, dtype=float)


    def crash_rates(self, entries: list[Entry], circuit_id: str) -> np.ndarray:
        circuit_factor = _ratio(
            self.catalogue.get(circuit_id, {}).get("stats", {}).get("incident_rate"),
            self._field_incident_rate(),
        )

        rates = []
        for entry in entries:
            driver = self.drivers.get(entry.driver_id, {})
            recent = driver.get("recent", {}) or {}
            base = recent.get("incident_rate")
            base = FIELD_INCIDENT_RATE if base is None else float(base)
            base = _shrink(base, recent.get("races", 0), FIELD_INCIDENT_RATE, CRASH_PRIOR_RACES)

            here = self.track_history.get(entry.driver_id, {}).get(circuit_id) or {}
            starts = int(here.get("races", 0) or 0)
            if starts:
                seen = float(here.get("incidents", 0) or 0) / starts
                here_factor = _ratio(
                    _shrink(seen, starts, FIELD_INCIDENT_RATE, CRASH_PRIOR_RACES),
                    FIELD_INCIDENT_RATE,
                )
            else:
                here_factor = 1.0

            rates.append(base * circuit_factor * here_factor)
        return np.clip(np.array(rates, dtype=float), 0.005, 0.35)

    def dsq_rates(self, entries: list[Entry]) -> np.ndarray:
        out = []
        for entry in entries:
            recent = (self.drivers.get(entry.driver_id, {}) or {}).get("recent", {}) or {}
            seen = recent.get("dsq_rate")
            seen = FIELD_DSQ_RATE if seen is None else float(seen)
            out.append(_shrink(seen, recent.get("races", 0), FIELD_DSQ_RATE, DSQ_PRIOR_RACES))
        return np.clip(np.array(out, dtype=float), 0.0, 0.05)

    def _field_incident_rate(self) -> float:
        if self._incident_baseline is None:
            rates = [
                meta.get("stats", {}).get("incident_rate")
                for meta in self.catalogue.values()
            ]
            rates = [float(r) for r in rates if r is not None]
            self._incident_baseline = (
                float(np.mean(rates)) if rates else FIELD_INCIDENT_RATE
            )
        return self._incident_baseline

    def predict(self, entries: list[Entry], conditions: Conditions,
                keep_positions: bool = False, pre_qualifying: bool = False) -> dict:
        if not entries:
            return {"entries": [], "track": self.catalogue.get(conditions.circuit_id)}

        frame = self.build_frame(entries, conditions)
        X = frame[self.features].to_numpy(dtype=float)
        field = len(frame)

        heads = self.prequali if pre_qualifying and self.prequali else {
            "models": self.models, "grid_priors": self.grid_priors, "blend_weights": self.blend_weights,
        }
        raw = {t: m.predict_proba(X)[:, 1] for t, m in heads["models"].items()}

        grid = np.array([e.grid for e in entries], dtype=float)
        priors = {
            target: grid_prior.prior_for(grid, heads["grid_priors"].get(target, {}))
            for target in raw
        }
        anchored = {
            target: grid_prior.blend(
                probs,
                priors[target],
                heads["blend_weights"].get(target, grid_prior.DEFAULT_WEIGHT),
            )
            for target, probs in raw.items()
        }

        sim = simulate_race(
            anchored["win"],
            anchored["podium"],
            anchored["points_finish"],
            dnf_rate=self.reliability_rates(entries, frame),
            incident_rate=self.crash_rates(entries, conditions.circuit_id),
            dsq_rate=self.dsq_rates(entries),
            grid=grid,
            keep_positions=keep_positions,
        )
        win, podium, points = sim["p_win"], sim["p_podium"], sim["p_points"]

        expected = sim["expected_finish"]
        order = np.argsort(-sim["expected_points"])
        placing = np.empty(field, dtype=int)
        placing[order] = np.arange(1, field + 1)

        reasons = [
            _reasons(
                frame.iloc[i], self.track_history.get(e.driver_id, {}).get(conditions.circuit_id),
                e, float(sim["p_crash"][i]),
            )
            for i, e in enumerate(entries)
        ]
        out = []
        for i, entry in enumerate(entries):
            driver = self.drivers.get(entry.driver_id, {})
            history = self.track_history.get(entry.driver_id, {}).get(conditions.circuit_id)
            out.append(
                {
                    "driver_id": entry.driver_id,
                    "name": driver.get("name", entry.driver_id),
                    "code": driver.get("code"),
                    "constructor_id": entry.constructor_id,
                    "team_name": self.teams.get(entry.constructor_id, {}).get(
                        "name", entry.constructor_id
                    ),
                    "grid": entry.grid,
                    "p_win": round(float(win[i]), 4),
                    "p_podium": round(float(podium[i]), 4),
                    "p_points": round(float(points[i]), 4),
                    "p_podium_grid": None if not np.isfinite(priors["podium"][i])
                    else round(float(priors["podium"][i]), 4),
                    "expected_position": int(placing[i]),
                    "expected_finish": round(float(expected[i]), 1),
                    "p_dnf": round(float(sim["p_dnf"][i]), 4),
                    "p_crash": round(float(sim["p_crash"][i]), 4),
                    "p_dsq": round(float(sim["p_dsq"][i]), 4),
                    "expected_points": round(float(sim["expected_points"][i]), 1),
                    "finish_range": [
                        int(sim["finish_p10"][i]),
                        int(sim["finish_p90"][i]),
                    ],
                    "track_history": history,
                    "notes": [n["text"] for n in reasons[i]],
                    "note_codes": [{"code": n["code"], "values": n["values"]} for n in reasons[i]],
                }
            )
        out.sort(key=lambda r: r["expected_position"])
        samples = {"positions": sim["positions"], "gone": sim["gone"]} if keep_positions else {}
        return {
            **samples,
            "entries": out,
            "track": self.catalogue.get(conditions.circuit_id),
            "conditions": {
                "weather": conditions.weather,
                "wet_index": WEATHER_PRESETS.get(conditions.weather, 0.0),
                "tyre_degradation": wet_adjusted_degradation(
                    _pick(
                        conditions.tyre_degradation,
                        self.catalogue.get(conditions.circuit_id, {}).get("tyre_degradation"),
                    ),
                    WEATHER_PRESETS.get(conditions.weather, 0.0),
                ),
                "track_difficulty": _pick(
                    conditions.track_difficulty,
                    self.catalogue.get(conditions.circuit_id, {}).get("track_difficulty"),
                ),
            },
            "model": {
                "stage": "pre_qualifying" if heads is self.prequali else "grid",
                "trained_through": self.trained_through,
                "seasons": self.seasons,
                "summary": self.report.get("summary", {}),
            },
        }


def _reasons(
    row: pd.Series, history: dict | None, entry: Entry, crash: float = 0.0
) -> list[dict]:
    notes: list[dict] = []

    def note(code: str, text: str, **values) -> None:
        notes.append({"code": code, "values": values, "text": text})

    if entry.grid <= 2:
        note("grid_front", f"starts P{entry.grid}", grid=entry.grid)
    elif entry.grid >= 12:
        note("grid_deep", f"deep in the field at P{entry.grid}", grid=entry.grid)

    form = row.get("drv_form_pos")
    if pd.notna(form):
        note("form", f"recent form ~P{form:.1f}", pos=round(float(form), 1))

    team_podium = row.get("team_form_podium_rate")
    if pd.notna(team_podium) and team_podium > 0.35:
        note("team_podium", f"car on the podium {team_podium:.0%} of recent starts",
             rate=round(float(team_podium), 3))

    vs_form = row.get("drv_track_vs_form")
    if pd.notna(vs_form) and history and history.get("races", 0) >= 2:
        if vs_form <= -1.0:
            note("over_performs", f"over-performs here ({vs_form:+.1f} vs usual)",
                 delta=round(float(vs_form), 1))
        elif vs_form >= 1.5:
            note("weaker_here", f"historically weaker here ({vs_form:+.1f} vs usual)",
                 delta=round(float(vs_form), 1))

    if history and history.get("podiums"):
        note("podiums_here", f"{history['podiums']} podium(s) at this circuit", n=int(history["podiums"]))

    dnf = row.get("team_form_dnf_rate")
    if pd.notna(dnf) and dnf > 0.22:
        note("reliability", f"reliability risk ({dnf:.0%} recent DNF rate)", rate=round(float(dnf), 3))

    if history and history.get("incidents"):
        n = int(history["incidents"])
        note("crashed_here", f"crashed out here {n} time{'' if n == 1 else 's'}", n=n)
    elif crash >= FIELD_INCIDENT_RATE * 1.5:
        note("crash_risk", f"elevated crash risk here ({crash:.0%})", rate=round(float(crash), 3))

    return notes[:4]


NEUTRAL_DEGRADATION = 5.0

FIELD_INCIDENT_RATE = 0.05
FIELD_DSQ_RATE = 0.006

CRASH_PRIOR_RACES = 25
DSQ_PRIOR_RACES = 200


def _shrink(value: float, n, prior: float, prior_n: float) -> float:
    n = float(n or 0)
    return (value * n + prior * prior_n) / (n + prior_n)


def _ratio(value, baseline: float) -> float:
    if value is None or not baseline:
        return 1.0
    return float(np.clip(float(value) / baseline, 0.4, 2.2))


def wet_adjusted_degradation(deg: float | None, wet: float) -> float | None:
    if deg is None:
        return None
    wet = float(np.clip(wet, 0.0, 1.0))
    return round(deg * (1.0 - wet) + NEUTRAL_DEGRADATION * wet, 1)


def _column(frame: pd.DataFrame, name: str) -> np.ndarray | None:
    if name not in frame.columns:
        return None
    return pd.to_numeric(frame[name], errors="coerce").to_numpy(dtype=float)


def _pick(*values):
    for v in values:
        if v is not None and not (isinstance(v, float) and np.isnan(v)):
            return float(v)
    return None
