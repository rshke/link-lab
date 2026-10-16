"""Real-process HTTP + SiLA 2 checks; no service implementation imports."""
import sys
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from interaction_demo import Stack, call, scenario


class InteractionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack = Stack()
        cls.stack.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.stack.__exit__(None, None, None)

    def test_01_normal_and_idempotency(self):
        run = scenario("normal")
        self.assertEqual(run["state"], "succeeded")
        result = run["results"][0]
        events_before = call(8012, "/v1/observations")["observations"]
        repeated = call(8012, "/v1/commands", {
            "commandId": result["commandId"], "deviceId": "measurement-1", "durationMs": 400})
        self.assertEqual(repeated, result)
        events_after = call(8012, "/v1/observations")["observations"]
        before = [e for e in events_before if e["commandId"] == result["commandId"]]
        after = [e for e in events_after if e["commandId"] == result["commandId"]]
        self.assertEqual(before, after, "Retry must not repeat physical work")
        with self.assertRaises(HTTPError):
            call(8012, "/v1/commands", {
                "commandId": result["commandId"], "deviceId": "measurement-1", "durationMs": 500})

    def test_02_fault_propagates(self):
        run = scenario("fail")
        self.assertEqual(run["state"], "failed")
        self.assertIn("Injected device fault", run["error"])
        # The next command returns to normal and the workflow releases the device.
        self.assertEqual(scenario("normal")["state"], "succeeded")

    def test_03_delay_is_observable(self):
        start = time.monotonic()
        run = scenario("delay")
        self.assertEqual(run["state"], "succeeded")
        self.assertGreaterEqual(time.monotonic() - start, 0.9)
        deadline = time.monotonic() + 2
        while True:
            observations = call(8012, "/v1/observations")["observations"]
            matching = [e for e in observations if e["commandId"] == run["results"][0]["commandId"]]
            if any(e["state"] == "succeeded" for e in matching) or time.monotonic() > deadline:
                break
            time.sleep(0.02)
        self.assertIn("delayed", [e["state"] for e in matching])
        self.assertEqual(matching[-1]["progress"], 100)
        self.assertEqual([e["sequence"] for e in matching], sorted({e["sequence"] for e in matching}))

    def test_04_invalid_spec_stops_at_admission(self):
        before = call(8012, "/v1/observations")
        for duration in (-1, True, 5001):
            with self.assertRaises(HTTPError) as error:
                call(8010, "/v1/experiments", {"steps": [{"deviceId": "measurement-1", "durationMs": duration}]})
            self.assertEqual(error.exception.code, 400)
        self.assertEqual(before, call(8012, "/v1/observations"))

    def test_05_workflow_reserves_device_and_sequences_steps(self):
        call(8013, "/v1/chaos", {"mode": "normal"})
        spec = {"steps": [{"deviceId": "measurement-1", "durationMs": 400}] * 2}
        accepted = call(8010, "/v1/experiments", spec)
        with self.assertRaises(HTTPError):
            call(8010, "/v1/experiments", spec)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            run = call(8010, "/v1/runs/" + accepted["runId"])
            if run["state"] != "running":
                break
            time.sleep(0.05)
        self.assertEqual(run["state"], "succeeded")
        self.assertEqual(len(run["results"]), 2)
        self.assertNotEqual(run["results"][0]["commandId"], run["results"][1]["commandId"])

    def test_06_disconnect_keeps_reservation(self):
        spec = {"steps": [{"deviceId": "measurement-1", "durationMs": 5000}]}
        accepted = call(8010, "/v1/experiments", spec)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            observations = call(8012, "/v1/observations")["observations"]
            if any(e["commandId"] == accepted["runId"] + ":0" for e in observations):
                break
            time.sleep(0.05)
        else:
            self.fail("Device did not receive the command")
        self.stack.processes[0].terminate()
        self.stack.processes[0].wait(timeout=5)
        deadline = time.monotonic() + 16
        while time.monotonic() < deadline:
            run = call(8010, "/v1/runs/" + accepted["runId"])
            if run["state"] != "running":
                break
            time.sleep(0.1)
        self.assertEqual(run["state"], "unknown")
        with self.assertRaises(HTTPError):
            call(8010, "/v1/experiments", spec)


if __name__ == "__main__":
    unittest.main()
