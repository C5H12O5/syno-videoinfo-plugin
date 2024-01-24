"""Package script for this plugin."""
import string
from pathlib import Path

from setuptools import setup

from version import version

# get the root directory of this plugin
ROOT_DIR = Path(__file__).resolve().parent

# use the name of the root directory as the plugin id
PLUGIN_ID = ROOT_DIR.name

# write the INFO file for this plugin
INFO_TMPL = """
{
  "id": "${plugin_id}-${version}",
  "entry_file": "run.sh",
  "type": ["movie", "tvshow"],
  "language": ["chs"],
  "test_example": {
    "movie": {
      "title": "--install"
    },
    "tvshow": {
      "title": "--install"
    },
    "tvshow_episode": {
      "title": "--install",
      "season": 1,
      "episode": 1
    }
  }
}
"""
with open(ROOT_DIR / "INFO", "w", encoding="utf-8") as writer:
    template = string.Template(INFO_TMPL)
    writer.write(template.substitute(plugin_id=PLUGIN_ID, version=version()))

# use 'python setup.py sdist --formats=zip' command to create the zip file
setup(
    name=PLUGIN_ID,
    version=version(),
    packages=[
        "",
        "scraper",
        "scraper.functions",
        "scrapeflows",
        "configserver"
    ],
    package_data={
        "": ["run.sh", "resolvers.conf", "INFO"],
        "scrapeflows": ["*.json"],
        "configserver": ["templates/*.html"],
    },
    python_requires=">=3.6",
)
