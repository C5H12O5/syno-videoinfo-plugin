"""A simple HTTP server for configuration."""
import http
import json
import os
import string
import sys
from http.server import HTTPServer
from typing import Any, Dict

basedir = os.path.dirname(os.path.realpath(__file__))

with open(
    os.path.join(basedir, "templates/source.html"), "r", encoding="utf-8"
) as html:
    source_tmpl = string.Template(html.read())

sites: Dict[Any, Any] = {}
configpath = os.path.join(basedir, "../scrapeflows")
for filename in [f for f in os.listdir(configpath) if f.endswith(".json")]:
    with open(
        os.path.join(configpath, filename), "r", encoding="utf-8"
    ) as flowdef_json:
        flowdef = json.load(flowdef_json)
        site = flowdef["site"]
        type_ = flowdef["type"].split("_", 1)[0]
        types = sites.get(site, [])
        if type_ not in types:
            types.append(type_)
        sites[site] = types

source_html = ""
for site, types in sites.items():
    movie = "selected" if "movie" in types else "disabled"
    tvshow = "selected" if "tvshow" in types else "disabled"
    source = {"site": site, "movie": movie, "tvshow": tvshow}
    source_html += source_tmpl.substitute(source)

with open(
    os.path.join(basedir, "templates/index.html"), "r", encoding="utf-8"
) as html:
    index_tmpl = string.Template(html.read())
    indel_html = index_tmpl.substitute(sources=source_html)


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for the HTTP server."""

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(indel_html.encode("utf-8"))

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
