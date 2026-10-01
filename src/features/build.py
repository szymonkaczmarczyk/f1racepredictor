from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from src.config import FORM_DECAY_PER_RACE, PODIUM_CUTOFF, TRACK_DECAY_PER_YEAR
from src.features.decay import Decayed
from src.ingest.circuits import STREET_CIRCUITS

GRID_FEATURES = [
    "grid", "grid_norm", "quali_position", "quali_gap_pct",
    "reached_q3", "grid_penalty", "pit_lane_start",
    "grid_podium_prior", "grid_win_prior", "grid_podium_prior_here",
]
DRIVER_FEATURES = [
    "drv_form_pos", "drv_form_pos_norm", "drv_form_podium_rate", "drv_form_win_rate",
    "drv_form_points_rate", "drv_form_dnf_rate", "drv_form_grid", "drv_form_gain",
    "drv_form_quali_gap", "drv_beat_teammate_rate", "drv_quali_vs_teammate",
    "drv_career_races", "drv_career_podium_rate", "drv_season_points_norm",
    "drv_season_rank", "drv_season_podium_rate",
    "drv_wet_podium_rate", "drv_wet_gain",
]
TEAM_FEATURES = [
    "team_form_pos", "team_form_podium_rate", "team_form_points_rate",
    "team_form_dnf_rate", "team_form_quali_gap", "team_form_best_pos",
    "team_season_points_norm", "team_season_rank", "team_car_rank_est",
]
TRACK_FEATURES = [
    "drv_track_races", "drv_track_avg_pos", "drv_track_podium_rate",
    "drv_track_best_pos", "drv_track_gain", "team_track_avg_pos",
    "drv_track_vs_form",
]
CIRCUIT_FEATURES = [
    "circuit_volatility", "circuit_dnf_rate", "circuit_grid_stickiness",
    "circuit_pole_win_rate", "circuit_laps", "circuit_distance_km",
    "tyre_degradation", "track_difficulty", "is_street", "is_wet",
]
CONTEXT_FEATURES = ["field_size", "round_norm", "driver_age", "era_races"]

RELATIVE_FEATURES = [
    "pace_rank_in_field", "form_rank_in_field", "grid_minus_pace_rank",
    "cars_ahead_faster", "cars_ahead_slower", "field_pace_spread",
    "team_best_grid", "grid_vs_teammate", "quali_gap_to_best_rival",
]

PRACTICE_COLUMNS = ["fp_best_gap_pct", "fp_longrun_gap_pct", "fp_team_longrun_gap_pct"]
PRACTICE_FEATURES = PRACTICE_COLUMNS + ["fp_best_rank", "fp_longrun_rank"]

FEATURES = (
    GRID_FEATURES + DRIVER_FEATURES + TEAM_FEATURES
    + TRACK_FEATURES + CIRCUIT_FEATURES + CONTEXT_FEATURES + RELATIVE_FEATURES
    + PRACTICE_FEATURES
)

TARGETS = ["podium", "win", "points_finish"]

ACTIVE_TEAM_WINDOW = 3

ERA_STARTS = (1998, 2009, 2014, 2017, 2022, 2026)
ERA_TEAM_FADE = 0.3
ERA_RACES_CAP = 60


