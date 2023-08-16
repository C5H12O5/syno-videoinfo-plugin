"""A simple HTTP server for configuration."""
import http
import json
import string
import sys
from http.server import HTTPServer
from pathlib import Path

_host = "0.0.0.0"
_port = 5125
_basedir = Path(__file__).resolve().parent

# initialize the templates
with open(_basedir / "templates/source.html", "r", encoding="utf-8") as html:
    _source_tmpl = string.Template(html.read())
with open(_basedir / "templates/index.html", "r", encoding="utf-8") as html:
    _index_tmpl = string.Template(html.read())


def render_index(saved_conf=None):
    """Render the index page."""
    source_html = ""
    for site, types in load_sites().items():
        source = {
            "site": site,
            "movie": "selected" if "movie" in types else "disabled",
            "tvshow": "selected" if "tvshow" in types else "disabled",
            "priority": 999,
        }
        site_conf = saved_conf.get(site) if saved_conf is not None else None
        if site_conf is not None:
            saved_types = site_conf["types"]
            source["movie"] = "selected" if "movie" in saved_types else ""
            source["tvshow"] = "selected" if "tvshow" in saved_types else ""
            source["priority"] = site_conf["priority"]
        source_html += _source_tmpl.substitute(source)

    return _index_tmpl.substitute(sources=source_html)


def load_sites():
    """Load the list of sites and types from flow definitions."""
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
    return sites


# initialize the index page
_index_html = render_index()


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for the HTTP server."""

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            conf_path = _basedir / "../scrapeflows.conf"
            if conf_path.exists():
                with open(conf_path, "r", encoding="utf-8") as reader:
                    saved_conf = json.load(reader)
                self.wfile.write(render_index(saved_conf).encode("utf-8"))
            else:
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
