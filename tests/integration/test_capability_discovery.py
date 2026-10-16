import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from interaction_demo import Stack, call


class CapabilityDiscoveryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack = Stack()
        cls.stack.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.stack.__exit__(None, None, None)

    def test_01_sila_declaration_reaches_platform(self):
        path = "/v1/devices/measurement-1/capabilities"
        snapshot = call(8010, path)
        self.assertEqual(snapshot, call(8012, path))
        definition = snapshot["definition"]
        self.assertEqual(definition["protocolVersion"], "1.0")
        self.assertEqual(definition["deviceId"], "measurement-1")
        action = definition["actions"][0]
        self.assertEqual(action["id"], "simulation.execute")
        self.assertEqual(action["parameters"]["durationMs"]["maximum"], 5000)
        self.assertEqual(action["resources"][0]["mode"], "exclusive")
        canonical = json.dumps(definition, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        self.assertEqual(snapshot["contentHash"], "sha256:" + hashlib.sha256(canonical).hexdigest())

    def test_02_live_fault_state_does_not_rewrite_capabilities(self):
        path = "/v1/devices/measurement-1/capabilities"
        before = call(8010, path)
        call(8013, "/v2/faults", {"code": "sensor_drift"})
        self.assertEqual(call(8010, "/v1/maintenance")["state"], "faulted")
        self.assertEqual(call(8010, path), before)
        self.assertEqual(before["definition"]["actions"][0]["preconditions"][0]["value"], "ready")


if __name__ == "__main__":
    unittest.main()