class FeatureStore:

    def __init__(
        self,
        form_decay: float = FORM_DECAY_PER_RACE,
        track_decay: float = TRACK_DECAY_PER_YEAR,
    ) -> None:
        self.form_decay = form_decay
        self.track_decay = track_decay

        self.drv: dict[str, dict[str, Decayed]] = defaultdict(_stat_group)
        self.team: dict[str, dict[str, Decayed]] = defaultdict(_stat_group)
        self.drv_track: dict[tuple[str, str], dict[str, Decayed]] = defaultdict(_stat_group)
        self.team_track: dict[tuple[str, str], dict[str, Decayed]] = defaultdict(_stat_group)
        self.circuit: dict[str, dict[str, Decayed]] = defaultdict(_stat_group)
        self.grid_slot: dict[int, dict[str, Decayed]] = defaultdict(_stat_group)
        self.circuit_grid: dict[tuple[str, int], dict[str, Decayed]] = defaultdict(_stat_group)

        self.drv_races: dict[str, int] = defaultdict(int)
        self.season_points: dict[int, dict[str, float]] = defaultdict(_float_counter)
        self.season_podiums: dict[int, dict[str, int]] = defaultdict(_int_counter)
        self.season_starts: dict[int, dict[str, int]] = defaultdict(_int_counter)
        self.team_season_points: dict[int, dict[str, float]] = defaultdict(_float_counter)
        self.driver_dob: dict[str, pd.Timestamp] = {}
        self.last_team: dict[str, str] = {}
        self.races_seen = 0
        self.team_last_race: dict[str, int] = {}
        self.season_seen: int | None = None
        self.era_races = 0

    def start_season(self, season: int) -> None:
        if self.season_seen is not None and season <= self.season_seen:
            return
        if self.season_seen is not None and season in ERA_STARTS:
            for stats in self.team.values():
                for stat in stats.values():
                    stat.weight *= ERA_TEAM_FADE
                    stat.total *= ERA_TEAM_FADE
            self.era_races = 0
        self.season_seen = season

    def entry_features(
        self,
        *,
        driver_id: str,
        constructor_id: str,
        circuit_id: str,
        season: int,
        year_frac: float,
        date: pd.Timestamp,
        grid: int,
        field_size: int,
        round_norm: float,
        quali_position: float | None = None,
        quali_gap_pct: float | None = None,
        reached_q3: float | None = None,
        pit_lane_start: bool = False,
        laps: float | None = None,
        distance_km: float | None = None,
        tyre_degradation: float | None = None,
        track_difficulty: float | None = None,
        is_wet: float = 0.0,
    ) -> dict:
        d = self.drv[driver_id]
        t = self.team[constructor_id]
        dt = self.drv_track[(driver_id, circuit_id)]
        tt = self.team_track[(constructor_id, circuit_id)]
        c = self.circuit[circuit_id]

        drv_form_pos = d["pos"].mean
        drv_track_pos = dt["pos"].mean

        drv_rank, team_rank = self._standings(season, driver_id, constructor_id)
        starts = self.season_starts[season][driver_id]

        age = None
        dob = self.driver_dob.get(driver_id)
        if dob is not None:
            age = round((date - dob).days / 365.25, 2)

        return {
            "grid": float(grid),
            "grid_norm": (grid - 1) / max(field_size - 1, 1),
            "quali_position": quali_position,
            "quali_gap_pct": quali_gap_pct,
            "reached_q3": reached_q3,
            "grid_penalty": (grid - quali_position) if quali_position is not None else None,
            "pit_lane_start": float(pit_lane_start),
            "grid_podium_prior": self._grid_prior(grid, "podium"),
            "grid_win_prior": self._grid_prior(grid, "win"),
            "grid_podium_prior_here": self._grid_prior_here(circuit_id, grid),

            "drv_form_pos": drv_form_pos,
            "drv_form_pos_norm": d["pos_norm"].mean,
            "drv_form_podium_rate": _rate(d["podium"]),
            "drv_form_win_rate": _rate(d["win"]),
            "drv_form_points_rate": d["norm_points"].mean,
            "drv_form_dnf_rate": _rate(d["dnf"]),
            "drv_form_grid": d["grid"].mean,
            "drv_form_gain": d["gain"].mean,
            "drv_form_quali_gap": d["quali_gap"].mean,
            "drv_beat_teammate_rate": _rate(d["beat_mate"]),
            "drv_quali_vs_teammate": d["quali_vs_mate"].mean,
            "drv_career_races": float(self.drv_races[driver_id]),
            "drv_career_podium_rate": d["podium"].blended(0.10, prior_weight=3.0),
            "drv_season_points_norm": self.season_points[season][driver_id] / max(starts, 1),
            "drv_season_rank": drv_rank,
            "drv_season_podium_rate": self.season_podiums[season][driver_id] / max(starts, 1),
            "drv_wet_podium_rate": d["wet_podium"].blended(0.12, 1.5) if d["wet_podium"].count else None,
            "drv_wet_gain": d["wet_gain"].mean,

            "team_form_pos": t["pos"].mean,
            "team_form_podium_rate": _rate(t["podium"]),
            "team_form_points_rate": t["norm_points"].mean,
            "team_form_dnf_rate": _rate(t["dnf"]),
            "team_form_quali_gap": t["quali_gap"].mean,
            "team_form_best_pos": t["best_pos"].mean,
            "team_season_points_norm": self.team_season_points[season][constructor_id]
            / max(round_norm * 24 + 1, 1),
            "team_season_rank": team_rank,
            "team_car_rank_est": self._car_rank(constructor_id),

            "drv_track_races": float(dt["pos"].count),
            "drv_track_avg_pos": drv_track_pos,
            "drv_track_podium_rate": _rate(dt["podium"]) if dt["podium"].count else None,
            "drv_track_best_pos": dt["pos"].best,
            "drv_track_gain": dt["gain"].mean,
            "team_track_avg_pos": tt["pos"].mean,
            "drv_track_vs_form": (
                drv_track_pos - drv_form_pos
                if drv_track_pos is not None and drv_form_pos is not None
                else None
            ),

            "circuit_volatility": c["volatility"].mean,
            "circuit_dnf_rate": _rate(c["dnf"]),
            "circuit_grid_stickiness": _rate(c["sticky"]),
            "circuit_pole_win_rate": _rate(c["pole_win"]),
            "circuit_laps": laps,
            "circuit_distance_km": distance_km,
            "tyre_degradation": tyre_degradation,
            "track_difficulty": track_difficulty,
            "is_street": float(circuit_id in STREET_CIRCUITS),
            "is_wet": is_wet,

            "field_size": float(field_size),
            "round_norm": round_norm,
            "driver_age": age,
            "era_races": float(min(self.era_races, ERA_RACES_CAP)),
        }

    def update(
        self, race: pd.DataFrame, *, win_points: float, year_frac: float, wet: float = 0.0
    ) -> None:
        field = len(race)
        if field == 0:
            return

        circuit_id = race["circuit_id"].iloc[0]
        season = int(race["season"].iloc[0])
        decay = self.form_decay

        by_team: dict[str, list] = defaultdict(list)
        for row in race.itertuples(index=False):
            by_team[row.constructor_id].append(row)

        pole_row = race.loc[race["grid"].idxmin()] if len(race) else None
        if pole_row is not None:
            self.circuit[circuit_id]["pole_win"].add(
                float(pole_row["position"] == 1), decay
            )

        for row in race.itertuples(index=False):
            pos = float(row.position)
            pos_norm = (pos - 1) / max(field - 1, 1)
            podium = float(row.classified and pos <= PODIUM_CUTOFF)
            dnf = float(not row.finished)
            gain = float(row.grid) - pos
            quali_gap = getattr(row, "quali_gap_pct", None)

            d = self.drv[row.driver_id]
            d["pos"].add(pos, decay)
            d["pos_norm"].add(pos_norm, decay)
            d["podium"].add(podium, decay)
            d["win"].add(float(pos == 1 and row.classified), decay)
            d["norm_points"].add(row.points / win_points, decay)
            d["dnf"].add(dnf, decay)
            d["grid"].add(float(row.grid), decay)
            d["gain"].add(gain, decay)
            if quali_gap is not None and not pd.isna(quali_gap):
                d["quali_gap"].add(float(quali_gap), decay)
            if wet >= 0.35:
                d["wet_podium"].add(podium, 0.97)
                d["wet_gain"].add(gain, 0.97)

            t = self.team[row.constructor_id]
            t["pos"].add(pos, decay)
            t["podium"].add(podium, decay)
            t["norm_points"].add(row.points / win_points, decay)
            t["dnf"].add(dnf, decay)
            if quali_gap is not None and not pd.isna(quali_gap):
                t["quali_gap"].add(float(quali_gap), decay)

            dt = self.drv_track[(row.driver_id, circuit_id)]
            dt["pos"].add_at(pos, year_frac, self.track_decay)
            dt["podium"].add_at(podium, year_frac, self.track_decay)
            dt["gain"].add_at(gain, year_frac, self.track_decay)
            tt = self.team_track[(row.constructor_id, circuit_id)]
            tt["pos"].add_at(pos, year_frac, self.track_decay)

            c = self.circuit[circuit_id]
            c["volatility"].add(abs(gain), decay)
            c["dnf"].add(dnf, decay)
            if row.grid <= PODIUM_CUTOFF:
                c["sticky"].add(podium, decay)

            slot = self.grid_slot[int(row.grid)]
            slot["podium"].add(podium, 0.995)
            slot["win"].add(float(pos == 1 and row.classified), 0.995)
            self.circuit_grid[(circuit_id, _grid_bucket(row.grid))]["podium"].add(podium, 0.98)

            self.drv_races[row.driver_id] += 1
            self.season_points[season][row.driver_id] += row.points
            self.season_starts[season][row.driver_id] += 1
            self.season_podiums[season][row.driver_id] += int(podium)
            self.team_season_points[season][row.constructor_id] += row.points
            self.last_team[row.driver_id] = row.constructor_id
            self.team_last_race[row.constructor_id] = self.races_seen

        for constructor_id, rows in by_team.items():
            self.team[constructor_id]["best_pos"].add(
                float(min(r.position for r in rows)), decay
            )
            if len(rows) != 2:
                continue
            a, b = rows
            for me, mate in ((a, b), (b, a)):
                if me.finished and mate.finished:
                    self.drv[me.driver_id]["beat_mate"].add(
                        float(me.position < mate.position), decay
                    )
                my_q = getattr(me, "quali_gap_pct", None)
                mate_q = getattr(mate, "quali_gap_pct", None)
                if my_q is not None and mate_q is not None and not (pd.isna(my_q) or pd.isna(mate_q)):
                    self.drv[me.driver_id]["quali_vs_mate"].add(float(my_q - mate_q), decay)

        self.races_seen += 1
        self.era_races += 1

    def _standings(self, season: int, driver_id: str, constructor_id: str):
        return (
            _rank_of(driver_id, self.season_points[season]),
            _rank_of(constructor_id, self.team_season_points[season]),
        )

    def _grid_prior(self, grid: int, kind: str) -> float | None:
        stat = self.grid_slot[int(grid)].get(kind)
        if stat is None or stat.weight <= 0:
            return None
        return stat.blended(PODIUM_CUTOFF / 20.0 if kind == "podium" else 0.05, 4.0)

    def _grid_prior_here(self, circuit_id: str, grid: int) -> float | None:
        bucket = _grid_bucket(grid)
        stat = self.circuit_grid[(circuit_id, bucket)].get("podium")
        if stat is None or stat.weight <= 0:
            return None
        overall = self._grid_prior(grid, "podium")
        return stat.blended(overall if overall is not None else 0.15, 6.0)

    def _car_rank(self, constructor_id: str) -> float | None:
        oldest = self.races_seen - ACTIVE_TEAM_WINDOW
        gaps = {
            cid: stats["quali_gap"].mean
            for cid, stats in self.team.items()
            if stats["quali_gap"].weight > 0.5
            and self.team_last_race.get(cid, -1) >= oldest
        }
        target = gaps.get(constructor_id)
        if target is None:
            return None
        return float(sum(1 for g in gaps.values() if g < target) + 1)


