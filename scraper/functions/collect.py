"""The implementation of the collect function."""
import ast
import logging
import re
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from scraper.exceptions import ResultParseError
from scraper.functions import Args, Func
from scraper.utils import dict_update, re_sub, str_to_etree, strip

_logger = logging.getLogger(__name__)

# define the valid string template pattern
_pattern = re.compile(r"\s*\[.*]\s*")


@dataclass(init=False)
class CollectArgs(Args):
    """Arguments for the collect function."""

    source: Any
    into: dict

    def parse(self, rawargs: dict, context: dict) -> "CollectArgs":
        source = context[rawargs["source"]]
        from_ = rawargs.get("from")
        if from_ is not None:
            source = _render(from_, source)

        self.source = source
        self.into = self.substitute(rawargs["into"], context)
        return self


@Func("collect", CollectArgs)
def collect(args: CollectArgs, context: dict) -> None:
    """Collect data from a source and put it into the context."""
    for ctxkey, tmpl in args.into.items():
        try:
            result = _render(tmpl, args.source)
        except Exception as e:
            _logger.error('Failed to collect "%s" using "%s"', ctxkey, tmpl)
            raise ResultParseError from e

        target = context.get(ctxkey)
        if isinstance(target, list) and isinstance(result, list):
            target.extend(result)
        elif isinstance(target, dict) and isinstance(result, dict):
            dict_update(target, result)
        else:
            context[ctxkey] = result
        _logger.info('Collected "%s" using "%s"', ctxkey, tmpl)
        _logger.debug("<==  result: %s", context[ctxkey])


def _render(tmpl: Any, source, etree=None):
    """Render a template with the given source."""
    if etree is None and _need_etree(tmpl):
        etree = str_to_etree(source)

    if isinstance(tmpl, list):
        return [_render(item, source, etree) for item in tmpl]
    elif isinstance(tmpl, dict):
        return {k: _render(v, source, etree) for k, v in tmpl.items()}
    elif isinstance(tmpl, str):
        return _render_str(tmpl, source, etree)
    return tmpl


def _render_str(tmpl: str, source, etree):
    """Render a string template with the given source."""
    if len(tmpl.strip()) == 0:
        return ""
    elif re.fullmatch(_pattern, tmpl) is None:
        return tmpl

    # evaluate the string template to get strategy and arguments
    finder, expr, *modification = ast.literal_eval(tmpl)

    # find result from source
    result = None
    if isinstance(source, str):
        if finder.startswith("xp_"):
            result = _xpath_find(finder[3:], expr, etree)
        elif finder.startswith("re_"):
            result = _regex_match(finder[3:], expr, source)
    elif isinstance(source, dict) and finder == "get":
        result = source.get(expr)

    # modify result if needed
    if result is not None and len(modification) > 0:
        modifier, *args = modification
        result = _modify(result, modifier, args)
    return strip(result)


def _need_etree(tmpl: Any):
    """Check if the template needs an etree."""
    if isinstance(tmpl, list):
        return any(_need_etree(item) for item in tmpl)
    elif isinstance(tmpl, dict):
        return any(_need_etree(v) for v in tmpl.values())
    elif isinstance(tmpl, str):
        return "xp_" in tmpl
    return False


def _xpath_find(strategy: str, expr: str, etree: Element):
    """Find strings in an element tree using xpath."""
    if strategy == "elem":
        elem = etree.find(expr)
        if elem is not None:
            return ElementTree.tostring(elem, encoding="unicode")
    elif strategy == "elems":
        elist = etree.findall(expr)
        return [ElementTree.tostring(e, encoding="unicode") for e in elist]
    elif strategy == "text":
        return etree.findtext(expr)
    elif strategy == "texts":
        return [e.text for e in etree.findall(expr)]
    elif strategy.startswith("attr_"):
        elem = etree.find(expr)
        if elem is not None:
            return elem.attrib[strategy[6:]]
    elif strategy.startswith("attrs_"):
        elist = etree.findall(expr)
        return [e.attrib[strategy[7:]] for e in elist]
    return None


def _regex_match(strategy: str, expr: str, source: str):
    """Match strings in a source string using regex."""
    pattern = re.compile(expr, re.DOTALL)
    if strategy == "match":
        matches = pattern.search(source)
        return matches.group(1) if matches else None
    elif strategy == "matches":
        return pattern.findall(source)
    return None


def _modify(result: Any, strategy: str, args: list):
    """Modify the result using the given strategy and arguments."""
    if strategy == "split" and len(args) == 1:
        sep = args[0]
        result = result.split(sep) if isinstance(result, str) else result
    elif strategy == "re_sub" and len(args) == 2:
        pattern, repl = args
        result = re_sub(result, pattern, repl)
    return result
