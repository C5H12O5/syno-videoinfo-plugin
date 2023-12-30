"""Defines the function decorator and abstract base class for arguments."""
__all__ = ["Args", "Func", "findfunc", "functions"]

import inspect
import logging
import pkgutil
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Type

_logger = logging.getLogger(__name__)


class Args(ABC):
    """Abstract base class for function arguments."""

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)

    @abstractmethod
    def parse(self, rawargs: Any, context: dict) -> "Args":
        pass

    @staticmethod
    def substitute(obj: Any, context: dict) -> Any:
        """Recursively substitute strings in an object with given context."""
        if isinstance(obj, str):
            return obj.format(**context)
        elif isinstance(obj, list):
            return [Args.substitute(item, context) for item in obj]
        elif isinstance(obj, dict):
            return {k: Args.substitute(v, context) for k, v in obj.items()}
        else:
            return obj


class Func:
    """Function decorator for registering functions."""

    def __init__(self, name: str, args: Type[Args]):
        self.name = name
        self.args = args

    def __call__(self, func):
        @wraps(func)
        def wrapped(rawargs: Any, context: dict) -> Any:
            return func(self.args()(rawargs, context), context)

        # bind function name to a special attribute
        wrapped._funcname = self.name
        return wrapped


# a dictionary of all registered functions
functions = {}

# load all marked functions in this package
for loader, modname, _ in pkgutil.walk_packages(__path__):
    module = loader.find_spec(modname).loader.load_module(modname)
    funcs = inspect.getmembers(
        module, lambda m: (inspect.isfunction(m) and hasattr(m, "_funcname"))
    )
    _logger.info("Load %d executable functions in %s.py", len(funcs), modname)
    functions.update({getattr(func, "_funcname"): func for _, func in funcs})


def findfunc(funcname: str) -> Callable[[Any, dict], Any]:
    """Find a registered function by name."""
    func = functions.get(funcname)
    if func is None:
        _logger.error('Function "%s" not found', funcname)
        raise KeyError(f'Function "{funcname}" not found')
    return func
