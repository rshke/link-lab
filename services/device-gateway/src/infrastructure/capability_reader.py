"""Read and validate the internal capability document over public SiLA calls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from jsonschema import Draft202012Validator
from domain.capabilities import validate_bindings

SCHEMA_PATH = Path(__file__).resolve().parents[4] / "contracts/schemas/capabilities/action-semantics-v1.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
NS = {"s": "http://www.sila-standard.org"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON member: " + key)
        result[key] = value
    return result


def parse_definition(text):
    if len(text.encode("utf-8")) > 65536:
        raise ValueError("Action declarations must be at most 64 KiB")
    try:
        document = json.loads(text, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise ValueError("Invalid action declaration JSON") from error
    errors = sorted(VALIDATOR.iter_errors(document), key=lambda error: str(list(error.path)))
    if errors:
        raise ValueError("Invalid action declaration: " + errors[0].message)
    return document


def feature_model(xml):
    root = ET.fromstring(xml)
    def identifier(element):
        return element.findtext("s:Identifier", namespaces=NS)
    def parameters(element, kind):
        return {identifier(item): item.findtext("s:DataType/s:Basic", namespaces=NS)
                for item in element.findall("s:" + kind, NS)}
    return {
        "commands": {identifier(cmd): {
            "observable": cmd.findtext("s:Observable", namespaces=NS) == "Yes",
            "parameters": parameters(cmd, "Parameter"), "responses": parameters(cmd, "Response")}
            for cmd in root.findall("s:Command", NS)},
        "properties": {identifier(prop): prop.findtext("s:DataType/s:Basic", namespaces=NS)
                       for prop in root.findall("s:Property", NS)},
    }


def read_snapshot(client, expected_device_id):
    # Never resolve schema URLs or import code named by the device.
    document = parse_definition(client.ActionSemantics.Definitions.get())
    required = {action["binding"]["feature"] for action in document["actions"]}
    required.update(source["feature"] for source in document["stateBindings"].values())
    implemented = set(client.SiLAService.ImplementedFeatures.get())
    if not required <= implemented:
        raise ValueError("Action declaration references an unimplemented SiLA Feature")
    features = {name: feature_model(client.SiLAService.GetFeatureDefinition(name).FeatureDefinition)
                for name in sorted(required)}
    validate_bindings(document, features, expected_device_id)
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return {"deviceId": document["deviceId"], "definitionVersion": document["definitionVersion"],
            "contentHash": "sha256:" + hashlib.sha256(canonical).hexdigest(),
            "retrievedAt": datetime.now(timezone.utc).isoformat(), "definition": document}
