"""The implementation of the HTTP function."""
import json
import logging
import shelve
import time
import urllib
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any

from scraper.exceptions import RequestSendError
from scraper.functions import Args, Func

_logger = logging.getLogger(__name__)

# define default HTTP cache configuration
_basedir = Path(__file__).resolve().parent
_cache_prefix = ".cache_"
_cache_expire = 86400

# define a global opener and install it to urllib.request
_cookie_processor = urllib.request.HTTPCookieProcessor(CookieJar())
_global_opener = urllib.request.build_opener(_cookie_processor)
urllib.request.install_opener(_global_opener)


@dataclass(init=False)
class HttpArgs(Args):
    """Arguments for the HTTP function."""

    url: str
    method: str
    headers: dict
    body: Any
    timeout: float
    result: str

    def parse(self, rawargs: dict, context: dict) -> "HttpArgs":
        # urlencode the request query string
        url = self.substitute(rawargs["url"], context)
        url_split = url.split("?")
        if len(url_split) > 1:
            qs = urllib.parse.parse_qs(url_split[1])
            url = url_split[0] + "?" + urllib.parse.urlencode(qs, doseq=True)

        # substitute the request headers
        headers = {
            k.lower(): self.substitute(v, context)
            for k, v in rawargs.get("headers", {}).items()
        }

        # process request body according to the content-type
        body = self.substitute(rawargs.get("body"), context)
        if body is not None:
            content_type = headers.get("content-type", "").lower()
            if content_type.startswith("application/json"):
                body = json.dumps(body, ensure_ascii=False)
            elif content_type.startswith("application/x-www-form-urlencoded"):
                body = urllib.parse.urlencode(body)

        # construct the arguments
        self.url = url
        self.method = rawargs["method"].upper()
        self.headers = headers
        self.body = body
        self.timeout = rawargs.get("timeout", 10)
        self.result = rawargs["result"]
        return self


@Func("http", HttpArgs)
def http(args: HttpArgs, context: dict) -> None:
    cache_name = _cache_prefix + context["site"]
    # send the HTTP request
    response = _http_request(
        args.url, args.method, args.headers, args.body, args.timeout, cache_name
    )
    # put the response into the context
    context[args.result] = response


def _http_request(url, method, headers, body, timeout, cache_name):
    """Send an HTTP request and return the response body."""
    _logger.info("HTTP request: %s %s", method, url)
    _logger.debug("==>  headers: %s", headers)
    _logger.debug("==>  body: %s", body)

    # check if the cache is expired
    shelve_flag = "c"  # creating database if not exist
    for cache_file in _basedir.glob("cache_name*"):
        modify_time = cache_file.stat().st_mtime
        if (time.time() - modify_time) > _cache_expire:
            shelve_flag = "n"  # always create a new, empty database

    # send the request and cache the response
    with shelve.open(str(_basedir / cache_name), shelve_flag) as cache:
        cache_key = url + str(body)
        if cache_key in cache:
            response_body = cache[cache_key]
            _logger.info("HTTP response: cached")
            _logger.debug("<==  body: %s", response_body)
            return response_body

        try:
            body = body.encode("utf-8") if body is not None else None
            request = urllib.request.Request(url, body, headers, method=method)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
                if 200 <= response.status < 300:
                    cache[cache_key] = response_body
                _logger.info("HTTP response: %s", response.status)
                _logger.debug("<==  headers: %s", response.headers)
                _logger.debug("<==  body: %s", response_body)
                return response_body
        except Exception as e:
            _logger.error("HTTP request error: %s", e)
            raise RequestSendError from e
