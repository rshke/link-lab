import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from application.runtime import Runtime


class MaintenanceReservationTest(unittest.TestCase):
    def test_lost_response_can_only_retry_same_operation(self):
        calls = []

        def maintain(operation):
            calls.append(dict(operation))
            if len(calls) == 1:
                raise TimeoutError("Reply lost after physical repair")
            return {"accepted": True}

        runtime = Runtime(None, lambda: {"state": "ready"}, maintain)
        operation = {"requestId": "stable", "incidentId": "incident", "action": "flush_channel", "expectedRevision": 1}
        with self.assertRaises(TimeoutError):
            runtime.maintain(operation)
        self.assertTrue(runtime.reserved)
        with self.assertRaises(ValueError):
            runtime.maintain({**operation, "requestId": "new"})
        with self.assertRaises(ValueError):
            runtime.submit({"admissionVersion": 1, "steps": [{}]})
        self.assertTrue(runtime.maintain(operation)["accepted"])
        self.assertFalse(runtime.reserved)
        self.assertEqual(calls, [operation, operation])

    def test_experiment_unknown_reservation_cannot_be_repaired_away(self):
        runtime = Runtime(None, lambda: {"state": "ready"}, lambda _: self.fail("Must not call device"))
        runtime.reserved = True
        with self.assertRaises(ValueError):
            runtime.maintain({"requestId": "repair"})
        self.assertTrue(runtime.reserved)


if __name__ == "__main__":
    unittest.main()
