from __future__ import annotations

import numpy as np
import pandas as pd

from src.features import build

EXPECTED_GRID_SESSIONS = 3
ROOKIE_GAP_MARGIN = 0.5
PRE_QUALIFYING_SOURCES = ("expected", "expected_practice")


def expected_order(drivers: list[str], teams: list[str], history: pd.DataFrame) -> pd.DataFrame:
    gaps = (
        history.sort_values(["season", "round"])
        .groupby("driver_id")["quali_gap_pct"]
        .apply(lambda s: s.dropna().tail(EXPECTED_GRID_SESSIONS).median())
    )
    frame = pd.DataFrame({"driver_id": drivers, "team": teams})
    frame["gap"] = frame["driver_id"].map(gaps)
    frame["gap"] = frame["gap"].fillna(frame.groupby("team")["gap"].transform("max") + ROOKIE_GAP_MARGIN)
    frame = frame.sort_values("gap", na_position="last").reset_index(drop=True)
    frame["grid"] = np.arange(1, len(frame) + 1)
    frame["gap"] = frame["gap"] - frame["gap"].min()
    return frame.set_index("driver_id")


class ExpectedGridRecorder:
    def __init__(self, qualifying: pd.DataFrame, races: pd.DataFrame):
        order = races.sort_values(["season", "round"])["race_id"].tolist()
        self.rank = {race_id: i for i, race_id in enumerate(order)}
        self.qualifying = qualifying.assign(_k=qualifying["race_id"].map(self.rank))
        self.grids: dict[str, pd.DataFrame] = {}

    def __call__(self, race: pd.DataFrame, store: build.FeatureStore) -> None:
        race_id = race["race_id"].iloc[0]
        circuit_id = race["circuit_id"].iloc[0]
        before = self.qualifying[
            (self.qualifying["_k"] < self.rank[race_id])
            & self.qualifying["driver_id"].isin(race["driver_id"])
        ]
        grid = expected_order(race["driver_id"].tolist(), race["constructor_id"].tolist(), before)
        grid["grid_podium_prior"] = [store._grid_prior(int(g), "podium") for g in grid["grid"]]
        grid["grid_win_prior"] = [store._grid_prior(int(g), "win") for g in grid["grid"]]
        grid["grid_podium_prior_here"] = [store._grid_prior_here(circuit_id, int(g)) for g in grid["grid"]]
        self.grids[race_id] = grid

    def dataset(self, actual: pd.DataFrame) -> pd.DataFrame:
        frames = []
        for race_id, part in actual.groupby("race_id", sort=False):
            grid = self.grids.get(race_id)
            if grid is None:
                continue
            frame = part.copy()
            field = len(frame)
            frame["grid"] = frame["driver_id"].map(grid["grid"]).astype(float)
            frame["grid_norm"] = (frame["grid"] - 1) / max(field - 1, 1)
            frame["quali_position"] = frame["grid"]
            frame["quali_gap_pct"] = frame["driver_id"].map(grid["gap"]).astype(float)
            frame["reached_q3"] = (frame["grid"] <= 10).astype(float)
            frame["grid_penalty"] = 0.0
            frame["pit_lane_start"] = 0.0
            for col in ("grid_podium_prior", "grid_win_prior", "grid_podium_prior_here"):
                frame[col] = frame["driver_id"].map(grid[col]).astype(float)
            frames.append(build.add_race_relative_features(frame))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=actual.columns)
