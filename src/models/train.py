from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

from src.config import (
    MIN_TRAIN_SEASONS,
    PODIUM_CUTOFF,
    RANDOM_STATE,
    RECENCY_HALF_LIFE_YEARS,
)
from src.features.build import FEATURES, TARGETS
from src.models import grid_prior


MONOTONIC = {
    "grid": -1, "grid_norm": -1, "quali_position": -1, "quali_gap_pct": -1,
    "grid_penalty": -1, "pit_lane_start": -1,
    "drv_form_pos": -1, "drv_form_pos_norm": -1, "drv_form_grid": -1,
    "drv_form_dnf_rate": -1, "drv_form_quali_gap": -1, "drv_season_rank": -1,
    "team_form_pos": -1, "team_form_dnf_rate": -1, "team_form_quali_gap": -1,
    "team_form_best_pos": -1, "team_season_rank": -1, "team_car_rank_est": -1,
    "drv_track_avg_pos": -1, "drv_track_best_pos": -1, "team_track_avg_pos": -1,
    "drv_track_vs_form": -1,
    "reached_q3": 1, "drv_form_podium_rate": 1, "drv_form_win_rate": 1,
    "drv_form_points_rate": 1, "drv_form_gain": 1, "drv_beat_teammate_rate": 1,
    "drv_career_podium_rate": 1, "drv_season_points_norm": 1,
    "drv_season_podium_rate": 1, "drv_wet_podium_rate": 1, "drv_wet_gain": 1,
    "team_form_podium_rate": 1, "team_form_points_rate": 1,
    "team_season_points_norm": 1, "drv_track_podium_rate": 1, "drv_track_gain": 1,
}

DEFAULT_PARAMS = dict(
    loss="log_loss",
    learning_rate=0.05,
    max_iter=400,
    max_leaf_nodes=31,
    min_samples_leaf=60,
    l2_regularization=5.0,
    max_features=0.6,
    early_stopping=False,
    random_state=RANDOM_STATE,
)


SIMS_IN_VALIDATION = 4_000

MIN_SEASONS_TO_FIT_BLEND = 2


def monotonic_vector(features: list[str] = FEATURES) -> list[int]:
    return [MONOTONIC.get(name, 0) for name in features]


def make_model(monotonic: bool = False, **overrides) -> HistGradientBoostingClassifier:
    params = {**DEFAULT_PARAMS, **overrides}
    if monotonic:
        params["monotonic_cst"] = monotonic_vector()
    return HistGradientBoostingClassifier(**params)


def recency_weights(
    dates: pd.Series,
    reference: pd.Timestamp | None = None,
    half_life: float = RECENCY_HALF_LIFE_YEARS,
) -> np.ndarray:
    reference = reference if reference is not None else dates.max()
    years_ago = (reference - dates).dt.days / 365.25
    if not half_life or half_life <= 0:
        return np.ones(len(dates))
    return np.power(0.5, years_ago / half_life)


def normalise_per_race(
    probs: np.ndarray, race_ids: np.ndarray, expected: float = PODIUM_CUTOFF
) -> np.ndarray:
    out = probs.astype(float).copy()
    for rid in np.unique(race_ids):
        mask = race_ids == rid
        p = out[mask]
        for _ in range(30):
            total = p.sum()
            if total <= 1e-9:
                break
            p = np.clip(p * (expected / total), 1e-6, 1.0)
            if abs(p.sum() - expected) < 1e-4:
                break
        out[mask] = p
    return out


def race_metrics(df: pd.DataFrame, prob_col: str, truth_col: str = "podium") -> dict:
    hits, exact, winner_hits, races = 0, 0, 0, 0
    for _, race in df.groupby("race_id", sort=False):
        ordered = race.sort_values(prob_col, ascending=False)
        top3 = set(ordered.head(PODIUM_CUTOFF)["driver_id"])
        actual = set(race.loc[race[truth_col] == 1, "driver_id"])
        if not actual:
            continue
        races += 1
        hits += len(top3 & actual)
        exact += int(top3 == actual)
        if "win" in race.columns:
            true_winner = race.loc[race["win"] == 1, "driver_id"]
            if len(true_winner):
                winner_hits += int(ordered.iloc[0]["driver_id"] == true_winner.iloc[0])
    if races == 0:
        return {}
    return {
        "races": races,
        "podium_hit_rate": hits / (races * PODIUM_CUTOFF),
        "exact_podium_rate": exact / races,
        "winner_top1_rate": winner_hits / races,
    }


