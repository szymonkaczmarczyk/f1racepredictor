from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.config import CURRENT_SEASON, PROCESSED_DIR
from src.ingest import practice


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-season", type=int, default=practice.FIRST_PRACTICE_SEASON)
    parser.add_argument("--refresh-upcoming", action="store_true",
                        help="refetch the next race's weekend, whose practice may still be running")
    args = parser.parse_args()

    races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
    results = pd.read_csv(PROCESSED_DIR / "results.csv", parse_dates=["date"])
    now = pd.Timestamp.now()
    window = races[(races["season"] >= args.from_season) & (races["season"] <= CURRENT_SEASON)]
    window = window[window["date"] - pd.Timedelta(days=3) <= now]
    upcoming = window[~window["race_id"].isin(results["race_id"])]["race_id"]

    fetched = missing = failures = 0
    started = time.time()
    for row in window.itertuples(index=False):
        refresh = args.refresh_upcoming and row.race_id in set(upcoming)
        cached = (practice.CACHE_DIR / f"{row.race_id}.json").exists()
        if cached and not refresh:
            continue
        try:
            payload = practice.fetch_weekend(int(row.season), row.date, row.race_id, refresh=refresh)
            failures = 0
        except Exception as exc:
            failures += 1
            print(f"  {row.race_id} failed: {exc}", flush=True)
            if failures >= 3:
                print("  three failures in a row, stopping; run again later to continue")
                break
            time.sleep(30)
            continue
        if payload:
            fetched += 1
        else:
            missing += 1
        print(f"  {row.race_id} {row.race_name[:28]:28s} "
              f"{'ok' if payload else 'no data'}  ({time.time() - started:.0f}s)", flush=True)

    frame = practice.table(races, results)
    practice.save(frame)
    print(f"\n{fetched} weekends fetched, {missing} without data; "
          f"{frame['race_id'].nunique()} weekends in practice.csv")


if __name__ == "__main__":
    main()
