import os
from infrastructure.sila_device import SilaDevice
from interaction_http import serve


if __name__ == "__main__":
    device = SilaDevice(int(os.environ.get("SILA_PORT", 50052)))

    def dispatch(method, path, body):
        if method == "GET" and path == "/health":
            return {"service": "device-gateway", "status": "ready"}
        if method == "GET" and path == "/v1/observations":
            return device.observations()
        if method == "POST" and path == "/v1/commands":
            return device.execute(body)
        raise ValueError("Unknown gateway route")

    try:
        serve(int(os.environ.get("GATEWAY_PORT", 8012)), dispatch)
    finally:
        device.close()
