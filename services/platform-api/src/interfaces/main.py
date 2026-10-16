import os
from pathlib import Path
from application.admit import admit
from application.maintenance import MaintenanceAdmission
from interaction_http import HtmlResponse, request, serve

WORKFLOW = os.environ.get("WORKFLOW_URL", "http://127.0.0.1:8011")
GATEWAY = os.environ.get("GATEWAY_URL", "http://127.0.0.1:8012")
maintenance = MaintenanceAdmission(lambda body: request(WORKFLOW + "/v1/maintenance/actions", body))
UI = Path(__file__).resolve().parents[4] / "apps/console/maintenance.html"


def dispatch(method, path, body):
    if method == "GET" and path in ("/", "/maintenance"):
        return HtmlResponse(UI.read_text(encoding="utf-8"))
    if method == "GET" and path == "/health":
        return {"service": "platform-api", "status": "ready"}
    if method == "GET" and path == "/v1/devices/measurement-1/capabilities":
        return request(GATEWAY + path)
    if method == "POST" and path == "/v1/experiments":
        return admit(body, lambda plan: request(WORKFLOW + "/v1/runs", plan))
    if method == "GET" and path == "/v1/maintenance":
        return request(WORKFLOW + path)
    if method == "GET" and path == "/v1/maintenance/audit":
        return maintenance.records()
    if method == "POST" and path == "/v1/maintenance/actions":
        return maintenance.perform(body)
    if method == "GET" and path.startswith("/v1/runs/"):
        return request(WORKFLOW + path)
    raise ValueError("Unknown platform route")


if __name__ == "__main__":
    serve(int(os.environ.get("PLATFORM_PORT", 8010)), dispatch)
