from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path
from threading import Timer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import MODEL_DIR
from src.app.server import app, predictor, start_background_sync

PORT = int(os.environ.get("F1_PORT", "5050"))


def main() -> None:
    if not (MODEL_DIR / "podium_model.joblib").exists():
        raise SystemExit(
            "No trained model found. Run, in order:\n"
            "  py scripts/01_fetch_data.py\n"
            "  py scripts/01b_fetch_pitstops.py\n"
            "  py scripts/02_build_features.py\n"
            "  py scripts/03_train.py"
        )
    p = predictor()
    print(f"Model trained through {p.trained_through} "
          f"({p.seasons[0]}-{p.seasons[1]}), {len(p.catalogue)} circuits, "
          f"{len(p.drivers)} drivers.")
    start_background_sync()
    url = f"http://127.0.0.1:{PORT}"
    print(f"Serving on {url}  (Ctrl+C to stop)")
    Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)


if __name__ == "__main__":
    main()
