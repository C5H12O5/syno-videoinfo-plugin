"""Entry point for this plugin."""
from pathlib import Path

import scraper

if __name__ == "__main__":
    # Prints the output of the scraper to the console.
    root_dir = Path(__file__).resolve().parent
    plugin_id = root_dir.name
    print(scraper.scrape(plugin_id))
