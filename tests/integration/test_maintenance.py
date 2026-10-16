"""Maintenance acceptance over platform -> workflow -> gateway -> real SiLA 2."""
import sys
import time
import unittest
import uuid
from pathlib import Path
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from interaction_demo import Stack, call, HTTP


class MaintenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack = Stack()
        cls.stack.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.stack.__exit__(None, None, None)

    def state(self):
        return call(8010, "/v1/maintenance")

    def perform(self, action, state=None, request_id=None):
        state = state or self.state()
        return call(8010, "/v1/maintenance/actions", {
            "requestId": request_id or str(uuid.uuid4()), "incidentId": state["incidentId"],
            "expectedRevision": state["revision"], "action": action})

    def test_01_distinct_repairs_and_gates(self):
        recipes = {
            "channel_blockage": ("flush_channel", "replace_filter"),
            "sensor_drift": ("clean_sensor", "calibrate_sensor"),
            "loose_cable": ("reseat_cable", "secure_connector"),
        }
        for code, steps in recipes.items():
            with self.subTest(code=code):
                call(8013, "/v2/faults", {"code": code})
                self.assertEqual(self.state()["state"], "faulted")
                with self.assertRaises(HTTPError):
                    call(8010, "/v1/experiments", {"steps": [{"deviceId": "measurement-1", "durationMs": 100}]})
                # A direct internal command cannot bypass the simulator's fault state.
                rejected = call(8012, "/v1/commands", {
                    "commandId": str(uuid.uuid4()), "deviceId": "measurement-1", "durationMs": 100})
                self.assertEqual(rejected["state"], "failed")
                self.assertFalse(self.perform(steps[0])["accepted"])
                self.assertFalse(self.perform("self_test")["accepted"])
                self.assertTrue(self.perform("inspect")["accepted"])
                self.assertFalse(self.perform(steps[1])["accepted"], "Wrong order cannot repair the device")
                wrong = "reseat_cable" if code != "loose_cable" else "flush_channel"
                self.assertFalse(self.perform(wrong)["accepted"])
                self.assertEqual(self.state()["completed"], [])
                state = self.state()
                request_id = str(uuid.uuid4())
                first = self.perform(steps[0], state, request_id)
                repeated = self.perform(steps[0], state, request_id)
                self.assertEqual(first, repeated, "An acknowledged physical operation must not repeat")
                self.assertFalse(self.perform(steps[1], state)["accepted"], "Stale revision must be rejected")
                self.assertTrue(self.perform(steps[1])["accepted"])
                self.assertEqual(self.state()["state"], "awaiting_self_test")
                with self.assertRaises(HTTPError):
                    call(8010, "/v1/experiments", {"steps": [{"deviceId": "measurement-1", "durationMs": 100}]})
                self.assertTrue(self.perform("self_test")["accepted"])
                self.assertEqual(self.state()["state"], "ready")
                self.assertFalse(self.state()["workflowReserved"])
        accepted = call(8010, "/v1/experiments", {"steps": [{"deviceId": "measurement-1", "durationMs": 100}]})
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            run = call(8010, "/v1/runs/" + accepted["runId"])
            if run["state"] != "running":
                break
            time.sleep(0.05)
        self.assertEqual(run["state"], "succeeded")

    def test_02_no_repair_during_experiment(self):
        accepted = call(8010, "/v1/experiments", {"steps": [{"deviceId": "measurement-1", "durationMs": 400}]})
        with self.assertRaises(HTTPError):
            self.perform("inspect")
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if call(8010, "/v1/runs/" + accepted["runId"])["state"] != "running":
                break
            time.sleep(0.05)
        self.assertFalse(self.state()["workflowReserved"])

    def test_03_ui_and_invalid_requests(self):
        with HTTP.open("http://127.0.0.1:8010/maintenance") as response:
            self.assertTrue(response.headers["Content-Type"].startswith("text/html"))
            page = response.read().decode("utf-8")
            self.assertIn("设备维护工作台", page)
            self.assertNotIn("fetch('http://", page)
        with self.assertRaises(HTTPError):
            call(8010, "/v1/maintenance/actions", {"action": "inspect"})


if __name__ == "__main__":
    unittest.main()
