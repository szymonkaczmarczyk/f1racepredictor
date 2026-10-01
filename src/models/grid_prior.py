from __future__ import annotations

import numpy as np
import pandas as pd

MAX_SLOT = 22

SLOT_PRIOR_STRENGTH = 50.0

WEIGHT_GRID = (0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0)

DEFAULT_WEIGHT = 0.45


def build_prior(frame: pd.DataFrame, target: str) -> dict[int, float]:
    slots = frame["grid"].clip(1, MAX_SLOT).astype(int)
    stats = frame.groupby(slots)[target].agg(["mean", "size"])
    overall = float(frame[target].mean())
    return {
        int(slot): float(
            (row["mean"] * row["size"] + overall * SLOT_PRIOR_STRENGTH)
            / (row["size"] + SLOT_PRIOR_STRENGTH)
        )
        for slot, row in stats.iterrows()
    }


def prior_for(grid: np.ndarray, table: dict[int, float]) -> np.ndarray:
    if not table:
        return np.full(len(grid), np.nan)
    slots = np.clip(np.asarray(grid, dtype=float), 1, MAX_SLOT).astype(int)
    backmarker = table[max(table)]
    return np.array([table.get(int(s), backmarker) for s in slots], dtype=float)


def blend(model_p: np.ndarray, prior_p: np.ndarray, weight: float) -> np.ndarray:
    model_p = np.asarray(model_p, dtype=float)
    prior_p = np.asarray(prior_p, dtype=float)
    usable = np.isfinite(prior_p)
    out = model_p.copy()
    out[usable] = _sigmoid(
        weight * _logit(model_p[usable]) + (1.0 - weight) * _logit(prior_p[usable])
    )
    return out


def choose_weight(
    predictions: pd.DataFrame,
    model_col: str,
    prior_col: str,
    score_fn,
    weights=WEIGHT_GRID,
) -> float:
    if predictions.empty:
        return DEFAULT_WEIGHT
    best_weight, best_score = DEFAULT_WEIGHT, -np.inf
    for candidate in weights:
        trial = predictions.copy()
        trial["_blended"] = blend(
            trial[model_col].to_numpy(), trial[prior_col].to_numpy(), candidate
        )
        value = score_fn(trial, "_blended")
        if value > best_score:
            best_weight, best_score = candidate, value
    return best_weight


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))
