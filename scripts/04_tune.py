from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.config import MODEL_DIR, PROCESSED_DIR
from src.models import train as T

SEASONS = list(range(2016, 2027))

CURRENT = dict(half_life=8.0, learning_rate=0.05, max_iter=400, max_leaf_nodes=31,
               min_samples_leaf=60, l2_regularization=5.0, max_features=0.6)

PRESETS = {
    "current": {
        "current": dict(CURRENT),
        "leaf60": {**CURRENT, "min_samples_leaf": 60},
        "leaf25": {**CURRENT, "min_samples_leaf": 25},
        "leaves15": {**CURRENT, "max_leaf_nodes": 15},
        "iter300": {**CURRENT, "max_iter": 300},
        "slow900": {**CURRENT, "learning_rate": 0.03, "max_iter": 900},
        "feat0.8": {**CURRENT, "max_features": 0.8},
        "feat0.4": {**CURRENT, "max_features": 0.4},
        "hl6": {**CURRENT, "half_life": 6.0},
        "hl12": {**CURRENT, "half_life": 12.0},
    },
    "weighting": {
        "hl3": dict(half_life=3.0),
        "hl5": dict(half_life=5.0),
        "hl8": dict(half_life=8.0),
        "flat": dict(half_life=0),
        "hl5-deep": dict(half_life=5.0, max_leaf_nodes=63, min_samples_leaf=15,
                         learning_rate=0.04, max_iter=700),
        "hl5-shallow": dict(half_life=5.0, max_leaf_nodes=15, min_samples_leaf=60,
                            learning_rate=0.06, max_iter=400),
        "hl5-reg": dict(half_life=5.0, l2_regularization=5.0, min_samples_leaf=40,
                        max_features=0.6),
        "hl5-slow": dict(half_life=5.0, learning_rate=0.03, max_iter=900),
        "mono-hl5": dict(half_life=5.0, monotonic=True),
    },
    "finalists": {
        "hl8": dict(half_life=8.0),
        "hl5-reg": dict(half_life=5.0, l2_regularization=5.0, min_samples_leaf=40,
                        max_features=0.6),
        "hl8-reg": dict(half_life=8.0, l2_regularization=5.0, min_samples_leaf=40,
                        max_features=0.6),
        "hl8-reg-shallow": dict(half_life=8.0, l2_regularization=5.0, min_samples_leaf=60,
                                max_features=0.6, max_leaf_nodes=15, learning_rate=0.06,
                                max_iter=400),
        "hl8-shallow": dict(half_life=8.0, max_leaf_nodes=15, min_samples_leaf=60,
                            learning_rate=0.06, max_iter=400),
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=list(PRESETS), default="weighting")
    parser.add_argument("--ensemble", action="store_true",
                        help="rank by all three heads combined, as the app does")
    args = parser.parse_args()

    configs = {k: dict(v) for k, v in PRESETS[args.preset].items()}
    dataset = pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["date"])
    rows = []
    print(f"preset={args.preset}  ensemble={args.ensemble}  seasons={SEASONS[0]}-{SEASONS[-1]}")

    header = (f"{'config':>18} {'AUC':>7} {'logloss':>8} {'brier':>7} {'w.brier':>8} {'podium@3':>9} "
              f"{'grid@3':>7} {'lift':>8} {'winner':>7} {'pole':>6} {'w.lift':>7} {'secs':>6}")
    print(header)
    print("-" * len(header))

    for name, cfg in configs.items():
        started = time.time()
        half_life = cfg.pop("half_life")
        report = T.walk_forward(dataset, SEASONS, half_life=half_life,
                                ensemble=args.ensemble, **cfg)
        cfg["half_life"] = half_life
        m = report.mean(numeric_only=True)
        elapsed = time.time() - started
        rows.append({"config": name, **cfg, **{k: float(v) for k, v in m.items()},
                     "seconds": round(elapsed, 1)})
        print(f"{name:>18} {m['roc_auc']:>7.3f} {m['log_loss']:>8.4f} {m['brier']:>7.4f} "
              f"{m.get('win_brier', float('nan')):>8.4f} {m['podium_hit_rate']:>9.3f} {m['baseline_podium_hit_rate']:>7.3f} "
              f"{m['lift_vs_grid']:>+8.3f} {m['winner_top1_rate']:>7.3f} "
              f"{m['baseline_winner_top1_rate']:>6.3f} {m['winner_lift_vs_pole']:>+7.3f} "
              f"{elapsed:>6.0f}")

    table = pd.DataFrame(rows).sort_values("podium_hit_rate", ascending=False)
    best = table.iloc[0]
    print("-" * len(header))
    print(f"Best on podium@3: {best['config']} "
          f"({best['podium_hit_rate']:.3f}, {best['lift_vs_grid']:+.3f} vs grid)")

    suffix = f"_{args.preset}" + ("_ensemble" if args.ensemble else "")
    path = MODEL_DIR / f"tuning_report{suffix}.json"
    path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(f"Saved -> {path}")


if __name__ == "__main__":
    main()
