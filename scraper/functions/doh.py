"""The implementation of the doh function."""
import json
import logging
import socket
import urllib
import urllib.request
from dataclasses import dataclass
from typing import List, Optional

from scraper.exceptions import RequestSendError
from scraper.functions import Args, Func

_logger = logging.getLogger(__name__)
_registered_hosts = set()
_doh_resolvers = [
    # https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https
    "1.1.1.1/dns-query",

    # https://developers.google.com/speed/public-dns/docs/doh
    "8.8.8.8/resolve"
]


def _patched_getaddrinfo(host, *args, **kwargs):
    """Patched version of socket.getaddrinfo."""
    if host in _registered_hosts:
        for resolver in _doh_resolvers:
            ip = _doh_query(resolver, host)
            if ip is not None:
                _logger.info("Resolved %s to %s", host, ip)
                host = ip
                break
    return _orig_getaddrinfo(host, *args, **kwargs)


# monkey patch socket.getaddrinfo
_orig_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = _patched_getaddrinfo


def _doh_query(resolver: str, host: str) -> Optional[str]:
    """Query the IP address of the given host using the given DoH resolver."""
    url = f"https://{resolver}?name={host}&type=A"
    headers = {"Accept": "application/dns-json"}
    _logger.info("DoH request: %s", url)

    try:
        request = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=5) as response:
            _logger.info("DoH response: %s", response.status)

            if response.status == 200:
                response_body = response.read().decode("utf-8")
                _logger.debug("<==  body: %s", response_body)

                answer = json.loads(response_body)["Answer"]
                return answer[0]["data"]
            else:
                return None
    except Exception as e:
        _logger.error("DoH request error: %s", e)
        raise RequestSendError from e


@dataclass(init=False)
class DohArgs(Args):
    """Arguments for the doh function."""

    hosts: List[str]

    def parse(self, rawargs: dict, _) -> "DohArgs":
        self.hosts = rawargs.get("hosts", [])
        if "host" in rawargs:
            self.hosts.append(rawargs["host"])
        return self


@Func("doh", DohArgs)
def doh(args: DohArgs, _) -> None:
    """Put the given hosts into the registered hosts set."""
    _registered_hosts.update(args.hosts)
