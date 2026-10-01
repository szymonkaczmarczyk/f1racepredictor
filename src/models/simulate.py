from __future__ import annotations

import numpy as np

from src.config import PODIUM_CUTOFF

POINTS_PLACES = 10

GRID_RISK_TILT = 0.7

MIN_RETIREMENT = 0.02
MIN_INCIDENT = 0.003
MAX_RETIREMENT = 0.45

UNKNOWN_RETIREMENT = 0.14
UNKNOWN_INCIDENT = 0.05
UNKNOWN_MECHANICAL = 0.09
UNKNOWN_DSQ = 0.006

POINTS_BY_POSITION = np.array([25, 18, 15, 12, 10, 8, 6, 4, 2, 1], dtype=float)

DEFAULT_SIMS = 20_000
_CALIBRATION_SIMS = 4_000
_CALIBRATION_ROUNDS = 25
_TOLERANCE = 0.01
_EPS = 1e-6


def simulate_race(
    win: np.ndarray,
    podium: np.ndarray,
    points: np.ndarray,
    dnf_rate: np.ndarray | None = None,
    mechanical_rate: np.ndarray | None = None,
    incident_rate: np.ndarray | None = None,
    dsq_rate: np.ndarray | None = None,
    grid: np.ndarray | None = None,
    n_sims: int = DEFAULT_SIMS,
    seed: int = 0,
    keep_positions: bool = False,
) -> dict[str, np.ndarray]:
    win = np.asarray(win, dtype=float)
    podium = np.asarray(podium, dtype=float)
    points = np.asarray(points, dtype=float)
    field = len(podium)
    if field == 0:
        empty = np.zeros(0)
        return {
            "p_win": empty, "p_podium": empty, "p_points": empty, "p_dnf": empty,
            "p_crash": empty, "p_dsq": empty,
            "expected_finish": empty, "expected_points": empty,
            "finish_p10": empty, "finish_p90": empty,
        }

    crash, mech, dsq = _failure_probabilities(
        dnf_rate, mechanical_rate, incident_rate, dsq_rate, grid, field
    )
    out_of_race = 1.0 - (1.0 - crash) * (1.0 - mech) * (1.0 - dsq)

    targets = coherent_targets(win, podium, points, 1.0 - out_of_race)
    strengths = _calibrate(*targets, out_of_race, seed)
    positions, gone = _run(*strengths, out_of_race, n_sims, seed + 1)

    p_win, p_podium, p_points = _marginals(positions)
    extra = {"positions": positions, "gone": gone} if keep_positions else {}
    return {
        **extra,
        "p_win": p_win,
        "p_podium": p_podium,
        "p_points": p_points,
        "p_dnf": gone.mean(axis=0),
        "p_crash": crash,
        "p_dsq": dsq,
        "expected_finish": positions.mean(axis=0),
        "expected_points": _expected_points(positions),
        "finish_p10": np.percentile(positions, 10, axis=0),
        "finish_p90": np.percentile(positions, 90, axis=0),
    }