def probability_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    if len(np.unique(y)) < 2:
        return {}
    return {
        "roc_auc": roc_auc_score(y, p),
        "log_loss": log_loss(y, np.clip(p, 1e-6, 1 - 1e-6)),
        "brier": brier_score_loss(y, p),
    }


def fit(
    dataset: pd.DataFrame,
    target: str = "podium",
    reference: pd.Timestamp | None = None,
    half_life: float = RECENCY_HALF_LIFE_YEARS,
    **model_kw,
):
    model = make_model(**model_kw)
    X = dataset[FEATURES].to_numpy(dtype=float)
    y = dataset[target].to_numpy(dtype=int)
    w = recency_weights(dataset["date"], reference, half_life)
    model.fit(X, y, sample_weight=w)
    return model


def walk_forward_predictions(
    dataset: pd.DataFrame,
    seasons: list[int],
    half_life: float = RECENCY_HALF_LIFE_YEARS,
    **model_kw,
) -> pd.DataFrame:
    available = sorted(dataset["season"].unique())
    frames = []

    for season in seasons:
        if season not in available:
            continue
        train = dataset[dataset["season"] < season]
        test = dataset[dataset["season"] == season].copy()
        if train["season"].nunique() < MIN_TRAIN_SEASONS or test.empty:
            continue

        X_test = test[FEATURES].to_numpy(dtype=float)
        reference = train["date"].max()
        grid = test["grid"].to_numpy(dtype=float)

        for target in TARGETS:
            model = fit(train, target=target, reference=reference,
                        half_life=half_life, **model_kw)
            test[f"p_{target}"] = model.predict_proba(X_test)[:, 1]
            table = grid_prior.build_prior(train, target)
            test[f"prior_{target}"] = grid_prior.prior_for(grid, table)

        test["train_races"] = train["race_id"].nunique()
        frames.append(test)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


SIMULATED = {"s_win": "p_win", "s_podium": "p_podium",
             "s_points_finish": "p_points", "s_expected_points": "expected_points"}


def simulate_predictions(predictions: pd.DataFrame, prefix: str = "b_") -> pd.DataFrame:
    from src.models.simulate import simulate_race

    out = predictions.copy()
    for col in SIMULATED:
        out[col] = np.nan
    for _, race in predictions.groupby("race_id", sort=False):
        result = simulate_race(
            race[f"{prefix}win"].to_numpy(),
            race[f"{prefix}podium"].to_numpy(),
            race[f"{prefix}points_finish"].to_numpy(),
            dnf_rate=race["team_form_dnf_rate"].to_numpy(),
            grid=race["grid"].to_numpy(dtype=float),
            n_sims=SIMS_IN_VALIDATION,
        )
        for col, key in SIMULATED.items():
            out.loc[race.index, col] = result[key]
    return out


CALIBRATION_BINS = (0.0, 0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0)


def calibration_table(simulated: pd.DataFrame) -> dict[str, list[dict]]:
    tables = {}
    for target in TARGETS:
        col = f"s_{target}"
        bins = pd.cut(simulated[col], CALIBRATION_BINS, include_lowest=True)
        grouped = simulated.groupby(bins, observed=True).agg(
            predicted=(col, "mean"), observed=(target, "mean"), n=(target, "size")
        )
        tables[target] = [
            {"bin": str(b), "predicted": round(float(r.predicted), 4),
             "observed": round(float(r.observed), 4), "n": int(r.n)}
            for b, r in grouped.iterrows()
        ]
    return tables


def fit_blend_weights(predictions: pd.DataFrame) -> dict[str, float]:
    def brier(frame: pd.DataFrame, col: str) -> float:
        return -brier_score_loss(frame["_target"], frame[col])

    weights = {}
    for target in TARGETS:
        frame = predictions.copy()
        frame["_target"] = frame[target]
        weights[target] = grid_prior.choose_weight(
            frame, f"p_{target}", f"prior_{target}", brier
        )
    return weights


def rolling_blend_weights(predictions: pd.DataFrame) -> pd.DataFrame:
    seasons = sorted(predictions["season"].unique())
    out = predictions.copy()
    for i, season in enumerate(seasons):
        past = predictions[predictions["season"] < season]
        weights = (
            fit_blend_weights(past)
            if i >= MIN_SEASONS_TO_FIT_BLEND and not past.empty
            else {t: grid_prior.DEFAULT_WEIGHT for t in TARGETS}
        )
        mask = out["season"] == season
        for target in TARGETS:
            out.loc[mask, f"b_{target}"] = grid_prior.blend(
                out.loc[mask, f"p_{target}"].to_numpy(),
                out.loc[mask, f"prior_{target}"].to_numpy(),
                weights[target],
            )
    return out


