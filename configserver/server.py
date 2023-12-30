"""A simple HTTP server for configuration."""
import ast
import http
import json
import string
import sys
from http.server import HTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 5125

# define the base directory
_basedir = Path(__file__).resolve().parent

# initialize the templates
with open(_basedir / "templates/config.html", "r", encoding="utf-8") as html:
    _config_tmpl = string.Template(html.read())
with open(_basedir / "templates/source.html", "r", encoding="utf-8") as html:
    _source_tmpl = string.Template(html.read())
with open(_basedir / "templates/index.html", "r", encoding="utf-8") as html:
    _index_tmpl = string.Template(html.read())

# initialize the DoH resolvers
with open(_basedir / "../resolvers.conf", "r", encoding="utf-8") as doh_reader:
    _doh_resolvers = ast.literal_eval(doh_reader.read())


def render_index(saved=None):
    """Render the index page."""
    source_html = ""
    sites = load_sites()
    for site, site_conf in sites.items():
        saved_conf = saved.get(site) if saved is not None else None
        config_html = render_config(site, site_conf, saved_conf)
        types = site_conf["types"]
        doh_enabled = site_conf["doh_enabled"]
        source = {
            "site": site,
            "movie": "selected" if "movie" in types else "disabled",
            "tvshow": "selected" if "tvshow" in types else "disabled",
            "doh_enabled": "selected" if doh_enabled else "",
            "doh_disabled": "selected" if not doh_enabled else "",
            "priority": len(sites),
            "config": config_html,
        }
        if saved_conf is not None:
            saved_types = saved_conf["types"]
            saved_doh = saved_conf["doh"]
            source["movie"] = "selected" if "movie" in saved_types else ""
            source["tvshow"] = "selected" if "tvshow" in saved_types else ""
            source["doh_enabled"] = "selected" if saved_doh else ""
            source["doh_disabled"] = "selected" if not saved_doh else ""
            source["priority"] = saved_conf["priority"]
        source_html += _source_tmpl.substitute(source)

    return _index_tmpl.substitute(
        sources=source_html, resolvers=_doh_resolvers, version=plugin_version()
    )


def render_config(site, site_conf, saved_conf):
    """Render the configuration for a site."""
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
        with open(filepath, "r", encoding="utf-8") as def_reader:
            flowdef = json.load(def_reader)
        site = flowdef["site"]
        site_conf = sites.get(site, {})
        site_conf["doh_enabled"] = flowdef.get("doh_enabled", False)

        # aggregate types
        type_ = flowdef["type"].split("_", 1)[0]
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


def plugin_version():
    """Get the plugin version from the directory name."""
    dir_name = _basedir.parent.name
    if "-" in dir_name:
        version = dir_name.split("-")[-1]
        if version != "plugin":
            return f"v{version}"
    return ""


# initialize the index page
_index_html = render_index()


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for the HTTP server."""

    def do_AUTH(self):
        filepath = _basedir / "authorization"
        if not filepath.exists():
            return True

        with open(filepath, "r", encoding="utf-8") as auth_reader:
            saved_auth = auth_reader.read()

        if self.headers.get("Authorization") is not None:
            auth_header = self.headers.get("Authorization")
            if auth_header.split("Basic ")[1] == saved_auth:
                return True

        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Login Required"')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Unauthorized")
        return False

    def do_GET(self):
        if not self.do_AUTH():
            return

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            filepath = _basedir / "../scrapeflows.conf"
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as conf_reader:
                    saved_conf = json.load(conf_reader)
                self.wfile.write(render_index(saved_conf).encode("utf-8"))
            else:
                self.wfile.write(_index_html.encode("utf-8"))

        elif self.path == "/exit":
            self.send_response(200)
            self.end_headers()
            self.server.server_close()
            sys.exit()

    def do_POST(self):
        if not self.do_AUTH():
            return

        filepath = None
        if self.path == "/save":
            filepath = _basedir / "../scrapeflows.conf"
        elif self.path == "/auth":
            filepath = _basedir / "authorization"

        if filepath is not None:
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            with open(filepath, "w", encoding="utf-8") as writer:
                writer.write(body.decode("utf-8"))
            self.send_response(200)
            self.end_headers()


if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), RequestHandler)
    httpd.serve_forever()
