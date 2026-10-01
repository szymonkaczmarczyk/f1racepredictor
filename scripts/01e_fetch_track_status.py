from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.config import CURRENT_SEASON, PROCESSED_DIR
from src.ingest import track_status


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch safety car, virtual safety car and red flag counts for every race run."
    )
    parser.add_argument("--from-season", type=int, default=track_status.FIRST_SEASON)
    args = parser.parse_args()

    races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv", usecols=["race_id"])
    run = set(results["race_id"])
    window = races[
        (races["season"] >= args.from_season)
        & (races["season"] <= CURRENT_SEASON)
        & races["race_id"].isin(run)
    ]

    fetched = missing = failures = 0
    started = time.time()
    for row in window.itertuples(index=False):
        if (track_status.CACHE_DIR / f"{row.race_id}.json").exists():
            continue
        try:
            payload = track_status.fetch_race(int(row.season), row.date, row.race_id)
            failures = 0
        except Exception as exc:
            failures += 1
            print(f"  {row.race_id} failed: {exc}", flush=True)
            if failures >= 3:
                print("  three failures in a row, stopping; run again later to continue")
                break
            time.sleep(10)
            continue
        if payload:
            fetched += 1
        else:
            missing += 1
        print(f"  {row.race_id} {row.race_name[:28]:28s} "
              f"{'ok' if payload else 'no data'}  ({time.time() - started:.0f}s)", flush=True)

    frame = track_status.table()
    track_status.save(frame)
    print(f"\n{fetched} races fetched, {missing} without data; {len(frame)} races in track_status.csv")


if __name__ == "__main__":
    main()
