"""The implementation of the retval function."""
from dataclasses import dataclass
from typing import Any, Optional

from scraper.exceptions import StopSignal
from scraper.functions import Args, Func


@dataclass(init=False)
class RetvalArgs(Args):
    """Arguments for the retval function."""

    condition: bool
    ctxkey: Optional[str]

    def parse(self, rawargs: dict, context: dict) -> "RetvalArgs":
        condition = True

        ifempty = rawargs.get("ifempty")
        if ifempty is not None:
            obj = context.get(ifempty)
            condition &= obj is None or len(obj) == 0

        notempty = rawargs.get("notempty")
        if notempty is not None:
            obj = context.get(notempty)
            condition &= obj is not None and len(obj) > 0

        self.condition = condition
        self.ctxkey = rawargs.get("source")
        return self


@Func("retval", RetvalArgs)
def retval(args: RetvalArgs, context: dict) -> Any:
    """Return the value from context with given key."""
    if args.condition:
        if args.ctxkey is not None:
            return context[args.ctxkey]
        else:
            raise StopSignal
