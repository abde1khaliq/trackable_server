"""
Minimal test server for the trackable/watcher project.

Serves an HTML page with several independently trackable elements:
- A timestamp that changes every request (guaranteed change detection)
- A price that changes on a schedule (simulates "real" intermittent change)
- A stock status that flips occasionally
- A static element that never changes (negative test — should NEVER trigger)
- Two elements sharing a class name (tests CSS selector disambiguation:
  nth-of-type, data-* scoping, etc.)

Run:
    python test_server.py

Example trackables to create against this page (url: http://localhost:8080):
    tracked_element_selector: .tracked-timestamp   -> changes every request
    tracked_element_selector: .tracked-price        -> changes every ~10s
    tracked_element_selector: .tracked-stock        -> changes every ~30s
    tracked_element_selector: .tracked-static        -> never changes
    tracked_element_selector: [data-product="1"] .price_color  -> disambiguated
    tracked_element_selector: [data-product="2"] .price_color  -> disambiguated
    tracked_element_selector: .price_color:nth-of-type(2)       -> index-based alt
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone


def do_get_dynamic_values():
    now = datetime.now(timezone.utc)

    # Changes every request
    timestamp = now.isoformat()

    # Changes roughly every 10 seconds
    price = 50 + (now.second // 10) * 5

    # Flips roughly every 30 seconds
    in_stock = (now.second // 30) % 2 == 0

    return timestamp, price, in_stock


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        timestamp, price, in_stock = do_get_dynamic_values()
        stock_label = "In Stock" if in_stock else "Out of Stock"

        html = f"""<!DOCTYPE html>
<html>
<head><title>Trackable Test Page</title></head>
<body>
    <h1>Watcher Test Page</h1>

    <p class="tracked-timestamp">Server time: {timestamp}</p>
    <p class="tracked-price">Price: ${price}</p>
    <p class="tracked-stock">Status: {stock_label}</p>
    <p class="tracked-static">This text never changes.</p>

    <div data-product="1">
        <span class="price_color">$50</span>
    </div>
    <div data-product="2">
        <span class="price_color">$75</span>
    </div>
</body>
</html>"""

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving test page on http://localhost:{port}")
    server.serve_forever()