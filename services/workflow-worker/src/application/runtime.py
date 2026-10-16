"""Owns the in-memory runs and exclusive reservation of the demo device."""
import threading
import uuid


class Runtime:
    def __init__(self, execute):
        self.execute = execute
        self.runs = {}
        self.lock = threading.Lock()
        self.reserved = False

    def submit(self, plan):
        if not isinstance(plan, dict) or plan.get("admissionVersion") != 1:
            raise ValueError("An admitted v1 plan is required")
        steps = plan.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("An admitted plan requires steps")
        with self.lock:
            if self.reserved:
                raise ValueError("Device is reserved by another run")
            self.reserved = True
            run_id = str(uuid.uuid4())
            self.runs[run_id] = {"runId": run_id, "state": "running", "results": []}
        threading.Thread(target=self._run, args=(run_id, steps), daemon=True).start()
        return {"runId": run_id, "state": "accepted"}

    def get(self, run_id):
        with self.lock:
            run = self.runs[run_id]
            return {**run, "results": list(run["results"])}

    def _run(self, run_id, steps):
        try:
            for index, step in enumerate(steps):
                result = self.execute({"commandId": f"{run_id}:{index}", **step})
                with self.lock:
                    self.runs[run_id]["results"].append(result)
                if result["state"] == "failed":
                    with self.lock:
                        self.runs[run_id].update(state="failed", error=result.get("error", "Device command failed"))
                        self.reserved = False
                    return
                if result["state"] != "succeeded":
                    raise ValueError("Device returned an unknown outcome")
            with self.lock:
                self.runs[run_id]["state"] = "succeeded"
                self.reserved = False
        except Exception as error:
            with self.lock:
                # A lost response does not prove that the device has stopped.
                # Keep its reservation until a developer reconciles/restarts the demo.
                self.runs[run_id].update(state="unknown", error=str(error))
