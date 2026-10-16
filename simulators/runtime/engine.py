"""Small simulated action engine; no dependency on the SiLA SDK."""
import threading
import time


class Engine:
    def __init__(self):
        self.lock = threading.Lock()
        self.mode = "normal"
        self.busy = False
        self.completed = {}
        self.sequence = 0

    def configure(self, body):
        if not isinstance(body, dict) or set(body) != {"mode"}:
            raise ValueError("Expected mode only")
        if body["mode"] not in ("normal", "delay", "fail"):
            raise ValueError("mode must be normal, delay or fail")
        with self.lock:
            self.mode = body["mode"]
        return {"nextCommandMode": body["mode"]}

    def execute(self, command_id, duration_ms, emit, progress):
        if not command_id or type(duration_ms) is not int or not 100 <= duration_ms <= 5000:
            raise ValueError("Invalid device command")
        with self.lock:
            if command_id in self.completed:
                previous_duration, result = self.completed[command_id]
                if previous_duration != duration_ms:
                    raise ValueError("Command ID reused with different parameters")
                return dict(result)
            if self.busy:
                raise ValueError("Device is busy")
            self.busy = True
            mode, self.mode = self.mode, "normal"
        try:
            for tick in range(11):
                state = "running"
                if tick == 5 and mode == "delay":
                    self._emit(command_id, "delayed", tick * 10, emit)
                    time.sleep(0.5)
                if tick == 5 and mode == "fail":
                    state = "failed"
                elif tick == 10:
                    state = "succeeded"
                self._emit(command_id, state, tick * 10, emit)
                progress(tick * 10)
                if state in ("failed", "succeeded"):
                    result = {"commandId": command_id, "state": state, "chaos": mode}
                    if state == "failed":
                        result["error"] = "Injected device fault at 50%"
                    with self.lock:
                        self.completed[command_id] = (duration_ms, result)
                    return dict(result)
                time.sleep(duration_ms / 10000)
        finally:
            with self.lock:
                self.busy = False

    def _emit(self, command_id, state, progress, emit):
        self.sequence += 1
        emit({"deviceId": "measurement-1", "commandId": command_id,
              "state": state, "progress": progress, "sequence": self.sequence})
