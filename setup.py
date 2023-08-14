"""Package script for this plugin."""
import os
import string

from setuptools import find_packages, setup

from version import version

root_dir = os.path.dirname(os.path.abspath(__file__))

# use the name of the root directory as the plugin id
plugin_id = os.path.basename(root_dir)

# write the INFO file for this plugin
info_tmpl = """
{
  "id": "${plugin_id}-${version}",
  "entry_file": "run.sh",
  "type": ["movie", "tvshow"],
  "language": ["chs"],
  "test_example": {
    "movie": {
      "title": "两杆大烟枪",
      "original_available": "1998-08-28"
    },
    "tvshow": {
      "title": "怪奇物语 第一季",
      "original_available": "2016-07-15"
    },
    "tvshow_episode": {
      "title": "怪奇物语 第一季",
      "original_available": "2016-07-15",
      "season": 1,
      "episode": 1
    }
  }
}
"""
with open(os.path.join(root_dir, "INFO"), "w", encoding="utf-8") as writer:
    template = string.Template(info_tmpl)
    writer.write(template.substitute(plugin_id=plugin_id, version=version()))

# use 'python setup.py sdist --formats=zip' command to create the zip file
setup(
    name=plugin_id,
    version=version(),
    packages=find_packages(),
    package_data={
        "": ["run.sh", "INFO"],
        "scrapeflows": ["*.json"],
        "configserver": ["*.html"]
    },
    python_requires=">=3.7",
)