def report_from_predictions(predictions: pd.DataFrame, target: str = "podium") -> pd.DataFrame:
    if "s_podium" not in predictions.columns:
        predictions = simulate_predictions(predictions)
    rows = []
    for season, part in predictions.groupby("season"):
        part = part.reset_index(drop=True)

        y = part[target].to_numpy(dtype=int)
        row = {"season": int(season), "train_races": int(part["train_races"].iloc[0])}
        row.update(probability_metrics(y, part[f"s_{target}"].to_numpy()))
        row.update(race_metrics(part, "s_expected_points", truth_col=target))
        for other, short in (("win", "win"), ("points_finish", "points")):
            metrics = probability_metrics(part[other].to_numpy(dtype=int), part[f"s_{other}"].to_numpy())
            row[f"{short}_brier"] = metrics.get("brier")
            row[f"{short}_log_loss"] = metrics.get("log_loss")

        baseline = part.copy()
        baseline["prob"] = -baseline["grid"]
        base = race_metrics(baseline, "prob", truth_col=target)
        row["baseline_podium_hit_rate"] = base.get("podium_hit_rate")
        row["baseline_exact_podium_rate"] = base.get("exact_podium_rate")
        row["baseline_winner_top1_rate"] = base.get("winner_top1_rate")
        row["lift_vs_grid"] = row.get("podium_hit_rate", 0) - base.get("podium_hit_rate", 0)
        row["winner_lift_vs_pole"] = (
            row.get("winner_top1_rate", 0) - base.get("winner_top1_rate", 0)
        )
        rows.append(row)
    return pd.DataFrame(rows)


def walk_forward(
    dataset: pd.DataFrame,
    seasons: list[int],
    target: str = "podium",
    half_life: float = RECENCY_HALF_LIFE_YEARS,
    ensemble: bool = False,
    **model_kw,
) -> pd.DataFrame:
    predictions = walk_forward_predictions(dataset, seasons, half_life=half_life, **model_kw)
    if predictions.empty:
        return pd.DataFrame()

    if ensemble:
        return report_from_predictions(rolling_blend_weights(predictions), target=target)

    rows = []
    for season, part in predictions.groupby("season"):
        part = part.copy()
        part["prob_norm"] = normalise_per_race(
            part[f"p_{target}"].to_numpy(), part["race_id"].to_numpy()
        )
        y = part[target].to_numpy(dtype=int)
        row = {"season": int(season), "train_races": int(part["train_races"].iloc[0])}
        row.update(probability_metrics(y, part[f"p_{target}"].to_numpy()))
        row.update(race_metrics(part, "prob_norm", truth_col=target))
        baseline = part.copy()
        baseline["prob"] = -baseline["grid"]
        base = race_metrics(baseline, "prob", truth_col=target)
        row["baseline_podium_hit_rate"] = base.get("podium_hit_rate")
        row["baseline_exact_podium_rate"] = base.get("exact_podium_rate")
        row["baseline_winner_top1_rate"] = base.get("winner_top1_rate")
        row["lift_vs_grid"] = row.get("podium_hit_rate", 0) - base.get("podium_hit_rate", 0)
        row["winner_lift_vs_pole"] = (
            row.get("winner_top1_rate", 0) - base.get("winner_top1_rate", 0)
        )
        rows.append(row)
    return pd.DataFrame(rows)


def permutation_importance_report(model, dataset: pd.DataFrame, target: str = "podium",
                                  n_repeats: int = 5) -> pd.DataFrame:
    from sklearn.inspection import permutation_importance

    X = dataset[FEATURES].to_numpy(dtype=float)
    y = dataset[target].to_numpy(dtype=int)
    result = permutation_importance(
        model, X, y, n_repeats=n_repeats, random_state=RANDOM_STATE,
        scoring="roc_auc", n_jobs=-1,
    )
    return (
        pd.DataFrame(
            {
                "feature": FEATURES,
                "importance": result.importances_mean,
                "std": result.importances_std,
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def fit_all_heads(dataset: pd.DataFrame, **kw) -> dict:
    reference = dataset["date"].max()
    return {t: fit(dataset, target=t, reference=reference, **kw) for t in TARGETS}
