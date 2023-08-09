"""The implementation of the HTTP function."""
import json
import logging
import os
import shelve
import time
import urllib
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any

from scraper.exceptions import RequestSendError
from scraper.functions import Args, Func

_logger = logging.getLogger(__name__)


# define default HTTP cache configuration
_currentdir = os.path.dirname(os.path.realpath(__file__))
_cache_name = ".httpcache"
_cache_file = os.path.join(_currentdir, _cache_name)
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
        self.url = self.substitute(rawargs["url"], context)  # type: ignore
        self.method = rawargs["method"].upper()
        self.headers = {
            k.lower(): self.substitute(v, context)
            for k, v in rawargs.get("headers", {}).items()
        }
        self.body = self.substitute(rawargs.get("body"), context)
        self.timeout = rawargs.get("timeout", 10)
        self.result = rawargs["result"]
        return self


@Func("http", HttpArgs)
def http(args: HttpArgs, context: dict) -> None:
    # send the HTTP request
    response = _http_request(
        args.url, args.method, args.headers, args.body, args.timeout
    )
    # put the response into the context
    context[args.result] = response


def _http_request(url, method, headers, body, timeout):
    _logger.info("HTTP request: %s %s", method, url)
    _logger.debug("==>  headers: %s", headers)
    _logger.debug("==>  body: %s", body)

    # urlencode the request query string
    url_split = url.split("?")
    if len(url_split) > 1:
        qs = urllib.parse.parse_qs(url_split[1])
        url = url_split[0] + "?" + urllib.parse.urlencode(qs, doseq=True)

    # process request body according to content type
    if body is not None and headers is not None:
        content_type = headers.get("content-type", "").lower()
        if content_type.startswith("application/json"):
            body = json.dumps(body, ensure_ascii=False)
        elif content_type.startswith("application/x-www-form-urlencoded"):
            body = urllib.parse.urlencode(body)

    # check if the cache is expired
    shelve_flag = "c"  # creating database if not exist
    for filename in os.listdir(_currentdir):
        if filename.startswith(_cache_name):
            shelve_file = os.path.join(_currentdir, filename)
            modify_time = os.path.getmtime(shelve_file)
            if (time.time() - modify_time) > _cache_expire:
                shelve_flag = "n"  # always create a new, empty database

    # send the request and cache the response
    with shelve.open(_cache_file, shelve_flag) as cache:
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
                cache[cache_key] = response_body
                _logger.info("HTTP response: %s", response.status)
                _logger.debug("<==  headers: %s", response.headers)
                _logger.debug("<==  body: %s", response_body)
                return response_body
        except Exception as e:
            _logger.error("HTTP request error: %s", e)
            raise RequestSendError from e
