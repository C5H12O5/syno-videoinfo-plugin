"""The implementation of the replace function."""
import logging
import re
from dataclasses import dataclass
from typing import Any

from scraper.functions import Args, Func

_logger = logging.getLogger(__name__)


@dataclass(init=False)
class ReplaceArgs(Args):
    """Arguments for the replace function."""

    ctxkey: str
    pattern: str
    replacement: str

    def parse(self, rawargs: dict, _) -> "ReplaceArgs":
        self.ctxkey = rawargs["source"]
        self.pattern = rawargs["pattern"]
        self.replacement = rawargs["replacement"]
        return self


@Func("replace", ReplaceArgs)
def replace(args: ReplaceArgs, context: dict) -> None:
    """Replace source with a pattern and put it back in the context."""
    source = context[args.ctxkey]
    context[args.ctxkey] = _re_sub(source, args.pattern, args.replacement)


def _re_sub(source: Any, pattern: str, repl: str) -> Any:
    """Recursively replace a pattern in a string, list, or dict."""
    if isinstance(source, str):
        return re.sub(pattern, repl, source)
    elif isinstance(source, list):
        return [_re_sub(item, pattern, repl) for item in source]
    elif isinstance(source, dict):
        return {k: _re_sub(v, pattern, repl) for k, v in source.items()}
    else:
        return source
