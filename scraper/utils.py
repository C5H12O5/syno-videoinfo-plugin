"""Utility functions for this package."""
import json
from html.parser import HTMLParser
from typing import Any, List, Optional
from xml.etree import ElementTree

from scraper.exceptions import ResultParseError


def deep_update(d: dict, u: dict):
    """Recursively update a dictionary."""
    for k, v in u.items():
        if k in d and isinstance(d[k], dict) and isinstance(v, dict):
            d[k] = deep_update(d[k], v)
        else:
            d[k] = v
    return d


def strip(result: Any):
    """Strip leading and trailing whitespace."""
    if isinstance(result, list):
        return list(filter(lambda x: x is not None, [strip(i) for i in result]))
    elif isinstance(result, dict):
        return {k: strip(v) for k, v in result.items()}
    elif isinstance(result, str):
        result = result.strip()
        return result if result != "" else None
    return result


def str_to_etree(string: str) -> Optional[ElementTree.Element]:
    """Convert a string to an ElementTree."""
    string = string.strip()
    if string.startswith("{") or string.startswith("["):
        return json_to_etree(json.loads(string))
    elif string.startswith("<"):
        return html_to_etree(string)
    return None


def json_to_etree(json_obj: Any, tag: str = "root"):
    """Convert a JSON object to an ElementTree."""
    element = ElementTree.Element(tag)
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            element.append(json_to_etree(v, k))
    elif isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            element.append(json_to_etree(item, f"_{str(i)}"))
    elif json_obj is not None:
        element.text = str(json_obj)
    return element


def html_to_etree(html_text: str):
    """Convert an HTML text to an ElementTree."""
    return EtreeHTMLParser().parse(html_text)


class EtreeHTMLParser(HTMLParser):
    """Simple HTML parser that converts HTML to an ElementTree."""

    tag_stack: List[ElementTree.Element]
    cur_tag: Optional[ElementTree.Element]
    after_end: bool

    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.cur_tag = None
        self.after_end = False

    def handle_starttag(self, tag, attrs):
        self.after_end = False
        self.cur_tag = ElementTree.Element(tag, {k: v or "" for k, v in attrs})
        if len(self.tag_stack) > 0:
            self.tag_stack[-1].append(self.cur_tag)
        self.tag_stack.append(self.cur_tag)

    def handle_endtag(self, tag):
        while any(item.tag == tag for item in self.tag_stack):
            self.after_end = True
            self.cur_tag = self.tag_stack.pop()
            if self.cur_tag.tag == tag:
                break

    def handle_data(self, data):
        if self.cur_tag is not None:
            if self.after_end:
                self.cur_tag.tail = data.strip()
            else:
                self.cur_tag.text = data.strip()

    def error(self, message):
        raise ResultParseError

    def parse(self, html):
        self.feed(html)
        self.close()
        return self.cur_tag
