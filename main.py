"""Prints the output of the scraper to the console."""
import os

import scraper

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_id = os.path.basename(root_dir)
    print(scraper.scrape(plugin_id))
