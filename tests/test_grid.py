import os
import unittest

os.environ.setdefault("F1_AUTO_SYNC", "0")

from src.app import server


def _lineup(*drivers):
    return [
        {"driver_id": d, "constructor_id": "team", "grid": i, "quali_position": i, "quali_gap_pct": None}
        for i, d in enumerate(drivers, start=1)
    ]


class StartingGridTest(unittest.TestCase):
    def test_penalty_moves_driver_back(self):
        out = server._apply_starting_grid(_lineup("a", "b", "c", "d"), {"a": 3, "b": 1, "c": 2, "d": 4})
        self.assertEqual([e["driver_id"] for e in out], ["b", "c", "a", "d"])
        self.assertEqual([e["grid"] for e in out], [1, 2, 3, 4])
        self.assertEqual(out[2]["quali_position"], 1)

    def test_missing_driver_goes_to_the_back(self):
        out = server._apply_starting_grid(_lineup("a", "b", "c"), {"b": 1, "c": 2})
        self.assertEqual([e["driver_id"] for e in out], ["b", "c", "a"])

    def test_lineup_prefers_starting_grid_over_qualifying(self):
        race = {"race_id": "2030_01", "circuit_id": "x", "status": "upcoming",
                "lineup_source": "qualifying", "lineup": _lineup("a", "b", "c")}
        originals = (server.calendar_for, server._starting_grid, server.schedule.next_race)
        server.calendar_for = lambda season: [race]
        server.schedule.next_race = lambda cal: race
        try:
            server._starting_grid = lambda r, s: {"a": 3, "b": 1, "c": 2}
            entries, source, _ = server._lineup_for(2030, None)
            self.assertEqual(source, "starting_grid")
            self.assertEqual([e["driver_id"] for e in entries], ["b", "c", "a"])

            server._starting_grid = lambda r, s: {}
            entries, source, _ = server._lineup_for(2030, None)
            self.assertEqual(source, "qualifying")
            self.assertEqual([e["driver_id"] for e in entries], ["a", "b", "c"])
        finally:
            server.calendar_for, server._starting_grid, server.schedule.next_race = originals


class LedgerUpgradeTest(unittest.TestCase):
    def existing(self, source, order):
        return {"grid_source": source,
                "entries": [{"driver_id": d, "grid": i} for i, d in enumerate(order, start=1)]}

    def test_better_source_rerecords(self):
        self.assertTrue(server._improves(self.existing("qualifying", "abc"), "starting_grid", _lineup(*"abc")))
        self.assertFalse(server._improves(self.existing("starting_grid", "abc"), "qualifying", _lineup(*"abc")))

    def test_changed_starting_grid_rerecords(self):
        self.assertTrue(server._improves(self.existing("starting_grid", "abc"), "starting_grid", _lineup(*"bca")))
        self.assertFalse(server._improves(self.existing("starting_grid", "abc"), "starting_grid", _lineup(*"abc")))

    def test_same_qualifying_does_not_rerecord(self):
        self.assertFalse(server._improves(self.existing("qualifying", "abc"), "qualifying", _lineup(*"bca")))


if __name__ == "__main__":
    unittest.main()
