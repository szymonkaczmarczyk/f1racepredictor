from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.app.server import app

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "ok  " if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


def main() -> None:
    client = app.test_client()

    print("GET /")
    page = client.get("/")
    check("index renders", page.status_code == 200 and b"Track and Race Conditions" in page.data)

    print("\nGET /api/bootstrap")
    boot = client.get("/api/bootstrap")
    check("responds", boot.status_code == 200)
    data = boot.get_json()
    tracks, drivers = data["tracks"], data["drivers"]
    on_calendar = [t for t in tracks if t["on_calendar"]]
    with_map = [t for t in tracks if t["has_map"]]
    active = [d for d in drivers if d["active"]]

    check("tracks present", len(tracks) >= 20, f"{len(tracks)} circuits")
    check("calendar circuits flagged", len(on_calendar) >= 15, f"{len(on_calendar)} on this year's calendar")
    check("layouts available", len(with_map) >= 20, f"{len(with_map)} drawable")
    check("drivers present", len(active) >= 15, f"{len(active)} active of {len(drivers)}")
    check("next race known", data["next_race"] is not None,
          data["next_race"]["race_name"] if data["next_race"] else "none")
    check("model metrics exposed", bool(data["model"]["summary"]),
          f"AUC {data['model']['summary'].get('roc_auc', 0):.3f}")

    circuit = (data["next_race"] or on_calendar[0])["circuit_id"]

    print(f"\nGET /api/track/{circuit}")
    track = client.get(f"/api/track/{circuit}").get_json()
    geo = track.get("geometry", {})
    check("track metadata", track.get("laps") is not None,
          f"{track['name']}, {track.get('laps')} laps, {track.get('distance_km')} km")
    check("layout is drawable", bool(geo.get("path")),
          f"{len(geo.get('corners', []))} corners detected")
    check("difficulty and degradation set",
          track.get("track_difficulty") is not None and track.get("tyre_degradation") is not None,
          f"difficulty {track.get('track_difficulty')}/10, degradation {track.get('tyre_degradation')}/10")

    print("\nGET /api/lineup")
    lineup = client.get("/api/lineup").get_json()["entries"]
    check("latest grid loads", len(lineup) >= 15, f"{len(lineup)} cars")

    print("\nGET /api/driver/<id>")
    who = lineup[0]["driver_id"]
    driver = client.get(f"/api/driver/{who}").get_json()
    check("driver dossier", "career" in driver,
          f"{driver.get('name')}: {driver['career']['races']} starts, "
          f"{driver['career']['podiums']} podiums")
    check("per-circuit history", isinstance(driver.get("tracks"), dict),
          f"{len(driver.get('tracks', {}))} circuits raced")
    check("unknown driver is a 404", client.get("/api/driver/nobody").status_code == 404)

    print("\nPOST /api/predict — dry")
    body = {
        "circuit_id": circuit,
        "weather": "dry",
        "tyre_degradation": track.get("tyre_degradation"),
        "track_difficulty": track.get("track_difficulty"),
        "laps": track.get("laps"),
        "entries": lineup,
    }
    dry = client.post("/api/predict", json=body).get_json()
    check("prediction returns", "entries" in dry and len(dry["entries"]) == len(lineup))
    podium_total = sum(e["p_podium"] for e in dry["entries"])
    win_total = sum(e["p_win"] for e in dry["entries"])
    check("podium probabilities sum to 3", abs(podium_total - 3) < 0.05, f"{podium_total:.3f}")
    check("win probabilities sum to 1", abs(win_total - 1) < 0.05, f"{win_total:.3f}")
    check("order is a permutation",
          sorted(e["expected_position"] for e in dry["entries"]) == list(range(1, len(lineup) + 1)))
    check("explanations attached", all(isinstance(e["notes"], list) for e in dry["entries"]))

    print("\n  predicted podium:")
    for e in dry["entries"][:3]:
        print(f"    P{e['expected_position']}  {e['name']:22s} {e['team_name']:16s} "
              f"from P{e['grid']:<2d} podium {e['p_podium']:.0%}  win {e['p_win']:.0%}")
        for note in e["notes"]:
            print(f"          · {note}")

    print("\nPOST /api/predict — heavy rain, same grid")
    wet = client.post("/api/predict", json={**body, "weather": "heavy_rain"}).get_json()
    dry_top = [e["driver_id"] for e in dry["entries"][:3]]
    wet_top = [e["driver_id"] for e in wet["entries"][:3]]
    dry_p = {e["driver_id"]: e["p_podium"] for e in dry["entries"]}
    moved = max(abs(e["p_podium"] - dry_p[e["driver_id"]]) for e in wet["entries"])
    check("weather changes the prediction", moved > 0.005,
          f"largest podium probability shift {moved:.1%}")
    print(f"    dry podium: {', '.join(dry_top)}")
    print(f"    wet podium: {', '.join(wet_top)}")

    print("\nPOST /api/predict — bad input")
    check("unknown circuit rejected",
          client.post("/api/predict", json={**body, "circuit_id": "nowhere"}).status_code == 400)
    check("empty grid rejected",
          client.post("/api/predict", json={**body, "entries": []}).status_code == 400)

    print("\n" + ("All checks passed." if not FAILURES
                  else f"{len(FAILURES)} FAILED: " + ", ".join(FAILURES)))
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
