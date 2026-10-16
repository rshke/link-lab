"""Cross-field invariants for advertised capabilities; no protocol SDK dependency."""


def validate_bindings(document, features, expected_device_id):
    if document["deviceId"] != expected_device_id:
        raise ValueError("Action declaration does not match the registered device")
    identifiers = set()
    for action in document["actions"]:
        if action["id"] in identifiers:
            raise ValueError("Duplicate action ID")
        identifiers.add(action["id"])
        binding = action["binding"]
        command = features.get(binding["feature"], {}).get("commands", {}).get(binding["command"])
        if not command or not command["observable"]:
            raise ValueError("Action requires an implemented observable SiLA command")
        if command["parameters"].get(binding["commandIdParameter"]) != "String":
            raise ValueError("Invalid command ID binding")
        used = {binding["commandIdParameter"]}
        for parameter in action["parameters"].values():
            if parameter["minimum"] > parameter["maximum"]:
                raise ValueError("Parameter minimum exceeds maximum")
            name = parameter["silaParameter"]
            if name in used or command["parameters"].get(name) != "Integer":
                raise ValueError("Duplicate or incompatible SiLA parameter binding")
            used.add(name)
        if used != set(command["parameters"]):
            raise ValueError("All required SiLA parameters must be bound")
        if command["responses"].get(action["completion"]["response"]) != "String":
            raise ValueError("Completion evidence must bind a String response")
        resources = [resource["id"] for resource in action["resources"]]
        if len(resources) != len(set(resources)):
            raise ValueError("Duplicate resource ID in an action")
    for source in document["stateBindings"].values():
        prop = features.get(source["feature"], {}).get("properties", {}).get(source["property"])
        if prop != "String":
            raise ValueError("State fact must bind an implemented String property")
