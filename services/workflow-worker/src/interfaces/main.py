import os
from application.runtime import Runtime
from interaction_http import request, serve

GATEWAY = os.environ.get("GATEWAY_URL", "http://127.0.0.1:8012")
runtime = Runtime(lambda command: request(GATEWAY + "/v1/commands", command))


def dispatch(method, path, body):
    if method == "GET" and path == "/health":
        return {"service": "workflow-worker", "status": "ready"}
    if method == "POST" and path == "/v1/runs":
        return runtime.submit(body)
    if method == "GET" and path.startswith("/v1/runs/"):
        return runtime.get(path.removeprefix("/v1/runs/"))
    raise ValueError("Unknown workflow route")


if __name__ == "__main__":
    serve(int(os.environ.get("WORKFLOW_PORT", 8011)), dispatch)
