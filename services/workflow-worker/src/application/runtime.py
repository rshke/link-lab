"""Owns the in-memory runs and exclusive reservation of the demo device."""
import threading
import uuid


class Runtime:
    def __init__(self, execute, read_device=None, maintain_device=None):
        self.execute = execute
        self.read_device = read_device
        self.maintain_device = maintain_device
        self.runs = {}
        self.lock = threading.Lock()
        self.reserved = False
        self.maintenance_pending = None
        self.maintenance_inflight = False

    def submit(self, plan):
        if not isinstance(plan, dict) or plan.get("admissionVersion") != 1:
            raise ValueError("An admitted v1 plan is required")
        steps = plan.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("An admitted plan requires steps")
        with self.lock:
            if self.reserved:
                raise ValueError("Device is reserved by another run")
            if self.read_device and self.read_device()["state"] != "ready":
                raise ValueError("Device requires maintenance and a passing self-test")
            self.reserved = True
            run_id = str(uuid.uuid4())
            self.runs[run_id] = {"runId": run_id, "state": "running", "results": []}
        threading.Thread(target=self._run, args=(run_id, steps), daemon=True).start()
        return {"runId": run_id, "state": "accepted"}

    def maintenance_state(self):
        state = self.read_device()
        with self.lock:
            return {**state, "workflowReserved": self.reserved}

    def maintain(self, operation):
        with self.lock:
            if self.reserved and self.maintenance_pending != operation:
                raise ValueError("Device is reserved; maintenance cannot release a running or unknown experiment")
            if self.maintenance_inflight:
                raise ValueError("A maintenance action is already in flight")
            self.reserved = True
            self.maintenance_pending = dict(operation)
            self.maintenance_inflight = True
        try:
            result = self.maintain_device(operation)
        except Exception:
            # An unconfirmed maintenance action must retain its reservation too.
            raise
        else:
            with self.lock:
                self.reserved = False
                self.maintenance_pending = None
            return result
        finally:
            with self.lock:
                self.maintenance_inflight = False

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
