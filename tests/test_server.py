"""
Minimal test server for the trackable/watcher project.

Serves an HTML page with an element whose text content changes on
every single request (down to the second) — guaranteeing your
watcher will detect a change on any check, regardless of how you've
set interval_minutes.

Run:
    python test_server.py

Then in your app, create a trackable with:
    url: http://localhost:8080
    tracked_element_class: tracked-content
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        now = datetime.now(timezone.utc)

        html = f"""<!DOCTYPE html>
<html>
<head><title>Trackable Test Page</title></head>
<body>
    <h1>Watcher Test Page</h1>
    <p class="tracked-content">Server time: {now.isoformat()}</p>
</body>
</html>"""

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # quiet default request logging, comment out if you want to see hits
        pass


if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving test page on http://localhost:{port}")
    server.serve_forever()