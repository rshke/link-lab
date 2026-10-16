from domain.admission import validate


def admit(spec, submit):
    validated = validate(spec)
    # The local demo admits every valid spec; no production approval policy.
    return submit({"admissionVersion": 1, **validated})
