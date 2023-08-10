"""Entry point for the scraper."""
import argparse
import json
import logging
import os
import threading
import time
from typing import Any, List

from scraper.exceptions import ScrapeError
from scraper.functions import findfunc

_logger = logging.getLogger(__name__)

# define default scraping config file path
_basedir = os.path.dirname(os.path.realpath(__file__))
_configpath = os.path.join(_basedir, "../scrapeflows")

# define maximum number of results to return
_maxlimit = 10
_lock = threading.Lock()
_results: List[Any] = []


def scrape(plugin_id: str) -> str:
    """Scrape video information from a given input."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--type", type=str, required=True)
    parser.add_argument("--lang", type=str, required=True)
    parser.add_argument("--limit", type=int, default=_maxlimit)
    parser.add_argument("--allowguess", action="store_true", default=False)
    parser.add_argument("--configpath", type=str, default=_configpath)
    parser.add_argument("--loglevel", type=str, default="critical")
    args = parser.parse_known_args()[0]
    maxlimit = min(args.limit, _maxlimit)

    # set basic logging configuration
    loglevel = getattr(logging, args.loglevel.upper())
    logformat = (
        "%(asctime)s %(threadName)s %(levelname)s "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    logging.basicConfig(level=loglevel, format=logformat)

    # parse --input argument as JSON
    jsoninput = json.loads(args.input)
    initialval = {
        "title": jsoninput["title"],
        "season": jsoninput.get("season", 0),
        "episode": jsoninput.get("episode", 1),
        "year": jsoninput.get("original_available", None),
        "lang": args.lang,
        "limit": maxlimit,
        "allowguess": args.allowguess,
    }

    # load and execute scrape flows using multithreading
    start = time.time()
    tasks = []
    for flow in ScrapeFlow.load(args.configpath, args.type, initialval):
        task = threading.Thread(target=_start, args=(flow, maxlimit))
        tasks.append(task)
        task.start()
    for task in tasks:
        task.join()
    end = time.time()
    _logger.info("Total execution time: %.3f seconds", end - start)
    return json.dumps(
        {"success": True, "result": _results}, ensure_ascii=False, indent=2
    ).replace("[plugin_id]", plugin_id)


def _start(flow: "ScrapeFlow", limit: int):
    """Start a scrape flow and store results."""
    try:
        result_gen = flow.start()
        while True:
            with _lock:
                if len(_results) >= limit:
                    break
                try:
                    _results.append(next(result_gen))
                except StopIteration:
                    break
    except ScrapeError as e:
        _logger.error("Error while scraping: %s", e)


class ScrapeFlow:
    """A flow of steps to scrape video information."""

    def __init__(self, site: str, steps: List[dict], context: dict):
        self.site = site
        self.steps = steps
        self.context = context

    def start(self):
        """Execute steps until an iterable is returned."""
        for funcname, rawargs in [s.popitem() for s in self.steps]:
            # execute the function with context
            iterable = findfunc(funcname)(rawargs, self.context)
            if iterable is not None:
                yield from iterable

    @staticmethod
    def load(path: str, videotype: str, initialval: dict):
        """Load scrape flows from given path."""
        for filename in [f for f in os.listdir(path) if f.endswith(".json")]:
            with open(
                os.path.join(path, filename), "r", encoding="utf-8"
            ) as flowdef_json:
                flowdef = json.load(flowdef_json)
                if flowdef["type"] != videotype:
                    continue
                # generate a flow instance from the definition
                yield ScrapeFlow(
                    flowdef["site"], list(flowdef["steps"]), initialval.copy()
                )
