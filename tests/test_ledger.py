import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src import ledger


def _result(order):
    return {
        "conditions": {"weather": "dry"},
        "model": {"trained_through": "2030-01-01"},
        "entries": [
            {"driver_id": d, "name": d.upper(), "grid": i, "expected_position": i,
             "p_win": 0.5 if i == 1 else 0.1, "p_podium": 0.8 if i <= 3 else 0.05, "p_points": 0.9}
            for i, d in enumerate(order, start=1)
        ],
    }


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original = ledger.LEDGER_DIR
        ledger.LEDGER_DIR = Path(self.tmp.name)
        self.race = {"race_id": "2030_01", "season": 2030, "round": 1, "race_name": "Test GP",
                     "start_utc": "2030-03-01T13:00:00+00:00"}

    def tearDown(self):
        ledger.LEDGER_DIR = self.original
        self.tmp.cleanup()

    def test_refuses_after_start(self):
        ok = ledger.record(self.race, _result(["a", "b", "c", "d"]), source="expected",
                           trigger="test", now=pd.Timestamp("2030-03-01T14:00:00+00:00"))
        self.assertFalse(ok)
        self.assertIsNone(ledger.recorded("2030_01"))

    def test_scores_against_the_result(self):
        ledger.record(self.race, _result(["a", "b", "c", "d"]), source="qualifying",
                      trigger="test", now=pd.Timestamp("2030-02-28T12:00:00+00:00"))
        results = pd.DataFrame({
            "race_id": "2030_01",
            "driver_id": ["a", "d", "b", "c"],
            "driver_name": ["A", "D", "B", "C"],
            "position": [1, 2, 3, 4],
            "grid": [1, 4, 2, 3],
            "classified": True,
        })
        card = ledger.scorecard(results)
        race = card["races"][0]
        self.assertEqual(race["status"], "scored")
        self.assertEqual(race["podium_hits"], 2)
        self.assertTrue(race["winner_hit"])
        self.assertEqual(card["summary"]["races"], 1)

    def test_pending_until_result(self):
        ledger.record(self.race, _result(["a", "b", "c"]), source="expected",
                      trigger="test", now=pd.Timestamp("2030-02-28T12:00:00+00:00"))
        card = ledger.scorecard(pd.DataFrame(columns=["race_id", "driver_id", "driver_name",
                                                      "position", "grid", "classified"]))
        self.assertEqual(card["races"][0]["status"], "pending")
        self.assertEqual(card["summary"]["races"], 0)

    def test_keeps_each_stage_and_scores_it(self):
        before = pd.Timestamp("2030-02-28T12:00:00+00:00")
        ledger.record(self.race, _result(["a", "b", "c", "d"]), source="expected", trigger="auto", now=before)
        ledger.record(self.race, _result(["a", "b", "c", "d"]), source="expected", trigger="predict", now=before)
        ledger.record(self.race, _result(["a", "d", "b", "c"]), source="qualifying", trigger="auto", now=before)
        self.assertEqual([h["grid_source"] for h in ledger.recorded("2030_01")["history"]], ["expected"])

        results = pd.DataFrame({
            "race_id": "2030_01",
            "driver_id": ["a", "d", "b", "c"],
            "driver_name": ["A", "D", "B", "C"],
            "position": [1, 2, 3, 4],
            "grid": [1, 4, 2, 3],
            "classified": True,
        })
        card = ledger.scorecard(results)
        stages = card["races"][0]["stages"]
        self.assertEqual([s["grid_source"] for s in stages], ["expected", "qualifying"])
        self.assertEqual([s["podium_hits"] for s in stages], [2, 3])
        self.assertEqual(card["summary"]["by_source"]["qualifying"]["podium_hit_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
