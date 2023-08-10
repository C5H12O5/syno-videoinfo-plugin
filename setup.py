"""Package script for this plugin."""
import os
import string

from setuptools import setup

from version import version

_info_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "INFO")
_info_tmpl = """
{
    "id": "syno-videoinfo-plugin-$version",
    "entry_file": "run.sh",
    "type": ["movie"],
    "language": ["chs"],
    "test_example": {
        "movie": {
            "title": "巨齿鲨2",
            "original_available": "2023-08-04"
        }
    }
}
"""

with open(_info_file, "w", encoding="utf-8") as f:
    f.write(string.Template(_info_tmpl).substitute(version=version()))

setup(
    name="syno-videoinfo-plugin",
    version=version(),
    packages=["", "scraper", "scraper.functions", "scrapeflows"],
    package_data={"": ["run.sh", "main.py", "INFO"], "scrapeflows": ["*.json"]},
)
