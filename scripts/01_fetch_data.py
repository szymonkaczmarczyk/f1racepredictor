from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import CURRENT_SEASON, FIRST_SEASON, PROCESSED_DIR
from src.ingest import ergast, openf1, tables, weather_history


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="ignore the on-disk cache")
    parser.add_argument("--from-season", type=int, default=FIRST_SEASON)
    parser.add_argument("--to-season", type=int, default=CURRENT_SEASON)
    args = parser.parse_args()

    raw_races: dict[int, list] = {}
    raw_results: dict[int, list] = {}
    raw_quali: dict[int, list] = {}
    raw_sprint: dict[int, list] = {}

    for season in range(args.from_season, args.to_season + 1):
        refresh = args.refresh or season >= CURRENT_SEASON
        print(f"  {season} ...", end=" ", flush=True)
        raw_races[season] = ergast.races(season, refresh=refresh)
        raw_results[season] = ergast.results(season, refresh=refresh)
        raw_quali[season] = ergast.qualifying(season, refresh=refresh)
        if season >= 2021:
            raw_sprint[season] = ergast.sprint(season, refresh=refresh)
        n_res = sum(len(r.get("Results", [])) for r in raw_results[season])
        print(f"{len(raw_races[season])} races, {n_res} results")

    print("\nBuilding tables ...")
    races = tables.build_races(raw_races)
    results = tables.build_results(raw_results)
    quali = tables.build_qualifying(raw_quali)
    sprint = tables.build_sprint(raw_sprint)

    for name, df in [
        ("races", races),
        ("results", results),
        ("qualifying", quali),
        ("sprint", sprint),
    ]:
        path = PROCESSED_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  {name:12s} {len(df):6d} rows -> {path.relative_to(PROCESSED_DIR.parent.parent)}")

    try:
        rows = openf1.meetings(args.to_season, refresh=True)
        cancelled = [m["meeting_name"] for m in rows if m.get("is_cancelled")]
        print(f"  openf1       {len(rows):6d} meetings"
              + (f" (cancelled: {', '.join(cancelled)})" if cancelled else ""))
    except Exception as exc:
        print(f"  openf1       unavailable ({exc}); keeping the cached schedule")

    weather = weather_history.update(races)
    weather_history.save(weather)
    wet = int((weather["wet_index"] >= 0.35).sum())
    print(f"  weather      {len(weather):6d} races measured, {wet} wet")

    seasons = sorted(results["season"].unique())
    print(f"\nSeasons {seasons[0]}-{seasons[-1]}, "
          f"{results['race_id'].nunique()} races, "
          f"{results['driver_id'].nunique()} drivers, "
          f"{results['constructor_id'].nunique()} constructors.")


if __name__ == "__main__":
    main()
