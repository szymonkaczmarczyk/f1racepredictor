from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.models.simulate import POINTS_BY_POSITION

SPRINT_POINTS = np.array([8, 7, 6, 5, 4, 3, 2, 1], dtype=float)


@dataclass
class SimulatedRace:
    drivers: list[str]
    positions: np.ndarray
    gone: np.ndarray
    sprint: bool = False


def outlook(
    standings: dict[str, float],
    races: list[SimulatedRace],
    teams: dict[str, str],
    team_standings: dict[str, float] | None = None,
    seed: int = 0,
) -> dict:
    rng = np.random.default_rng(seed)
    drivers = sorted({d for r in races for d in r.drivers} | set(standings))
    column = {d: i for i, d in enumerate(drivers)}
    n_sims = min((len(r.positions) for r in races), default=1)

    totals = np.tile(np.array([standings.get(d, 0.0) for d in drivers]), (n_sims, 1))
    for race in races:
        cols = [column[d] for d in race.drivers]
        totals[:, cols] += _points(race.positions[:n_sims], race.gone[:n_sims], POINTS_BY_POSITION)
        if race.sprint:
            order = rng.permutation(len(race.positions))[:n_sims]
            totals[:, cols] += _points(race.positions[order], race.gone[order], SPRINT_POINTS)

    team_ids = sorted({teams[d] for d in drivers if d in teams} | set(team_standings or {}))
    team_totals = np.zeros((n_sims, len(team_ids)))
    for j, team in enumerate(team_ids):
        members = [column[d] for d in drivers if teams.get(d) == team]
        scored = totals[:, members].sum(axis=1) - sum(standings.get(drivers[m], 0.0) for m in members)
        team_totals[:, j] = (team_standings or {}).get(team, 0.0) + scored

    return {
        "sims": n_sims,
        "races_left": len(races),
        "sprints_left": sum(r.sprint for r in races),
        "drivers": _table(drivers, totals, standings, rng),
        "teams": _table(team_ids, team_totals, team_standings or {}, rng),
    }


def _points(positions: np.ndarray, gone: np.ndarray, table: np.ndarray) -> np.ndarray:
    lookup = np.zeros(int(positions.max()) + 1)
    lookup[1 : 1 + len(table)] = table[: len(lookup) - 1]
    return np.where(gone, 0.0, lookup[positions])


def _table(ids: list[str], totals: np.ndarray, now: dict[str, float], rng) -> list[dict]:
    if not ids:
        return []
    jitter = rng.random(totals.shape) * 1e-6
    champion = (totals + jitter).argmax(axis=1)
    p_title = np.bincount(champion, minlength=len(ids)) / len(totals)
    rows = [
        {
            "id": ident,
            "points_now": float(now.get(ident, 0.0)),
            "expected_points": round(float(totals[:, i].mean()), 1),
            "points_p10": float(np.percentile(totals[:, i], 10)),
            "points_p90": float(np.percentile(totals[:, i], 90)),
            "p_title": round(float(p_title[i]), 4),
        }
        for i, ident in enumerate(ids)
    ]
    return sorted(rows, key=lambda r: (-r["expected_points"], -r["points_now"]))
