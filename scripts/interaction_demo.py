"""Launch the four local processes or exercise their public interfaces."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import ProxyHandler, build_opener, Request

ROOT = Path(__file__).resolve().parents[1]
HTTP = build_opener(ProxyHandler({}))


def call(port, path, body=None):
    raw = None if body is None else json.dumps(body).encode()
    with HTTP.open(Request(f"http://127.0.0.1:{port}{path}", data=raw,
                           headers={"Content-Type": "application/json"}), timeout=20) as response:
        return json.load(response)


def wait_ready(port, process):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Process for port {port} exited: {process.returncode}")
        try:
            call(port, "/health")
            return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"Port {port} did not become ready")


class Stack:
    def __enter__(self):
        self.processes = []
        try:
            for port in (8010, 8011, 8012, 8013, 50052):
                with socket.socket() as probe:
                    probe.bind(("127.0.0.1", port))
            components = [
                ("simulators/measurement", 8013),
                ("services/device-gateway", 8012),
                ("services/workflow-worker", 8011),
                ("services/platform-api", 8010),
            ]
            for component, port in components:
                env = os.environ.copy()
                env["NO_PROXY"] = "127.0.0.1,localhost"
                env["PYTHONPATH"] = os.pathsep.join(str(ROOT / path) for path in
                    (component + "/src", "packages", "contracts/sila2/generated", "simulators/runtime"))
                process = subprocess.Popen([sys.executable, "-u", str(ROOT / component / "src/interfaces/main.py")],
                                           cwd=ROOT, env=env)
                self.processes.append(process)
                wait_ready(port, process)
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        for process in reversed(self.processes):
            if process.poll() is None:
                process.terminate()
        for process in self.processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def scenario(mode):
    call(8013, "/v1/chaos", {"mode": mode})
    accepted = call(8010, "/v1/experiments", {"steps": [{"deviceId": "measurement-1", "durationMs": 400}]})
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        run = call(8010, "/v1/runs/" + accepted["runId"])
        if run["state"] in ("succeeded", "failed"):
            print(json.dumps(run, indent=2), flush=True)
            return run
        time.sleep(0.05)
    raise TimeoutError("Run did not finish")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("serve", "normal", "delay", "fail"))
    args = parser.parse_args()
    if args.action == "serve":
        with Stack():
            print("Ready: platform :8010, workflow :8011, gateway :8012, simulator admin :8013 / SiLA :50052", flush=True)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
    else:
        scenario(args.action)
