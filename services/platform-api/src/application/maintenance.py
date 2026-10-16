"""Admission and local-demo audit for simulated physical maintenance."""
import threading
from datetime import datetime, timezone


class MaintenanceAdmission:
    def __init__(self, submit):
        self.submit = submit
        self.lock = threading.Lock()
        self.audit = {}

    def records(self):
        with self.lock:
            return {"records": list(self.audit.values())}

    def perform(self, body):
        required = {"requestId", "incidentId", "action", "expectedRevision"}
        if not isinstance(body, dict) or set(body) != required:
            raise ValueError("Expected requestId, incidentId, action and expectedRevision")
        for field in ("requestId", "incidentId", "action"):
            if not isinstance(body[field], str) or not 1 <= len(body[field]) <= 100:
                raise ValueError("Invalid maintenance identifier")
        if type(body["expectedRevision"]) is not int or body["expectedRevision"] < 0:
            raise ValueError("Invalid expectedRevision")
        result = self.submit(body)
        with self.lock:
            self.audit.setdefault(body["requestId"], {
                **body, "accepted": result["accepted"], "message": result["message"],
                "at": datetime.now(timezone.utc).isoformat(), "actor": "local-demo-operator"})
        return result
