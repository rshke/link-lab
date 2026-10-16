import json
import threading
import time
from collections import deque

from sila2.client import SilaClient


class SilaDevice:
    def __init__(self, port):
        self.client = SilaClient("127.0.0.1", port, insecure=True)
        self.lock = threading.Lock()
        self.events = deque(maxlen=1000)
        self.subscription = self.client.ExperimentDevice.Status.subscribe()
        self.subscription.add_callback(self._observe)

    def _observe(self, value):
        status = json.loads(value)
        with self.lock:
            self.events.append(status)
        print(json.dumps({"source": "sila2.Status", **status}), flush=True)

    def observations(self):
        with self.lock:
            return {"observations": list(self.events)}

    def maintenance_state(self):
        return json.loads(self.client.DeviceMaintenance.State.get())

    def maintain(self, request):
        return json.loads(self.client.DeviceMaintenance.Perform(
            request["requestId"], request["incidentId"], request["action"],
            request["expectedRevision"]).Result)

    def execute(self, command):
        if not isinstance(command, dict) or set(command) != {"commandId", "deviceId", "durationMs"}:
            raise ValueError("Expected commandId, deviceId and durationMs")
        if command["deviceId"] != "measurement-1":
            raise ValueError("Unknown device")
        instance = self.client.ExperimentDevice.Execute(command["commandId"], command["durationMs"])
        try:
            deadline = time.monotonic() + 12
            while not instance.done:
                if time.monotonic() > deadline:
                    # No automatic retry: the device may still be executing.
                    raise TimeoutError("Device outcome unknown; inspect command status before retrying")
                time.sleep(0.02)
            return json.loads(instance.get_responses().Result)
        finally:
            instance.cancel_execution_info_subscription()

    def close(self):
        self.subscription.cancel()
        self.client.close()
