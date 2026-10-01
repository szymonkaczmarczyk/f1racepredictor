from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import pandas as pd

from src.config import CIRCUIT_DIR, MODEL_DIR, PROCESSED_DIR
from src.features import prequali, registry
from src.features.build import FEATURES, build_dataset
from src.features.weather import estimate_wet_index
from src.ingest import circuits as circuit_geo
from src.ingest import practice, race_pace, track_meta, track_status, weather_history
from src.ingest.schedule import build_calendar


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wet-source", choices=("weather", "pace"), default="weather",
                        help="measured rain around the start (default), or the old index "
                             "read back from race pace")
    args = parser.parse_args()

    races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv", parse_dates=["date"])
    quali = pd.read_csv(PROCESSED_DIR / "qualifying.csv")
    pitstops_path = PROCESSED_DIR / "pitstops.csv"
    pitstops = pd.read_csv(pitstops_path) if pitstops_path.exists() else None

    print("Circuit geometry ...")
    circuit_ids = sorted(races["circuit_id"].unique())
    geometry = circuit_geo.build_all(circuit_ids)
    raw_geo = {
        cid: json.loads((CIRCUIT_DIR / f"{circuit_geo.GEO_ID[cid]}.geojson").read_text(encoding="utf-8"))
        for cid in circuit_ids
        if cid in circuit_geo.GEO_ID and (CIRCUIT_DIR / f"{circuit_geo.GEO_ID[cid]}.geojson").exists()
    }
    print(f"  {len(geometry)}/{len(circuit_ids)} circuits traced")

    print("Current season calendar ...")
    calendar = build_calendar(races, results, quali)
    done = sum(1 for r in calendar if r["completed"])
    print(f"  {done}/{len(calendar)} rounds run")

    print("Circuit catalogue ...")
    catalogue = track_meta.build_catalogue(
        races, results, geometry, raw_geo, pitstops,
        always_include={r["circuit_id"] for r in calendar},
        degradation=race_pace.load(),
        track_status=track_status.load(),
    )
    track_meta.save(catalogue, PROCESSED_DIR / "circuit_catalogue.json")
    debuts = [c["circuit_id"] for c in catalogue.values() if c.get("debut")]
    print(f"  {len(catalogue)} circuits" + (f" (debut, no history: {', '.join(debuts)})" if debuts else ""))

    print("Driver and team dossiers ...")
    current = int(races["season"].max())
    registry.save(registry.build_drivers(results, current), PROCESSED_DIR / "drivers.json")
    registry.save(registry.build_teams(results, current), PROCESSED_DIR / "teams.json")
    registry.save(
        registry.build_driver_track_history(results, current),
        PROCESSED_DIR / "driver_track_history.json",
    )
    print(f"  {results['driver_id'].nunique()} drivers, "
          f"{results['constructor_id'].nunique()} constructors")

    wet = weather_history.load() if args.wet_source == "weather" else pd.Series(dtype=float)
    if wet.empty:
        print("Estimating race conditions from pace (no measured weather) ...")
        wet = estimate_wet_index(results)
    else:
        print("Race conditions from measured weather ...")
    wet_races = int((wet >= 0.35).sum())
    print(f"  {wet_races} of {len(wet)} races wet "
          f"({wet_races / max(len(wet), 1):.1%})")

    print("Feature matrix ...")
    recorder = prequali.ExpectedGridRecorder(quali, races)
    dataset, store = build_dataset(
        results, quali, races, catalogue, wet_index=wet, practice=practice.load(),
        before_update=recorder,
    )
    path = PROCESSED_DIR / "features.csv"
    dataset.to_csv(path, index=False)
    expected = recorder.dataset(dataset)
    expected.to_csv(PROCESSED_DIR / "features_prequali.csv", index=False)
    print(f"  {len(expected)} rows with the grid as it was expected before qualifying")

    joblib.dump(store, MODEL_DIR / "feature_store.joblib", compress=3)

    coverage = dataset[FEATURES].notna().mean().sort_values()
    print(f"  {len(dataset)} rows x {len(FEATURES)} features -> {path.name}")
    print(f"  podium rate {dataset['podium'].mean():.3f}")
    print("\n  Sparsest features (coverage):")
    for name, value in coverage.head(6).items():
        print(f"    {name:26s} {value:6.1%}")


if __name__ == "__main__":
    main()
