"""A simple HTTP server for configuration."""
import http
import os
import sys
from http.server import HTTPServer

_basedir = os.path.dirname(os.path.realpath(__file__))
_index = os.path.join(_basedir, "index.html")


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for the HTTP server."""

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(_index, "r", encoding="utf-8") as file:
                html = file.read()
            self.wfile.write(html.encode("utf-8"))

        elif self.path.endswith("/close"):
            self.send_response(200)
            self.wfile.write(b"Closing server...")
            self.server.server_close()
            sys.exit()


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5125
    httpd = HTTPServer((host, port), RequestHandler)
    httpd.serve_forever()
