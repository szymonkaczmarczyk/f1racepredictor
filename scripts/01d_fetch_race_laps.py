from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.config import CURRENT_SEASON, PROCESSED_DIR
from src.ingest import race_pace
from src.ingest.track_meta import DEGRADATION_YEARS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-season", type=int, default=CURRENT_SEASON - DEGRADATION_YEARS + 1)
    args = parser.parse_args()

    races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv", usecols=["race_id"])
    run = races[(races["season"] >= args.from_season) & races["race_id"].isin(results["race_id"])]

    fetched = failures = 0
    started = time.time()
    for row in run.itertuples(index=False):
        if (race_pace.CACHE_DIR / f"{row.race_id}.json").exists():
            continue
        try:
            payload = race_pace.fetch_race(int(row.season), row.date, row.race_id)
            failures = 0
        except Exception as exc:
            failures += 1
            print(f"  {row.race_id} failed: {exc}", flush=True)
            if failures >= 3:
                print("  three failures in a row, stopping; run again later to continue")
                break
            time.sleep(30)
            continue
        fetched += bool(payload)
        print(f"  {row.race_id} {row.race_name[:28]:28s} "
              f"{'ok' if payload else 'no data'}  ({time.time() - started:.0f}s)", flush=True)

    frame = race_pace.table(races)
    race_pace.save(frame)
    print(f"\n{fetched} races fetched; {len(frame)} races with measured degradation")


if __name__ == "__main__":
    main()