def _grid_bucket(grid: int) -> int:
    grid = int(grid)
    if grid <= 3:
        return grid
    if grid <= 5:
        return 4
    if grid <= 8:
        return 6
    if grid <= 12:
        return 9
    return 13


def _stat_group() -> dict[str, Decayed]:
    return defaultdict(Decayed)


def _float_counter() -> dict[str, float]:
    return defaultdict(float)


def _int_counter() -> dict[str, int]:
    return defaultdict(int)


def _rate(stat: Decayed) -> float | None:
    return stat.mean


def _rank_of(key, scores: dict) -> float | None:
    if not scores or key not in scores:
        return None
    target = scores[key]
    return float(sum(1 for v in scores.values() if v > target) + 1)


def add_race_relative_features(frame: pd.DataFrame) -> pd.DataFrame:
    f = frame.copy()

    f["pace_rank_in_field"] = f["team_form_quali_gap"].rank(method="min")
    f["form_rank_in_field"] = f["drv_form_pos"].rank(method="min")
    f["grid_minus_pace_rank"] = f["grid"] - f["pace_rank_in_field"]
    f["field_pace_spread"] = f["team_form_quali_gap"].std()

    grid = f["grid"].to_numpy(dtype=float)
    pace = f["pace_rank_in_field"].to_numpy(dtype=float)
    pace = np.where(np.isnan(pace), np.nanmedian(pace) if not np.all(np.isnan(pace)) else 0.0, pace)
    ahead = grid[None, :] < grid[:, None]
    faster = pace[None, :] < pace[:, None]
    f["cars_ahead_faster"] = (ahead & faster).sum(axis=1).astype(float)
    f["cars_ahead_slower"] = (ahead & ~faster).sum(axis=1).astype(float)

    by_team = f.groupby("constructor_id")["grid"]
    f["team_best_grid"] = by_team.transform("min")
    pair = by_team.transform("count") == 2
    teammate = by_team.transform("sum") - f["grid"]
    f["grid_vs_teammate"] = np.where(pair, f["grid"] - teammate, np.nan)

    gaps = f["quali_gap_pct"]
    team_best = gaps.groupby(f["constructor_id"]).min().dropna().sort_values()
    if len(team_best) >= 2:
        fastest_team = team_best.index[0]
        rival = np.where(f["constructor_id"] == fastest_team, team_best.iloc[1], team_best.iloc[0])
        f["quali_gap_to_best_rival"] = gaps - rival
    else:
        f["quali_gap_to_best_rival"] = np.nan

    return f


