from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
import urllib.parse


class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, data=None, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        if data is not None:
            if isinstance(data, (dict, list)):
                self.wfile.write(json.dumps(data).encode())
            elif isinstance(data, str):
                self.wfile.write(data.encode())
            else:
                self.wfile.write(data)

    def do_POST(self):
        if self.path == "/upload/video":
            # read and discard body
            _ = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            upload_id = f"upload-{uuid.uuid4().hex}"
            self._send(200, {"upload_id": upload_id})
            return

        if self.path == "/video/publish":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b""
            post_id = f"post-{uuid.uuid4().hex}"
            self._send(200, {"post_id": post_id, "status": "processing"})
            return

        self._send(404, {"error": "not found"})

    def do_GET(self):
        # status check: /video/status/{post_id}
        parts = self.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "video" and parts[1] == "status":
            post_id = parts[2]
            # immediately return published for deterministic test
            self._send(200, {"status": "published"})
            return

        self._send(404, {"error": "not found"})

    def do_DELETE(self):
        # delete: /video/{post_id}
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "video":
            self._send(204, "")
            return
        self._send(404, {"error": "not found"})


def run(port: int = 8001):
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Mock publish server listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    run()
