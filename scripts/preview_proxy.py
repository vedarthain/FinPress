import http.server
import urllib.request
import os

UPSTREAM = "https://finpress.deb5045ai.workers.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            return super().do_GET()
        if self.path.startswith("/api/"):
            return self.proxy("GET")
        return super().do_GET()

    def do_POST(self):
        return self.proxy("POST")

    def proxy(self, method):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            req = urllib.request.Request(UPSTREAM + self.path, data=body, method=method)
            for h in ("Content-Type",):
                if self.headers.get(h):
                    req.add_header(h, self.headers.get(h))
            with urllib.request.urlopen(req, timeout=15) as resp:
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(str(e).encode())


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("0.0.0.0", 8789), Handler).serve_forever()
