import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infrastructure.capability_reader import feature_model, parse_definition, read_snapshot
from domain.capabilities import validate_bindings


class CapabilityTest(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "simulators/measurement/config/action-semantics-v1.json").read_text())
        self.xml = {
            "org.link/simulation/ExperimentDevice/v1": (ROOT / "contracts/sila2/ExperimentDevice-v1_0.sila.xml").read_text(),
            "org.link/maintenance/DeviceMaintenance/v1": (ROOT / "contracts/sila2/DeviceMaintenance-v1_0.sila.xml").read_text(),
        }
        self.features = {key: feature_model(value) for key, value in self.xml.items()}

    def test_schema_rejects_unknown_version_vocabulary_and_fields(self):
        variants = []
        for key, value in (("protocolVersion", "2.0"), ("extra", "https://example.invalid/schema")):
            doc = copy.deepcopy(self.document)
            doc[key] = value
            variants.append(doc)
        doc = copy.deepcopy(self.document)
        doc["actions"][0]["preconditions"][0]["fact"] = "sample.mixed"
        variants.append(doc)
        doc = copy.deepcopy(self.document)
        doc["actions"][0]["parameters"]["durationMs"]["minimum"] = True
        variants.append(doc)
        for document in variants:
            with self.subTest(document=document), self.assertRaises(ValueError):
                parse_definition(json.dumps(document))
        with self.assertRaises(ValueError):
            parse_definition('{"protocolVersion":"2.0","protocolVersion":"1.0"}')
        with self.assertRaises(ValueError):
            parse_definition(" " * 65537)

    def test_rejects_cross_field_and_protocol_mismatches(self):
        variants = []
        duplicate = copy.deepcopy(self.document)
        duplicate["actions"].append(copy.deepcopy(duplicate["actions"][0]))
        variants.append(duplicate)
        for field, value in (("command", "MissingCommand"), ("commandIdParameter", "DurationMs")):
            doc = copy.deepcopy(self.document)
            doc["actions"][0]["binding"][field] = value
            variants.append(doc)
        doc = copy.deepcopy(self.document)
        doc["actions"][0]["parameters"]["durationMs"]["minimum"] = 6000
        variants.append(doc)
        doc = copy.deepcopy(self.document)
        doc["actions"][0]["resources"] *= 2
        variants.append(doc)
        doc = copy.deepcopy(self.document)
        doc["stateBindings"]["device.maintenance_state"]["property"] = "MissingState"
        variants.append(doc)
        for document in variants:
            with self.subTest(document=document), self.assertRaises(ValueError):
                validate_bindings(parse_definition(json.dumps(document)), self.features, "measurement-1")
        with self.assertRaises(ValueError):
            validate_bindings(self.document, self.features, "different-device")

    def test_snapshot_hash_ignores_json_key_order(self):
        def client(text):
            return SimpleNamespace(
                ActionSemantics=SimpleNamespace(Definitions=SimpleNamespace(get=lambda: text)),
                SiLAService=SimpleNamespace(
                    ImplementedFeatures=SimpleNamespace(get=lambda: list(self.xml)),
                    GetFeatureDefinition=lambda name: SimpleNamespace(FeatureDefinition=self.xml[name])))
        a = read_snapshot(client(json.dumps(self.document)), "measurement-1")
        b = read_snapshot(client(json.dumps(self.document, sort_keys=True)), "measurement-1")
        canonical = json.dumps(self.document, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        self.assertEqual(a["contentHash"], "sha256:" + hashlib.sha256(canonical).hexdigest())
        self.assertEqual(a["contentHash"], b["contentHash"])
        with self.assertRaises(ValueError):
            bad_client = client(json.dumps(self.document))
            bad_client.SiLAService.ImplementedFeatures.get = lambda: []
            read_snapshot(bad_client, "measurement-1")


if __name__ == "__main__":
    unittest.main()
