from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from src.config import PODIUM_CUTOFF, PROCESSED_DIR, VALIDATION_SEASONS
from src.features.build import FEATURES
from src.models import train as T


def main() -> None:
    dataset = pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["date"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv",
                          usecols=["race_id", "driver_id", "outcome"])
    dataset = dataset.merge(results, on=["race_id", "driver_id"], how="left")
    seasons = [s for s in VALIDATION_SEASONS if s >= 2019]

    scored = []
    for season in seasons:
        train = dataset[dataset["season"] < season]
        test = dataset[dataset["season"] == season].copy()
        if test.empty:
            continue
        model = T.fit(train, target="podium", reference=train["date"].max())
        test["prob"] = model.predict_proba(test[FEATURES].to_numpy(dtype=float))[:, 1]
        scored.append(test)
    df = pd.concat(scored, ignore_index=True)
    print(f"Diagnosing {df['race_id'].nunique()} races from {seasons[0]}-{seasons[-1]}\n")

    swaps_right = swaps_wrong = 0
    agree_hits = model_hits = grid_hits = races = 0
    confident_swaps = []

    for race_id, race in df.groupby("race_id"):
        race = race.copy()
        actual = set(race.loc[race["podium"] == 1, "driver_id"])
        if not actual:
            continue
        races += 1
        by_model = race.sort_values("prob", ascending=False)
        by_grid = race.sort_values("grid")
        m_top, g_top = set(by_model.head(3)["driver_id"]), set(by_grid.head(3)["driver_id"])

        model_hits += len(m_top & actual)
        grid_hits += len(g_top & actual)
        agree_hits += len(m_top & g_top)

        promoted = m_top - g_top
        demoted = g_top - m_top
        for p in promoted:
            swaps_right += int(p in actual)
            swaps_wrong += int(p not in actual)
            row = race[race["driver_id"] == p].iloc[0]
            confident_swaps.append(
                {
                    "race": race_id,
                    "driver": row["driver_name"],
                    "grid": int(row["grid"]),
                    "prob": float(row["prob"]),
                    "podium": int(row["podium"]),
                    "replaced_grid": int(race[race["driver_id"].isin(demoted)]["grid"].min())
                    if len(demoted) else None,
                }
            )

    n_swaps = swaps_right + swaps_wrong
    print(f"Model top-3 agrees with grid top-3 on {agree_hits / (races * 3):.1%} of slots")
    print(f"podium@3  model {model_hits / (races * 3):.3f}   grid {grid_hits / (races * 3):.3f}")
    print(f"\nThe model overrode the grid {n_swaps} times "
          f"({n_swaps / races:.2f} per race)")
    if n_swaps:
        print(f"  right {swaps_right:4d}  ({swaps_right / n_swaps:.1%})")
        print(f"  wrong {swaps_wrong:4d}  ({swaps_wrong / n_swaps:.1%})")
        print(f"  a coin flip would be 50%; the driver being displaced podiums "
              f"{1 - swaps_right / n_swaps:.0%} of the time")

    swaps = pd.DataFrame(confident_swaps)
    if not swaps.empty:
        print("\nOverride accuracy by how confident the model was:")
        swaps["bucket"] = pd.cut(swaps["prob"], [0, .2, .3, .4, .5, 1.0])
        summary = swaps.groupby("bucket", observed=True).agg(
            n=("podium", "size"), hit_rate=("podium", "mean"), avg_grid=("grid", "mean")
        )
        print(summary.to_string(float_format=lambda v: f"{v:.2f}"))

        print("\nOverride accuracy by the grid slot promoted from:")
        swaps["from"] = pd.cut(swaps["grid"], [3, 5, 8, 12, 30],
                               labels=["P4-5", "P6-8", "P9-12", "P13+"])
        print(
            swaps.groupby("from", observed=True)
            .agg(n=("podium", "size"), hit_rate=("podium", "mean"))
            .to_string(float_format=lambda v: f"{v:.2f}")
        )

    print("\nWhat the baseline leaves on the table")
    top3 = df[df["grid"] <= PODIUM_CUTOFF]
    outside = df[df["grid"] > PODIUM_CUTOFF]
    print(f"  a top-three start converts to a podium {top3['podium'].mean():.1%} of the time")
    print(f"  a start outside it converts {outside['podium'].mean():.1%} of the time")
    print(f"  so overriding the grid trades a {top3['podium'].mean():.0%} pick for a "
          f"{outside['podium'].mean():.0%} one — it has to be a very good reason")

    missed = top3[top3["podium"] == 0]
    print(f"\n  when a top-three starter misses out ({len(missed)} cases), why:")
    print(missed["outcome"].value_counts(normalize=True).head(4)
          .to_string(float_format=lambda v: f"{v:.1%}"))


if __name__ == "__main__":
    main()
