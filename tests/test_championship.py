import unittest

import numpy as np

from src.models import championship
from src.models.simulate import simulate_race


def _race(drivers, strength, sprint=False, seed=0):
    win = np.array(strength, dtype=float) / sum(strength)
    podium = np.clip(win * 3, 0, 0.95)
    points = np.clip(win * 10, 0, 0.98)
    sim = simulate_race(win, podium, points, n_sims=3000, seed=seed, keep_positions=True)
    return championship.SimulatedRace(drivers=drivers, positions=sim["positions"], gone=sim["gone"], sprint=sprint)


class ChampionshipTest(unittest.TestCase):
    def test_title_odds_sum_to_one_and_follow_the_gap(self):
        drivers = ["a", "b", "c", "d"]
        races = [_race(drivers, [4, 3, 2, 1], seed=i) for i in range(3)]
        out = championship.outlook({"a": 100.0, "b": 60.0}, races, dict(zip(drivers, ["x", "x", "y", "y"])))
        p_title = {r["id"]: r["p_title"] for r in out["drivers"]}
        self.assertAlmostEqual(sum(p_title.values()), 1.0, places=3)
        self.assertGreater(p_title["a"], p_title["b"])
        self.assertGreater(p_title["b"], p_title["d"])
        self.assertEqual(out["races_left"], 3)

    def test_points_never_drop_below_current_standings(self):
        drivers = ["a", "b"]
        out = championship.outlook({"a": 50.0, "b": 10.0}, [_race(drivers, [1, 1])], {"a": "x", "b": "y"},
                                   team_standings={"x": 50.0, "y": 10.0})
        rows = {r["id"]: r for r in out["drivers"]}
        self.assertGreaterEqual(rows["a"]["points_p10"], 50.0)
        teams = {r["id"]: r for r in out["teams"]}
        self.assertAlmostEqual(teams["x"]["expected_points"], rows["a"]["expected_points"], delta=0.2)

    def test_season_over_keeps_final_standings(self):
        out = championship.outlook({"a": 300.0, "b": 250.0}, [], {"a": "x", "b": "y"})
        self.assertEqual(out["drivers"][0]["id"], "a")
        self.assertEqual(out["drivers"][0]["p_title"], 1.0)

    def test_sprint_adds_points(self):
        drivers = ["a", "b"]
        plain = championship.outlook({}, [_race(drivers, [1, 1])], {"a": "x", "b": "y"})
        sprint = championship.outlook({}, [_race(drivers, [1, 1], sprint=True)], {"a": "x", "b": "y"})
        total = lambda o: sum(r["expected_points"] for r in o["drivers"])
        self.assertGreater(total(sprint), total(plain))


if __name__ == "__main__":
    unittest.main()