def coherent_targets(
    win: np.ndarray, podium: np.ndarray, points: np.ndarray, survive: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    field = len(podium)
    points = _fit_total(points, min(POINTS_PLACES, field), survive)
    podium = _fit_total(podium, min(PODIUM_CUTOFF, field), points)
    win = _fit_total(win, min(1, field), podium)
    return win, podium, points


def _fit_total(p: np.ndarray, total: float, cap: np.ndarray) -> np.ndarray:
    p = np.clip(np.nan_to_num(p.astype(float), nan=_EPS), _EPS, cap)
    for _ in range(100):
        current = p.sum()
        if abs(current - total) < 1e-6:
            break
        p = np.clip(p * (total / current), _EPS, cap)
    return p


def _calibrate(
    win: np.ndarray, podium: np.ndarray, points: np.ndarray,
    out_of_race: np.ndarray, seed: int,
) -> list[np.ndarray]:
    goals = _stage_shares(win, podium, points)
    logs = [np.log(g) for g in goals]
    for _ in range(_CALIBRATION_ROUNDS):
        positions, _ = _run(*logs, out_of_race, _CALIBRATION_SIMS, seed)
        got = _stage_shares(*_marginals(positions))
        gaps = [np.log(g) - np.log(h) for g, h in zip(goals, got)]
        if max(np.abs(g).max() for g in gaps) < _TOLERANCE:
            break
        logs = [np.clip(l + np.clip(g, -3.0, 3.0), -30.0, 30.0) for l, g in zip(logs, gaps)]
    return logs


def _stage_shares(win, podium, points):
    return (
        np.clip(win, _EPS, None),
        np.clip(podium - win, _EPS, None),
        np.clip(points - podium, _EPS, None),
    )


def _marginals(positions: np.ndarray):
    field = positions.shape[1]
    return (
        (positions == 1).mean(axis=0),
        (positions <= min(PODIUM_CUTOFF, field)).mean(axis=0),
        (positions <= min(POINTS_PLACES, field)).mean(axis=0),
    )


def _run(
    log_win: np.ndarray, log_podium: np.ndarray, log_rest: np.ndarray,
    out_of_race: np.ndarray, n_sims: int, seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    field = len(log_win)
    rows = np.arange(n_sims)

    gone = rng.random((n_sims, field)) < out_of_race
    alive = ~gone
    tier = np.where(gone, 3, 2)
    order_score = np.where(
        gone, rng.random((n_sims, field)), log_rest + rng.gumbel(size=(n_sims, field))
    )

    first = np.where(alive, log_win + rng.gumbel(size=(n_sims, field)), -np.inf)
    winner = first.argmax(axis=1)
    has_winner = alive.any(axis=1)
    tier[rows[has_winner], winner[has_winner]] = 0
    alive[rows[has_winner], winner[has_winner]] = False

    places = min(PODIUM_CUTOFF, field) - 1
    if places > 0:
        second = np.where(alive, log_podium + rng.gumbel(size=(n_sims, field)), -np.inf)
        top = np.argsort(-second, axis=1)[:, :places]
        valid = np.take_along_axis(second, top, axis=1) > -np.inf
        r = np.broadcast_to(rows[:, None], top.shape)[valid]
        c = top[valid]
        tier[r, c] = 1
        order_score[r, c] = second[r, c]

    key = tier * 1e4 - np.clip(order_score, -1e3, 1e3)
    order = np.argsort(key, axis=1)
    positions = np.empty((n_sims, field), dtype=np.int16)
    np.put_along_axis(
        positions, order,
        np.broadcast_to(np.arange(1, field + 1, dtype=np.int16), (n_sims, field)),
        axis=1,
    )
    return positions, gone


def _expected_points(positions: np.ndarray) -> np.ndarray:
    table = np.zeros(positions.max() + 1, dtype=float)
    scoring = POINTS_BY_POSITION[: len(table) - 1]
    table[1 : 1 + len(scoring)] = scoring
    return table[positions].mean(axis=0)


def _failure_probabilities(
    dnf_rate: np.ndarray | None,
    mechanical_rate: np.ndarray | None,
    incident_rate: np.ndarray | None,
    dsq_rate: np.ndarray | None,
    grid: np.ndarray | None,
    field: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    crash = _clean(incident_rate, field, UNKNOWN_INCIDENT)
    dsq = _clean(dsq_rate, field, UNKNOWN_DSQ)

    if mechanical_rate is not None:
        mech = _clean(mechanical_rate, field, UNKNOWN_MECHANICAL)
    elif dnf_rate is not None:
        total = _clean(dnf_rate, field, UNKNOWN_RETIREMENT)
        mech = total - crash
    else:
        mech = np.full(field, UNKNOWN_MECHANICAL)

    if grid is not None and field > 1:
        g = np.asarray(grid, dtype=float)
        spread = (g - 1.0) / (field - 1.0) - 0.5
        crash = crash * (1.0 + GRID_RISK_TILT * spread)

    return (
        np.clip(crash, MIN_INCIDENT, MAX_RETIREMENT),
        np.clip(mech, MIN_INCIDENT, MAX_RETIREMENT),
        np.clip(dsq, 0.0, 0.1),
    )


def _clean(values: np.ndarray | None, field: int, fallback: float) -> np.ndarray:
    if values is None:
        return np.full(field, fallback)
    arr = np.asarray(values, dtype=float)
    return np.where(np.isfinite(arr), arr, fallback)
