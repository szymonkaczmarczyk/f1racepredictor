import unittest

import numpy as np

from src.models.simulate import simulate_race


class SimulationTest(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(3)
        field = 20
        strength = np.sort(rng.random(field))[::-1]
        self.win = strength ** 6 / (strength ** 6).sum()
        self.podium = np.clip(strength ** 3 / (strength ** 3).sum() * 3, 0, 0.95)
        self.points = np.clip(strength / strength.sum() * 10, 0, 0.97)
        self.result = simulate_race(self.win, self.podium, self.points, n_sims=6000, seed=1)

    def test_totals(self):
        r = self.result
        self.assertAlmostEqual(r["p_win"].sum(), 1.0, delta=1e-9)
        self.assertAlmostEqual(r["p_podium"].sum(), 3.0, delta=1e-9)
        self.assertLessEqual(r["p_points"].sum(), 10.0 + 1e-9)

    def test_nested(self):
        r = self.result
        self.assertTrue(np.all(r["p_win"] <= r["p_podium"] + 1e-9))
        self.assertTrue(np.all(r["p_podium"] <= r["p_points"] + 1e-9))

    def test_follows_every_head(self):
        r = self.result
        self.assertLess(np.abs(r["p_win"] - self.win / self.win.sum()).max(), 0.05)
        top = np.argsort(-self.win)[:3]
        self.assertTrue(set(np.argsort(-r["p_win"])[:3]) & set(top))

    def test_changing_win_head_changes_win_probability(self):
        flipped = self.win.copy()
        flipped[[0, 1]] = flipped[[1, 0]]
        other = simulate_race(flipped, self.podium, self.points, n_sims=6000, seed=1)
        self.assertGreater(other["p_win"][1], self.result["p_win"][1])

    def test_empty_field(self):
        r = simulate_race(np.zeros(0), np.zeros(0), np.zeros(0))
        self.assertEqual(len(r["p_win"]), 0)


if __name__ == "__main__":
    unittest.main()
