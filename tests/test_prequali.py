import os
import unittest

import pandas as pd

os.environ.setdefault("F1_AUTO_SYNC", "0")

from src.features import prequali


class ExpectedOrderTest(unittest.TestCase):
    def test_orders_by_median_of_last_three_gaps(self):
        history = pd.DataFrame({
            "season": 2030, "round": [1, 2, 3, 4, 1, 2, 3, 4],
            "driver_id": ["a"] * 4 + ["b"] * 4,
            "quali_gap_pct": [5.0, 0.4, 0.5, 0.6, 0.0, 0.1, 0.9, 1.0],
        })
        grid = prequali.expected_order(["a", "b"], ["x", "y"], history)
        self.assertEqual(grid["grid"].to_dict(), {"a": 1, "b": 2})
        self.assertAlmostEqual(grid.loc["a", "gap"], 0.0)
        self.assertAlmostEqual(grid.loc["b", "gap"], 0.4)

    def test_rookie_goes_behind_team_mate(self):
        history = pd.DataFrame({
            "season": 2030, "round": [1, 1], "driver_id": ["a", "b"], "quali_gap_pct": [0.2, 0.8],
        })
        grid = prequali.expected_order(["a", "b", "rookie"], ["x", "y", "x"], history)
        self.assertGreater(grid.loc["rookie", "grid"], grid.loc["a", "grid"])
        self.assertAlmostEqual(grid.loc["rookie", "gap"], 0.5)


class StageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.app import server
        cls.server = server
        cls.client = server.app.test_client()

    def test_expected_grid_uses_pre_qualifying_model(self):
        if not self.server.predictor().prequali:
            self.skipTest("model bundle has no pre-qualifying heads yet")
        boot = self.client.get("/api/bootstrap").get_json()
        if not boot["next_race"]:
            self.skipTest("no upcoming race")
        lineup = self.client.get("/api/lineup").get_json()
        body = {"circuit_id": boot["next_race"]["circuit_id"], "weather": "dry",
                "entries": lineup["entries"], "grid_source": "what_if", "base_source": "expected"}
        pre = self.client.post("/api/predict", json=body).get_json()
        post = self.client.post("/api/predict", json={**body, "base_source": "qualifying"}).get_json()
        self.assertEqual(pre["model"]["stage"], "pre_qualifying")
        self.assertEqual(post["model"]["stage"], "grid")
        self.assertIn("p_podium_grid", pre["entries"][0])


if __name__ == "__main__":
    unittest.main()
