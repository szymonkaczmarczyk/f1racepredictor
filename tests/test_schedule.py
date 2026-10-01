import unittest

import pandas as pd

from src.ingest import openf1, schedule


def _race(round_, start, completed=False, cancelled=False, circuit="c", quali=None):
    return {
        "race_id": f"2030_{round_:02d}", "season": 2030, "round": round_,
        "race_name": f"Race {round_}", "circuit_id": circuit,
        "lat": 0.0, "lon": 0.0, "date": start[:10], "start_utc": start,
        "quali_utc": quali, "completed": completed, "cancelled": cancelled,
    }


class ScheduleTest(unittest.TestCase):
    def setUp(self):
        self.calendar = [
            _race(1, "2030-03-01T13:00:00+00:00", completed=True, circuit="a"),
            _race(2, "2030-03-08T13:00:00+00:00", circuit="b"),
            _race(3, "2030-03-15T13:00:00+00:00", cancelled=True, circuit="x"),
            _race(4, "2030-03-22T13:00:00+00:00", circuit="c", quali="2030-03-21T15:00:00+00:00"),
        ]

    def status(self, now):
        return {r["round"]: r["status"] for r in schedule.with_status(self.calendar, pd.Timestamp(now))}

    def test_statuses_move_with_the_clock(self):
        s = self.status("2030-03-08T14:00:00+00:00")
        self.assertEqual(s, {1: "completed", 2: "in_progress", 3: "cancelled", 4: "upcoming"})
        s = self.status("2030-03-10T00:00:00+00:00")
        self.assertEqual(s[2], "awaiting_results")

    def test_next_race_skips_unreported_and_cancelled(self):
        nxt = schedule.next_race(self.calendar, pd.Timestamp("2030-03-10T00:00:00+00:00"))
        self.assertEqual(nxt["round"], 4)

    def test_needs_sync(self):
        self.assertTrue(schedule.needs_sync(self.calendar, pd.Timestamp("2030-03-10T00:00:00+00:00")))
        done = [dict(r, completed=True) if r["round"] == 2 else r for r in self.calendar]
        self.assertFalse(schedule.needs_sync(done, pd.Timestamp("2030-03-10T00:00:00+00:00")))
        self.assertTrue(schedule.needs_sync(done, pd.Timestamp("2030-03-21T18:00:00+00:00")))

    def test_race_at_prefers_pending(self):
        cal = self.calendar + [_race(5, "2030-04-01T13:00:00+00:00", circuit="a")]
        self.assertEqual(schedule.race_at(cal, "a", pd.Timestamp("2030-03-10T00:00:00+00:00"))["round"], 5)

    def test_meeting_matched_by_date_not_name(self):
        meetings = [
            {"meeting_name": "Bahrain Grand Prix", "country_name": "Bahrain", "is_cancelled": True,
             "date_start": "2030-04-10T11:30:00+00:00", "date_end": "2030-04-12T17:00:00+00:00"},
            {"meeting_name": "Bahrain Grand Prix", "country_name": "Malaysia", "is_cancelled": False,
             "date_start": "2030-10-02T04:30:00+00:00", "date_end": "2030-10-04T09:00:00+00:00"},
        ]
        found = openf1.meeting_for(pd.Timestamp("2030-10-04T07:00:00+00:00"), meetings)
        self.assertEqual(found["country_name"], "Malaysia")
        self.assertIsNone(openf1.meeting_for(pd.Timestamp("2030-06-01T13:00:00+00:00"), meetings))


if __name__ == "__main__":
    unittest.main()
