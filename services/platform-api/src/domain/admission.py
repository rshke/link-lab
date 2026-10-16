"""Deterministic validation for the single-device interaction demo."""


def validate(spec):
    if not isinstance(spec, dict) or set(spec) != {"steps"}:
        raise ValueError("Expected an experiment with steps only")
    steps = spec["steps"]
    if not isinstance(steps, list) or not 1 <= len(steps) <= 10:
        raise ValueError("Expected 1 to 10 steps")
    for step in steps:
        if not isinstance(step, dict) or set(step) != {"deviceId", "durationMs"}:
            raise ValueError("Each step needs deviceId and durationMs")
        if step["deviceId"] != "measurement-1":
            raise ValueError("Unknown device")
        duration = step["durationMs"]
        if type(duration) is not int or not 100 <= duration <= 5000:
            raise ValueError("durationMs must be an integer in [100, 5000]")
    return {"steps": [dict(step) for step in steps]}
