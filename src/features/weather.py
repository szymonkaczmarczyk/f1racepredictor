from __future__ import annotations

import numpy as np
import pandas as pd

DRY_RATIO = 1.035
WET_RATIO = 1.16


def estimate_wet_index(results: pd.DataFrame, window: int = 12) -> pd.Series:
    if "time_millis" not in results.columns:
        return pd.Series(dtype=float)

    winners = results[(results["position"] == 1) & results["time_millis"].notna()].copy()
    if winners.empty:
        return pd.Series(dtype=float)

    winners["ms_per_lap"] = winners["time_millis"] / winners["laps"].clip(lower=1)
    winners = winners.sort_values(["circuit_id", "season", "round"])

    baseline = (
        winners.groupby("circuit_id")["ms_per_lap"]
        .transform(lambda s: s.rolling(window, min_periods=3, center=True).median())
    )
    fallback = winners.groupby("circuit_id")["ms_per_lap"].transform("median")
    baseline = baseline.fillna(fallback)

    ratio = winners["ms_per_lap"] / baseline
    index = (ratio - DRY_RATIO) / (WET_RATIO - DRY_RATIO)
    index = index.clip(0.0, 1.0).fillna(0.0)

    return pd.Series(np.round(index.to_numpy(), 3), index=winners["race_id"].to_numpy())


WEATHER_PRESETS = {
    "dry": 0.0,
    "cloudy": 0.05,
    "light_rain": 0.45,
    "heavy_rain": 0.85,
    "mixed": 0.60,
}
