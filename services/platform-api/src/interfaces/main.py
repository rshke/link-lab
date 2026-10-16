import os
from application.admit import admit
from interaction_http import request, serve

WORKFLOW = os.environ.get("WORKFLOW_URL", "http://127.0.0.1:8011")


def dispatch(method, path, body):
    if method == "GET" and path == "/health":
        return {"service": "platform-api", "status": "ready"}
    if method == "POST" and path == "/v1/experiments":
        return admit(body, lambda plan: request(WORKFLOW + "/v1/runs", plan))
    if method == "GET" and path.startswith("/v1/runs/"):
        return request(WORKFLOW + path)
    raise ValueError("Unknown platform route")


if __name__ == "__main__":
    serve(int(os.environ.get("PLATFORM_PORT", 8010)), dispatch)
