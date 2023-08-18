"""The implementation of the retval function."""
import ast
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

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

        compare = rawargs.get("compare")
        if compare is not None:
            left_key, operator, right_key = ast.literal_eval(compare)
            left = context.get(left_key)
            right = context.get(right_key)
            condition &= _compare(left, operator, right)

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


def _compare(left: Any, operator: str, right: Any) -> bool:
    """Compare two values with the given operator."""
    if left is None or right is None:
        return True  # ignore compare if either value is None
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return _compare_num(left, operator, right)
    if isinstance(left, str) and isinstance(right, str):
        return _compare_num(_timestamp(left), operator, _timestamp(right))
    return False


def _compare_num(
    left: Union[int, float], operator: str, right: Union[int, float]
) -> bool:
    """Compare two numbers with the given operator."""
    if operator == "==":
        return left == right
    elif operator == "!=":
        return left != right
    elif operator == ">":
        return left > right
    elif operator == ">=":
        return left >= right
    elif operator == "<":
        return left < right
    elif operator == "<=":
        return left <= right
    else:
        return False


def _timestamp(time_str: str) -> float:
    """Convert a time string to timestamp."""
    if len(time_str) == 4:
        format_str = "%Y"
    elif len(time_str) == 7:
        format_str = "%Y-%m"
    else:
        format_str = "%Y-%m-%d"

    try:
        return datetime.strptime(time_str, format_str).timestamp()
    except ValueError:
        return 0
