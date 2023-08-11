"""The implementation of the collect function."""
import logging
import re
from dataclasses import dataclass
from typing import Any, Union
from xml.etree import ElementTree

from scraper.exceptions import ResultParseError
from scraper.functions import Args, Func
from scraper.utils import deep_update, str_to_etree, strip

_logger = logging.getLogger(__name__)


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
            deep_update(target, result)
        else:
            context[ctxkey] = result
        _logger.info('Collected "%s" using "%s"', ctxkey, tmpl)
        _logger.debug("<==  result: %s", context[ctxkey])


def _render(tmpl: Union[list, dict, str], source, etree=None):
    """Render a template with the given source."""
    if etree is None and _need_etree(tmpl):
        etree = str_to_etree(source)

    if isinstance(tmpl, list):
        return [_render(item, source, etree) for item in tmpl]
    elif isinstance(tmpl, dict):
        return {k: _render(v, source, etree) for k, v in tmpl.items()}
    elif isinstance(tmpl, str):
        return _render_str(tmpl, source, etree)


def _render_str(tmpl: str, source, etree):
    """Render a string template with the given source."""
    if len(tmpl.strip()) == 0:
        return ""
    if ":" not in tmpl:
        return tmpl
    # split template into strategy and expression
    strategy, expr = [s.strip() for s in tmpl.split(":", 1)]
    if isinstance(source, str):
        if strategy.startswith("x"):
            return strip(_xpath_find(strategy, expr, etree))
        else:
            return strip(_regex_match(strategy, expr, source))
    elif isinstance(source, dict):
        if strategy == "get":
            return source.get(expr)
    else:
        return None


def _need_etree(tmpl: Union[list, dict, str]):
    """Check if the template needs an etree."""
    if isinstance(tmpl, list):
        return any(_need_etree(item) for item in tmpl)
    elif isinstance(tmpl, dict):
        return any(_need_etree(v) for v in tmpl.values())
    elif isinstance(tmpl, str):
        return ":" in tmpl and tmpl.split(":", 1)[0].startswith("x")
    return False


def _xpath_find(strategy: str, expr: str, etree):
    """Find strings in an element tree using xpath."""
    if strategy == "xelem":
        elem = etree.find(expr)
        if elem is not None:
            return ElementTree.tostring(elem, encoding="unicode")
    elif strategy == "xelems":
        elist = etree.findall(expr)
        return [ElementTree.tostring(e, encoding="unicode") for e in elist]
    elif strategy == "xtext":
        return etree.findtext(expr)
    elif strategy == "xtexts":
        return [e.text for e in etree.findall(expr)]
    elif strategy.startswith("xattr_"):
        elem = etree.find(expr)
        if elem is not None:
            return elem.attrib[strategy[6:]]
    elif strategy.startswith("xattrs_"):
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
