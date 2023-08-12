"""The implementation of the loop function."""
import logging
from dataclasses import dataclass
from typing import Generator, List, Optional, Tuple

from scraper.functions import Args, Func, functions

_logger = logging.getLogger(__name__)


@dataclass(init=False)
class LoopArgs(Args):
    """Arguments for the loop function."""

    source: list
    item: str
    steps: List[Tuple[str, dict]]
    iferr: Optional[str]

    def parse(self, rawargs: dict, context: dict) -> "LoopArgs":
        self.source = context[rawargs["source"]]
        self.item = rawargs["item"]
        self.steps = [s.popitem() for s in rawargs["steps"]]
        self.iferr = rawargs.get("iferr")
        return self


@Func("loop", LoopArgs)
def loop(args: LoopArgs, context: dict) -> Generator:
    """Loop over a list of items and execute steps."""
    for i in range(len(args.source)):
        subcontext = {
            "$parent": context,
            "site": context["site"],
            args.item: args.source[i]
        }
        try:
            for funcname, rawargs in args.steps:
                # execute the function with subcontext
                result = functions[funcname](rawargs, subcontext)
                if result is not None:
                    yield result
            args.source[i] = subcontext[args.item]
        except Exception as e:
            if args.iferr == "continue":
                _logger.error("Error occurred in loop", exc_info=True)
                continue
            raise e
