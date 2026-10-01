import os
import time
import unittest

os.environ.setdefault("F1_AUTO_SYNC", "0")

from src import pipeline
from src.app import server


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.app.test_client()
        cls.boot = cls.client.get("/api/bootstrap").get_json()
        cls.lineup = cls.client.get("/api/lineup").get_json()

    def predict(self, body, **headers):
        return self.client.post("/api/predict", json=body, headers=headers)

    def valid_body(self, **extra):
        circuit = self.boot["next_race"]["circuit_id"] if self.boot["next_race"] else "monza"
        return {"circuit_id": circuit, "weather": "dry", "entries": self.lineup["entries"], **extra}

    def test_bootstrap(self):
        self.assertTrue(self.boot["tracks"])
        rounds = [t["round"] for t in self.boot["tracks"] if t["on_calendar"]]
        self.assertEqual(rounds, sorted(rounds))

    def test_lineup_has_a_source(self):
        self.assertIn(self.lineup["source"], server.GRID_SOURCES)
        self.assertGreaterEqual(len(self.lineup["entries"]), 10)

    def test_prediction_is_coherent(self):
        r = self.predict(self.valid_body())
        self.assertEqual(r.status_code, 200)
        entries = r.get_json()["entries"]
        self.assertAlmostEqual(sum(e["p_win"] for e in entries), 1.0, delta=1e-3)
        self.assertAlmostEqual(sum(e["p_podium"] for e in entries), 3.0, delta=1e-3)
        for e in entries:
            self.assertLessEqual(e["p_win"], e["p_podium"] + 1e-9)
            self.assertLessEqual(e["p_podium"], e["p_points"] + 1e-9)

    def test_rejects_bad_input(self):
        cases = [
            [1, 2],
            {"circuit_id": "monza", "entries": "x"},
            {"circuit_id": "nowhere", "entries": [{"driver_id": "russell"}]},
            self.valid_body(entries=[{"driver_id": "<img src=x>"}]),
            self.valid_body(entries=[{"driver_id": "russell", "grid": "abc"}]),
            self.valid_body(entries=[{"driver_id": "russell", "quali_gap_pct": "1e999"}]),
            self.valid_body(entries=[{"driver_id": "russell"}, {"driver_id": "russell"}]),
            self.valid_body(entries=[{"driver_id": "russell"}] * 40),
            self.valid_body(weather="<script>"),
            self.valid_body(season=99999),
        ]
        for body in cases:
            with self.subTest(body=str(body)[:60]):
                r = self.predict(body)
                self.assertEqual(r.status_code, 400)
                self.assertIn("error", r.get_json())

    def test_cross_site_post_is_blocked(self):
        calls = []
        original = pipeline.run
        pipeline.run = lambda **kw: calls.append(kw) or {}
        try:
            r = self.client.post("/api/sync", headers={"Origin": "https://evil.example"})
            self.assertEqual(r.status_code, 403)
            r = self.client.post("/api/sync", headers={"Sec-Fetch-Site": "cross-site"})
            self.assertEqual(r.status_code, 403)
        finally:
            pipeline.run = original
        self.assertEqual(calls, [])

    def test_untrusted_host_is_rejected(self):
        r = self.client.get("/api/bootstrap", headers={"Host": "attacker.example"})
        self.assertEqual(r.status_code, 400)

    def test_security_headers(self):
        r = self.client.get("/")
        self.assertIn("frame-ancestors 'none'", r.headers["Content-Security-Policy"])
        self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(r.headers["X-Frame-Options"], "DENY")

    def test_reloads_after_an_external_sync(self):
        reloads = []
        original = server._reload
        server._reload = lambda: reloads.append(1)
        path = pipeline.STATE_PATH
        existed = path.exists()
        before = path.stat().st_mtime if existed else None
        try:
            if not existed:
                path.write_text("{}", encoding="utf-8")
            os.utime(path, (time.time() + 5, time.time() + 5))
            self.client.get("/api/track/monza")
        finally:
            server._reload = original
            if existed:
                os.utime(path, (before, before))
            else:
                path.unlink()
            server._reload()
        self.assertEqual(reloads, [1])

    def test_errors_are_json(self):
        r = self.client.get("/api/sync")
        self.assertEqual(r.status_code, 405)
        self.assertIn("error", r.get_json())


if __name__ == "__main__":
    unittest.main()
