"""A simple HTTP server for configuration."""
import http
import json
import string
import sys
from http.server import HTTPServer
from pathlib import Path

_host = "0.0.0.0"
_port = 5125
_index_html = ""
_basedir = Path(__file__).resolve().parent


def init_server():
    """Initialize the server."""
    global _index_html

    # get list of sites and types from flow definitions
    sites = {}
    for filepath in (_basedir / "../scrapeflows").glob("*.json"):
        with open(filepath, "r", encoding="utf-8") as flowdef_json:
            flowdef = json.load(flowdef_json)
            site = flowdef["site"]
            type_ = flowdef["type"].split("_", 1)[0]
            types = sites.get(site, [])
            if type_ not in types:
                types.append(type_)
            sites[site] = types

    # generate HTML for source list
    source_html = ""
    with open(_basedir / "templates/source.html", "r", encoding="utf-8") as html:
        source_tmpl = string.Template(html.read())
    for site, types in sites.items():
        movie = "selected" if "movie" in types else "disabled"
        tvshow = "selected" if "tvshow" in types else "disabled"
        source = {"site": site, "movie": movie, "tvshow": tvshow}
        source_html += source_tmpl.substitute(source)

    # generate HTML for index page
    with open(_basedir / "templates/index.html", "r", encoding="utf-8") as html:
        index_tmpl = string.Template(html.read())
        _index_html = index_tmpl.substitute(sources=source_html)


# initialize the server
init_server()


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for the HTTP server."""

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(_index_html.encode("utf-8"))

        elif self.path.endswith("/exit"):
            self.send_response(200)
            self.wfile.write(b"Closing server...")
            self.server.server_close()
            sys.exit()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        with open(_basedir / "../scrapeflows.conf", "w", encoding="utf-8") as w:
            w.write(body.decode("utf-8"))
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    httpd = HTTPServer((_host, _port), RequestHandler)
    httpd.serve_forever()
