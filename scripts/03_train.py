from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import pandas as pd

from src.config import (
    CURRENT_SEASON,
    MODEL_DIR,
    PROCESSED_DIR,
    RECENCY_HALF_LIFE_YEARS,
    VALIDATION_SEASONS,
)
from src.features.build import FEATURES, TARGETS
from src.models import grid_prior
from src.models import train as T

COLUMNS = [
    ("season", "season", 6, ">6.0f"),
    ("races", "races", 5, ">5.0f"),
    ("roc_auc", "AUC", 6, ">6.3f"),
    ("log_loss", "logloss", 7, ">7.3f"),
    ("brier", "brier", 6, ">6.3f"),
    ("win_brier", "w.brier", 7, ">7.3f"),
    ("points_brier", "p.brier", 7, ">7.3f"),
    ("podium_hit_rate", "podium@3", 8, ">8.3f"),
    ("baseline_podium_hit_rate", "grid@3", 7, ">7.3f"),
    ("lift_vs_grid", "lift", 7, ">+7.3f"),
    ("exact_podium_rate", "exact", 6, ">6.3f"),
    ("winner_top1_rate", "winner", 7, ">7.3f"),
    ("baseline_winner_top1_rate", "pole", 6, ">6.3f"),
    ("winner_lift_vs_pole", "w.lift", 7, ">+7.3f"),
]


def print_report(report: pd.DataFrame) -> None:
    header = " ".join(format(title, f">{w}") for _, title, w, _ in COLUMNS)
    rule = "-" * len(header)
    row_text = lambda values: " ".join(
        format(v, spec) for v, (_, _, _, spec) in zip(values, COLUMNS)
    )

    print(header)
    print(rule)
    for row in report[[c for c, _, _, _ in COLUMNS]].itertuples(index=False):
        print(row_text(row))
    print(rule)
    means = report.mean(numeric_only=True)
    print(row_text([means[c] for c, _, _, _ in COLUMNS]))


def load_prequali() -> pd.DataFrame | None:
    path = PROCESSED_DIR / "features_prequali.csv"
    if not path.exists():
        return None
    return pd.read_csv(path, parse_dates=["date"])


def prequali_heads(dataset: pd.DataFrame, weights: dict) -> dict:
    return {
        "models": T.fit_all_heads(dataset),
        "grid_priors": {t: grid_prior.build_prior(dataset, t) for t in TARGETS},
        "blend_weights": weights,
    }


def save_bundle(dataset: pd.DataFrame, models: dict, weights: dict,
                prequali: dict | None = None) -> dict:
    bundle = {
        "models": models,
        "features": FEATURES,
        "targets": TARGETS,
        "grid_priors": {t: grid_prior.build_prior(dataset, t) for t in TARGETS},
        "blend_weights": weights,
        "trained_through": str(dataset["date"].max().date()),
        "seasons": [int(dataset["season"].min()), int(dataset["season"].max())],
        "recency_half_life_years": RECENCY_HALF_LIFE_YEARS,
        "params": T.DEFAULT_PARAMS,
    }
    if prequali:
        bundle["prequali"] = prequali
    path = MODEL_DIR / "podium_model.joblib"
    tmp = path.with_suffix(".tmp")
    joblib.dump(bundle, tmp, compress=3)
    os.replace(tmp, path)
    print(f"Saved -> {path}")
    return bundle


def write_report(payload: dict) -> None:
    path = MODEL_DIR / "validation_report.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    print(f"Saved -> {path}")


