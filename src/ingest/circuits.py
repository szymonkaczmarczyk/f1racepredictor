from __future__ import annotations

import json
import math
from pathlib import Path

import requests

from src.config import CIRCUIT_DIR, CIRCUIT_GEO_BASE

GEO_ID = {
    "albert_park": "au-1953",
    "americas": "us-2012",
    "bahrain": "bh-2002",
    "baku": "az-2016",
    "catalunya": "es-1991",
    "estoril": "pt-1972",
    "galvez": "ar-1952",
    "hockenheimring": "de-1932",
    "hungaroring": "hu-1986",
    "imola": "it-1953",
    "indianapolis": "us-1909",
    "interlagos": "br-1940",
    "istanbul": "tr-2005",
    "jacarepagua": "br-1977",
    "jeddah": "sa-2021",
    "kyalami": "za-1961",
    "losail": "qa-2004",
    "madring": "es-2026",
    "magny_cours": "fr-1960",
    "marina_bay": "sg-2008",
    "miami": "us-2022",
    "monaco": "mc-1929",
    "monza": "it-1922",
    "mugello": "it-1914",
    "nurburgring": "de-1927",
    "portimao": "pt-2008",
    "red_bull_ring": "at-1969",
    "ricard": "fr-1969",
    "rodriguez": "mx-1962",
    "sepang": "my-1999",
    "shanghai": "cn-2004",
    "silverstone": "gb-1948",
    "sochi": "ru-2014",
    "spa": "be-1925",
    "suzuka": "jp-1962",
    "vegas": "us-2023",
    "villeneuve": "ca-1978",
    "watkins_glen": "us-1956",
    "yas_marina": "ae-2009",
    "zandvoort": "nl-1948",
}

STREET_CIRCUITS = {
    "monaco", "baku", "marina_bay", "jeddah", "vegas", "miami", "albert_park",
    "valencia", "detroit", "phoenix", "adelaide", "madring",
}

VIEW_W, VIEW_H, PAD = 1000.0, 620.0, 46.0
M_PER_DEG = 111_320.0

RESAMPLE_M = 8.0
SMOOTH_WINDOW = 3
CORNER_RATE = 0.06
STRAIGHT_M = 20.0
MIN_CORNER_DEG = 18.0


def _resample(points: list[tuple[float, float]], step: float) -> list[tuple[float, float]]:
    out = [points[0]]
    carry = 0.0
    for a, b in zip(points, points[1:]):
        d = math.dist(a, b)
        if d < 1e-9:
            continue
        t = step - carry
        while t <= d:
            out.append((a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d))
            t += step
        carry = (carry + d) % step
    return out


def detect_corners(metric: list[tuple[float, float]]) -> list[float]:
    if len(metric) < 6:
        return []

    pts = _resample(metric, RESAMPLE_M)
    heading = [
        math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]))
        for i in range(len(pts) - 1)
    ]
    turn = [(heading[i + 1] - heading[i] + 180) % 360 - 180 for i in range(len(heading) - 1)]

    half = SMOOTH_WINDOW // 2
    if half:
        turn = [
            sum(turn[max(0, i - half):i + half + 1]) / len(turn[max(0, i - half):i + half + 1])
            for i in range(len(turn))
        ]

    threshold = CORNER_RATE * RESAMPLE_M
    apexes: list[float] = []
    accum, sign, gap, start = 0.0, 0, 0.0, 0

    def close(end: int) -> None:
        if abs(accum) >= MIN_CORNER_DEG:
            apexes.append((start + end) / 2 * RESAMPLE_M)

    for i, delta in enumerate(turn):
        if abs(delta) < threshold:
            gap += RESAMPLE_M
            if gap > STRAIGHT_M:
                close(i)
                accum, sign = 0.0, 0
            continue
        this_sign = 1 if delta > 0 else -1
        if sign and this_sign != sign:
            close(i)
            accum, start = 0.0, i
        if accum == 0.0:
            start = i
        sign, gap = this_sign, 0.0
        accum += delta
    close(len(turn) - 1)
    return apexes


def _geo_path(geo_id: str) -> Path:
    return CIRCUIT_DIR / f"{geo_id}.geojson"


def download(geo_id: str, *, refresh: bool = False) -> dict | None:
    path = _geo_path(geo_id)
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    url = f"{CIRCUIT_GEO_BASE}/circuits/{geo_id}.geojson"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception:
        return None
    path.write_text(response.text, encoding="utf-8")
    return response.json()


def to_svg(geojson: dict) -> dict | None:
    feature = next(
        (f for f in geojson.get("features", []) if f["geometry"]["type"] == "LineString"),
        None,
    )
    if feature is None:
        return None

    coords = feature["geometry"]["coordinates"]
    if len(coords) < 8:
        return None

    lat0 = sum(c[1] for c in coords) / len(coords)
    k = math.cos(math.radians(lat0))
    pts = [(c[0] * k * M_PER_DEG, c[1] * M_PER_DEG) for c in coords]

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)
    if span_x <= 0 or span_y <= 0:
        return None

    scale = min((VIEW_W - 2 * PAD) / span_x, (VIEW_H - 2 * PAD) / span_y)
    off_x = (VIEW_W - span_x * scale) / 2
    off_y = (VIEW_H - span_y * scale) / 2

    def project(p):
        x = (p[0] - min(xs)) * scale + off_x
        y = VIEW_H - ((p[1] - min(ys)) * scale + off_y)
        return round(x, 1), round(y, 1)

    screen = [project(p) for p in pts]
    d = f"M {screen[0][0]} {screen[0][1]} " + " ".join(
        f"L {x} {y}" for x, y in screen[1:]
    )
    if math.dist(screen[0], screen[-1]) < 30:
        d += " Z"

    props = feature.get("properties", {})
    start, nxt = screen[0], screen[min(4, len(screen) - 1)]
    angle = math.degrees(math.atan2(nxt[1] - start[1], nxt[0] - start[0]))

    apexes = detect_corners(pts)
    corners = [
        {"n": i + 1, "x": p[0], "y": p[1]}
        for i, p in enumerate(_points_at(screen, [a * scale for a in apexes]))
    ]

    return {
        "path": d,
        "view_box": f"0 0 {VIEW_W:.0f} {VIEW_H:.0f}",
        "length_m": props.get("length"),
        "altitude_m": props.get("altitude"),
        "opened": props.get("opened"),
        "start": {"x": start[0], "y": start[1], "angle": round(angle, 1)},
        "corners": corners,
    }


def _points_at(polyline: list[tuple[float, float]], distances: list[float]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    if not distances:
        return out
    remaining = sorted(distances)
    travelled, i = 0.0, 0
    for a, b in zip(polyline, polyline[1:]):
        seg = math.dist(a, b)
        while i < len(remaining) and remaining[i] <= travelled + seg:
            t = (remaining[i] - travelled) / seg if seg > 0 else 0.0
            out.append((round(a[0] + (b[0] - a[0]) * t, 1), round(a[1] + (b[1] - a[1]) * t, 1)))
            i += 1
        if i >= len(remaining):
            break
        travelled += seg
    while len(out) < len(remaining):
        out.append((round(polyline[-1][0], 1), round(polyline[-1][1], 1)))
    return out


def build_all(circuit_ids: list[str], *, refresh: bool = False) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for cid in circuit_ids:
        geo_id = GEO_ID.get(cid)
        if not geo_id:
            continue
        raw = download(geo_id, refresh=refresh)
        if not raw:
            continue
        svg = to_svg(raw)
        if svg:
            out[cid] = svg
    return out
