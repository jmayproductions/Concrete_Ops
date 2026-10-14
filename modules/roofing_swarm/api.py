"""HTTP API for Copilot Studio connectors."""
from __future__ import annotations
import argparse, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse
from modules.roofing_swarm.swarm import RoofingSwarm
from modules.roofing_swarm.workflows import WORKFLOW_IDS

class Handler(BaseHTTPRequestHandler):
    swarm = RoofingSwarm()
    def _send(self, code, payload):
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def log_message(self, fmt, *args):
        print(f"[roofing-swarm-api] {self.address_string()} {fmt % args}")
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")
        if path in ("/v1/workflows", "/v1/workflows/"):
            self._send(200, {"workflows": list(WORKFLOW_IDS)}); return
        if path in ("/health", "/v1/health"):
            self._send(200, {"ok": True}); return
        self._send(404, {"error": "not found"})
    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/"); prefix = "/v1/workflows/"
        if not path.startswith(prefix) or not path.endswith("/run"):
            self._send(404, {"error": "not found"}); return
        workflow_id = unquote(path[len(prefix):-len("/run")].strip("/"))
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try: payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid JSON"}); return
        context = payload.get("context") or {}
        if isinstance(payload.get("RoofContextJson"), str):
            try: context = {**context, **json.loads(payload["RoofContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "RoofContextJson is not valid JSON"}); return
        try: result = self.swarm.run(workflow_id, context)
        except ValueError as exc:
            self._send(400, {"error": str(exc)}); return
        self._send(200, result.to_dict())

def main():
    p = argparse.ArgumentParser(); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8100)
    args = p.parse_args()
    print(f"Roofing QAQC swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()

if __name__ == "__main__":
    main()
