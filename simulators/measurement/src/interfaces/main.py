import json
import os
from datetime import timedelta

from sila2.server import SilaServer
from experimentdevice import ExperimentDeviceBase, ExperimentDeviceFeature, Execute_Responses
from engine import Engine
from interaction_http import serve
from devicemaintenance import DeviceMaintenanceBase, DeviceMaintenanceFeature, Perform_Responses


class MaintenanceDevice(DeviceMaintenanceBase):
    def __init__(self, server, engine):
        super().__init__(server)
        self.engine = engine

    def get_State(self, *, metadata):
        return json.dumps(self.engine.maintenance_state())

    def Perform(self, RequestId, IncidentId, Action, ExpectedRevision, *, metadata):
        return Perform_Responses(Result=json.dumps(
            self.engine.maintain(RequestId, IncidentId, Action, ExpectedRevision)))


class Device(ExperimentDeviceBase):
    def __init__(self, server, engine):
        super().__init__(server)
        self.engine = engine
        self.Execute_default_lifetime_of_execution = timedelta(minutes=5)
        self.update_Status(json.dumps({"deviceId": "measurement-1", "commandId": None,
                                       "state": "idle", "progress": 0, "sequence": 0}))

    def Execute(self, CommandId, DurationMs, *, metadata, instance):
        instance.begin_execution()
        result = self.engine.execute(
            CommandId, DurationMs,
            lambda status: self.update_Status(json.dumps(status)),
            lambda percent: setattr(instance, "progress", percent / 100),
        )
        return Execute_Responses(Result=json.dumps(result))


if __name__ == "__main__":
    engine = Engine()
    server = SilaServer("Measurement Simulator", "Measurement", "Interaction demo", "0.1", "https://example.invalid")
    server.set_feature_implementation(ExperimentDeviceFeature, Device(server, engine))
    server.set_feature_implementation(DeviceMaintenanceFeature, MaintenanceDevice(server, engine))
    # Local development only. Both protocol and chaos management bind to loopback.
    server.start_insecure("127.0.0.1", int(os.environ.get("SILA_PORT", 50052)), enable_discovery=False)

    def dispatch(method, path, body):
        if method == "GET" and path == "/health":
            return {"service": "measurement-simulator", "status": "ready"}
        if method == "POST" and path == "/v1/chaos":
            return engine.configure(body)
        if method == "POST" and path == "/v2/faults":
            return engine.inject_fault(body)
        raise ValueError("Unknown simulator management route")

    try:
        serve(int(os.environ.get("SIM_ADMIN_PORT", 8013)), dispatch)
    finally:
        server.stop()
