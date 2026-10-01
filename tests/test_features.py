import json
import unittest

import numpy as np
import pandas as pd

from src.config import PROCESSED_DIR
from src.features.build import FEATURES, build_dataset


class FeatureLeakTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        races = pd.read_csv(PROCESSED_DIR / "races.csv", parse_dates=["date"])
        results = pd.read_csv(PROCESSED_DIR / "results.csv", parse_dates=["date"])
        cls.quali = pd.read_csv(PROCESSED_DIR / "qualifying.csv")
        cls.catalogue = json.loads((PROCESSED_DIR / "circuit_catalogue.json").read_text(encoding="utf-8"))
        cls.races = races[races["season"] >= 2022]
        cls.results = results[results["season"] >= 2022]
        cls.target = sorted(cls.results["race_id"].unique())[-1]

    def build(self, results):
        frame, store = build_dataset(results, self.quali, self.races, self.catalogue)
        return frame[frame["race_id"] == self.target].set_index("driver_id")[FEATURES], store

    def test_race_result_does_not_reach_its_own_row(self):
        original, _ = self.build(self.results)
        shuffled = self.results.copy()
        mask = shuffled["race_id"] == self.target
        positions = shuffled.loc[mask, "position"].to_numpy()
        shuffled.loc[mask, "position"] = positions[::-1]
        shuffled.loc[mask, "points"] = shuffled.loc[mask, "points"].to_numpy()[::-1]
        shuffled.loc[mask, "laps"] = 1
        changed, _ = self.build(shuffled)
        pd.testing.assert_frame_equal(original.sort_index(), changed.sort_index())

    def test_car_rank_only_counts_current_teams(self):
        frame, store = self.build(self.results)
        field = self.results.loc[self.results["race_id"] == self.target, "constructor_id"].nunique()
        self.assertLessEqual(np.nanmax(frame["team_car_rank_est"]), field + 1)

    def test_era_counter_resets_at_new_rules(self):
        results = self.results[self.results["season"] >= 2025]
        frame, _ = build_dataset(results, self.quali, self.races, self.catalogue)
        last_2025 = frame[frame["season"] == 2025]["era_races"].max()
        first_2026 = frame[(frame["season"] == 2026) & (frame["round"] == 1)]["era_races"]
        self.assertGreater(last_2025, 10)
        self.assertTrue((first_2026 == 0).all())


if __name__ == "__main__":
    unittest.main()
