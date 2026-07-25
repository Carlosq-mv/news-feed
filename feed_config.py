import json
import logging


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


def validate_fields(feeds: list[dict[str, str]]) -> list[dict[str, str]]:
    """Validate that each feed entry has a non-empty source and url

    Args:
        feeds: A list of dict that represents the structure of the json data

    Returns:
        A list of dict with valid source and url of feeds.
    """

    valid_feeds = []

    for feed in feeds:
        # retrieve source and url
        source = feed.get("source")
        url = feed.get("url")

        # check if source and url are present in feed
        if not source or not url:
            # skip the feed is one of these is not included
            logger.error(f"Invalid feed entry, skipping: {feed}")
            continue

        valid_feeds.append(feed)

    # return valid feeds with source and url
    return valid_feeds
