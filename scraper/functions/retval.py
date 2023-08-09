"""The implementation of the retval function."""
from dataclasses import dataclass
from typing import Any

from scraper.functions import Args, Func


@dataclass(init=False)
class RetvalArgs(Args):
    """Arguments for the retval function."""

    ctxkey: str

    def parse(self, rawargs: str, _) -> "RetvalArgs":
        self.ctxkey = rawargs
        return self


@Func("retval", RetvalArgs)
def retval(args: RetvalArgs, context: dict) -> Any:
    """Return the value from context with given key."""
    return context[args.ctxkey]
