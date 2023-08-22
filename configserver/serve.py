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
with open(_basedir / "templates/config.html", "r", encoding="utf-8") as html:
    _config_tmpl = string.Template(html.read())
with open(_basedir / "templates/source.html", "r", encoding="utf-8") as html:
    _source_tmpl = string.Template(html.read())
with open(_basedir / "templates/index.html", "r", encoding="utf-8") as html:
    _index_tmpl = string.Template(html.read())


def render_index(saved=None):
    """Render the index page."""
    source_html = ""
    for site, site_conf in load_sites().items():
        saved_conf = saved.get(site) if saved is not None else None
        config_html = render_config(site, site_conf, saved_conf)
        types = site_conf["types"]
        source = {
            "site": site,
            "movie": "selected" if "movie" in types else "disabled",
            "tvshow": "selected" if "tvshow" in types else "disabled",
            "priority": 999,
            "config": config_html
        }
        if saved_conf is not None:
            saved_types = saved_conf["types"]
            source["movie"] = "selected" if "movie" in saved_types else ""
            source["tvshow"] = "selected" if "tvshow" in saved_types else ""
            source["priority"] = saved_conf["priority"]
        source_html += _source_tmpl.substitute(source)

    return _index_tmpl.substitute(sources=source_html)


def render_config(site, site_conf, saved_conf):
    config_html = ""
    config = site_conf.get("config")
    if config is not None:
        for key, option in config.items():
            value = saved_conf.get(key, "") if saved_conf is not None else ""
            mapping = {"site": site, "key": key, "value": value}
            mapping.update(option)
            config_html += _config_tmpl.substitute(mapping)
    return config_html


def load_sites():
    """Load the list of sites and types from flow definitions."""
    sites = {}
    for filepath in (_basedir / "../scrapeflows").glob("*.json"):
        with open(filepath, "r", encoding="utf-8") as flowdef_json:
            flowdef = json.load(flowdef_json)
        site = flowdef["site"]
        type_ = flowdef["type"].split("_", 1)[0]

        # aggregate types
        site_conf = sites.get(site, {})
        types = site_conf.get("types", [])
        if type_ not in types:
            types.append(type_)
        site_conf["types"] = types

        # aggregate config
        if "config" in flowdef:
            config = site_conf.get("config", {})
            config.update(flowdef["config"])
            site_conf["config"] = config

        sites[site] = site_conf

    return dict(sorted(sites.items(), key=lambda x: x[0]))


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
            self.end_headers()
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