def season_win_points(results: pd.DataFrame) -> dict[int, float]:
    winners = results[results["position"] == 1]
    table = winners.groupby("season")["points"].max().to_dict()
    return {int(k): float(v) if v else 25.0 for k, v in table.items()}


def year_fraction(date: pd.Timestamp) -> float:
    return date.year + (date.dayofyear - 1) / 365.25


def build_dataset(
    results: pd.DataFrame,
    qualifying: pd.DataFrame,
    races: pd.DataFrame,
    circuit_meta: dict[str, dict] | None = None,
    store: FeatureStore | None = None,
    wet_index: pd.Series | None = None,
    practice: pd.DataFrame | None = None,
    before_update=None,
) -> tuple[pd.DataFrame, FeatureStore]:
    circuit_meta = circuit_meta or {}
    store = store or FeatureStore()
    wet_map = {} if wet_index is None else wet_index.to_dict()
    practice_by_race = (
        {rid: part.set_index("driver_id") for rid, part in practice.groupby("race_id")}
        if practice is not None and not practice.empty else {}
    )

    df = results.merge(
        qualifying[["race_id", "driver_id", "quali_position", "quali_gap_pct", "q3"]],
        on=["race_id", "driver_id"],
        how="left",
    )
    df = df[~df["status"].isin(["Did not qualify", "Did not prequalify", "Withdrew"])]
    df = df.sort_values(["date", "season", "round", "position"]).reset_index(drop=True)

    dob = _driver_dob(results)
    store.driver_dob.update(dob)

    win_points = season_win_points(results)
    rounds_per_season = races.groupby("season")["round"].max().to_dict()

    laps_seen: dict[str, list[float]] = defaultdict(list)
    frames: list[pd.DataFrame] = []
    for race_id, race in df.groupby("race_id", sort=False):
        rows: list[dict] = []
        season = int(race["season"].iloc[0])
        rnd = int(race["round"].iloc[0])
        date = race["date"].iloc[0]
        circuit_id = race["circuit_id"].iloc[0]
        field = len(race)
        yf = year_fraction(date)
        meta = circuit_meta.get(circuit_id, {})
        store.start_season(season)
        laps = _scheduled_laps(laps_seen[circuit_id], meta, race)
        laps_seen[circuit_id].append(float(race["laps"].max()))
        round_norm = rnd / max(rounds_per_season.get(season, 20), 1)
        wet = float(wet_map.get(race_id, 0.0))

        for row in race.itertuples(index=False):
            feats = store.entry_features(
                driver_id=row.driver_id,
                constructor_id=row.constructor_id,
                circuit_id=circuit_id,
                season=season,
                year_frac=yf,
                date=date,
                grid=int(row.grid),
                field_size=field,
                round_norm=round_norm,
                quali_position=_nan_to_none(row.quali_position),
                quali_gap_pct=_nan_to_none(row.quali_gap_pct),
                reached_q3=(
                    None if pd.isna(row.quali_position)
                    else (0.0 if pd.isna(row.q3) else 1.0)
                ),
                pit_lane_start=bool(row.pit_lane_start),
                laps=laps,
                distance_km=(laps * meta["length_m"] / 1000.0)
                if laps and meta.get("length_m") else None,
                tyre_degradation=meta.get("tyre_degradation"),
                track_difficulty=meta.get("track_difficulty"),
                is_wet=wet,
            )
            feats.update(
                {
                    "race_id": race_id,
                    "season": season,
                    "round": rnd,
                    "date": date,
                    "circuit_id": circuit_id,
                    "driver_id": row.driver_id,
                    "driver_name": row.driver_name,
                    "constructor_id": row.constructor_id,
                    "finish_position": int(row.position),
                    "podium": int(row.classified and row.position <= PODIUM_CUTOFF),
                    "win": int(row.classified and row.position == 1),
                    "points_finish": int(row.points > 0),
                }
            )
            rows.append(feats)

        frames.append(add_race_relative_features(
            with_practice(pd.DataFrame(rows), practice_by_race.get(race_id))
        ))
        if before_update is not None:
            before_update(race, store)
        store.update(race, win_points=win_points.get(season, 25.0), year_frac=yf, wet=wet)

    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    for col in FEATURES:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out, store


def with_practice(frame: pd.DataFrame, weekend: pd.DataFrame | None) -> pd.DataFrame:
    for col in PRACTICE_COLUMNS:
        frame[col] = (
            frame["driver_id"].map(weekend[col]) if weekend is not None and col in weekend
            else np.nan
        )
    frame["fp_best_rank"] = frame["fp_best_gap_pct"].rank(method="min")
    frame["fp_longrun_rank"] = frame["fp_longrun_gap_pct"].rank(method="min")
    return frame


def _scheduled_laps(previous: list[float], meta: dict, race: pd.DataFrame) -> float | None:
    if previous:
        return float(np.median(previous[-3:]))
    if meta.get("laps"):
        return float(meta["laps"])
    return float(race["laps"].max()) if len(race) else None


def _driver_dob(results: pd.DataFrame) -> dict[str, pd.Timestamp]:
    if "driver_dob" not in results.columns:
        return {}
    pairs = results.dropna(subset=["driver_dob"]).drop_duplicates("driver_id")
    return dict(zip(pairs["driver_id"], pd.to_datetime(pairs["driver_dob"])))


def _nan_to_none(value):
    return None if value is None or pd.isna(value) else float(value)