def quick(dataset: pd.DataFrame) -> None:
    previous_path = MODEL_DIR / "podium_model.joblib"
    previous = joblib.load(previous_path) if previous_path.exists() else {}
    weights = previous.get("blend_weights", {}) or {t: grid_prior.DEFAULT_WEIGHT for t in TARGETS}
    print("Refitting final models (blend weights carried over) ...")
    expected = load_prequali()
    pre = None
    if expected is not None and not expected.empty:
        pre_weights = (previous.get("prequali") or {}).get("blend_weights") or weights
        pre = prequali_heads(expected, pre_weights)
    bundle = save_bundle(dataset, T.fit_all_heads(dataset), weights, pre)

    report_path = MODEL_DIR / "validation_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    payload.setdefault("validated_through", payload.get("trained_through"))
    payload["trained_through"] = bundle["trained_through"]
    write_report(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true",
                        help="refit the final models only, keeping the last validation")
    args = parser.parse_args()

    dataset = pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["date"])
    print(f"{len(dataset)} entries, seasons "
          f"{dataset['season'].min()}-{dataset['season'].max()}, "
          f"{dataset['race_id'].nunique()} races\n")
    if args.quick:
        quick(dataset)
        return

    print("Walk-forward validation (train on everything before each season).")
    print("Ordering is by all three heads combined, exactly as the app ranks them.")
    predictions = T.walk_forward_predictions(dataset, VALIDATION_SEASONS)
    if predictions.empty:
        raise SystemExit("no season had enough history to validate against")

    simulated = T.simulate_predictions(T.rolling_blend_weights(predictions))
    report = T.report_from_predictions(simulated)
    calibration = T.calibration_table(simulated)

    weights = T.fit_blend_weights(predictions)
    print("Blend weights against grid order (1.0 = ignore the grid prior):")
    for target, w in weights.items():
        print(f"  {target:14s} {w:.2f}")

    report_path = MODEL_DIR / "validation_raw.csv"
    report.to_csv(report_path, index=False)
    print(f"(saved raw report -> {report_path.name})\n")
    print_report(report)

    print("\nCalibration of the probabilities the app shows (predicted -> observed):")
    for target, rows in calibration.items():
        cells = "  ".join(f"{r['predicted']:.2f}->{r['observed']:.2f}" for r in rows)
        print(f"  {target:14s} {cells}")

    print("\nTraining final models on the full history ...")
    models = T.fit_all_heads(dataset)
    print("  " + ", ".join(TARGETS))

    print("\nPermutation importance (podium, scored on the final season):")
    last = dataset["season"].max()
    holdout = dataset[dataset["season"] == last]
    trained_before = T.fit(dataset[dataset["season"] < last], target="podium")
    importance = T.permutation_importance_report(trained_before, holdout)
    for row in importance.head(18).itertuples(index=False):
        bar = "#" * max(1, int(row.importance * 220))
        print(f"  {row.feature:26s} {row.importance:7.4f}  {bar}")

    pre, pre_payload = None, None
    expected = load_prequali()
    if expected is not None and not expected.empty:
        print("\nBefore qualifying: the same walk-forward, on the grid as it was expected.")
        pre_predictions = T.walk_forward_predictions(expected, VALIDATION_SEASONS)
        pre_report = T.report_from_predictions(T.simulate_predictions(T.rolling_blend_weights(pre_predictions)))
        pre_weights = T.fit_blend_weights(pre_predictions)
        print_report(pre_report)
        print("Blend weights before qualifying: " + ", ".join(f"{t} {w:.2f}" for t, w in pre_weights.items()))
        pre = prequali_heads(expected, pre_weights)
        pre_payload = {
            "validation": pre_report.to_dict(orient="records"),
            "summary": {k: float(v) for k, v in pre_report.mean(numeric_only=True).items()},
        }

    bundle = save_bundle(dataset, models, weights, pre)

    means = report.mean(numeric_only=True)
    payload = {
        "validation": report.to_dict(orient="records"),
        "summary": {k: float(v) for k, v in means.items()},
        "importance": importance.head(30).to_dict(orient="records"),
        "calibration": calibration,
        "trained_through": bundle["trained_through"],
        "validated_through": bundle["trained_through"],
        "current_season": CURRENT_SEASON,
    }
    if pre_payload:
        payload["prequali"] = pre_payload
    write_report(payload)


if __name__ == "__main__":
    main()
