from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.config import CURRENT_SEASON, PROCESSED_DIR, RAW_DIR
from src.ingest import ergast
from src.ingest.tables import race_id

FIRST_PITSTOP_SEASON = 2011


def cached_rounds() -> list[Path]:
    return sorted(RAW_DIR.glob("*_pitstops.json"))


def _has_stops(endpoint: str) -> bool:
    path = ergast._cache_path(endpoint)
    if not path.exists():
        return False
    try:
        races = json.loads(path.read_text(encoding="utf-8")).get("RaceTable", {}).get("Races", [])
    except (OSError, ValueError):
        return False
    return any(race.get("PitStops") for race in races)


def assemble() -> pd.DataFrame:
    rows = []
    for path in cached_rounds():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for race in data.get("RaceTable", {}).get("Races", []):
            rid = race_id(race["season"], race["round"])
            for stop in race.get("PitStops", []):
                rows.append(
                    {
                        "race_id": rid,
                        "season": int(race["season"]),
                        "round": int(race["round"]),
                        "driver_id": stop["driverId"],
                        "stop": int(stop["stop"]),
                        "lap": int(stop["lap"]),
                        "duration": stop.get("duration"),
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--assemble-only", action="store_true",
                        help="skip the API entirely and rebuild from the cache")
    parser.add_argument("--from-season", type=int, default=FIRST_PITSTOP_SEASON)
    args = parser.parse_args()

    if not args.assemble_only:
        races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
        today = pd.Timestamp.today().normalize()
        for season in range(args.from_season, CURRENT_SEASON + 1):
            held = races[(races["season"] == season) & (races["date"] < today)]
            rounds = held["round"].tolist()
            fetched = skipped = 0
            for rnd in rounds:
                endpoint = f"{season}/{rnd}/pitstops"
                refresh = args.refresh or (
                    season >= CURRENT_SEASON and not _has_stops(endpoint)
                )
                try:
                    ergast.fetch(endpoint, refresh=refresh)
                    fetched += 1
                except ergast.ErgastError as exc:
                    skipped += 1
                    if "rate limited" in str(exc):
                        print(f"  {season}: rate limited after {fetched} rounds — "
                              f"stopping. Re-run later to continue.")
                        rounds = []
                        break
            if fetched or skipped:
                print(f"  {season}: {fetched} rounds cached"
                      + (f", {skipped} unavailable" if skipped else ""))
            if not rounds:
                break

    df = assemble()
    path = PROCESSED_DIR / "pitstops.csv"
    df.to_csv(path, index=False)

    if df.empty:
        print("\nNo pit stop data cached yet.")
        return
    covered = df.groupby("season")["race_id"].nunique()
    print(f"\n{len(df)} stops across {df['race_id'].nunique()} races -> {path.name}")
    print(f"  seasons {int(covered.index.min())}-{int(covered.index.max())}: "
          + ", ".join(f"{int(s)}({n})" for s, n in covered.items()))


if __name__ == "__main__":
    main()
