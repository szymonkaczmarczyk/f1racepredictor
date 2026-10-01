from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch the latest results, rebuild features and refit the model if needed."
    )
    parser.add_argument("--full", action="store_true",
                        help="rerun the full walk-forward validation as well (minutes)")
    args = parser.parse_args()
    try:
        state = pipeline.run(full_validation=args.full)
    except pipeline.SyncBusy as exc:
        raise SystemExit(str(exc))
    print(json.dumps(state, indent=1))


if __name__ == "__main__":
    main()
