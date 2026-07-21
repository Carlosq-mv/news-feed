import logging
import json
import sys

from rss_reader import get_rss, parse_rss
from db import insert_article

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def load_feed_config(path: str) -> list[dict[str, str]]:
    """Load from a JSON file the source and url into a python dict.
    Args:
        path: A string that represents that file path to json file
              that contains the feeds.

    Returns:
        A list of dict with the source and url of feeds.
    """
    with open(path, "r") as f:
        feeds = json.load(f)
    return feeds
