"""Small JSON HTTP transport shared by the local demo processes."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dataclasses import dataclass


@dataclass(frozen=True)
class HtmlResponse:
    content: str


def request(url, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=20) as response:
            return json.load(response)
    except HTTPError as error:
        raise ValueError(error.read().decode()) from error


def serve(port, dispatch):
    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                if not 0 <= length <= 65536:
                    raise ValueError("Request body must be at most 64 KiB")
                body = json.loads(self.rfile.read(length)) if length else None
                result = dispatch(self.command, self.path, body)
                status = 200
            except (ValueError, TypeError, KeyError) as error:
                status, result = 400, {"error": str(error)}
            except Exception as error:
                status, result = 502, {"error": str(error)}
            html = isinstance(result, HtmlResponse)
            raw = result.content.encode("utf-8") if html else json.dumps(result).encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8" if html else "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        do_GET = do_POST = handle_request

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(json.dumps({"listening": port}), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
