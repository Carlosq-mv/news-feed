import logging
import json
import sys

from rss_reader import fetch_rss_xml, parse_rss_xml
from db import insert_article, does_article_exists

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


def main():
    """Rundown of workflow:
    retrieve feed data from json files
    validate feed data from json data (make sure source and url fields are present)
    get rss data for every feed
    parse the rss feeds to only get desired data from the articles
    check if article is in database
    if not in database commit to database
    """
    # retrieve the feeds with source and url from json file
    feeds = load_feed_config(sys.argv[1])

    # validate the feeds
    valid_feeds = validate_fields(feeds)

    for feed in valid_feeds:
        raw_xml_data = fetch_rss_xml(feed)

        if not raw_xml_data:
            logger.warning(f"Skipping feed, no XML data returned: {feed.get('source')}")
            continue

        # NOTE: guid and source are validated in previous functions
        parsed_xml_data = parse_rss_xml(raw_xml_data, feed.get("source"))  # type: ignore

        for article in parsed_xml_data:
            # check if article exists is in database
            source, guid = article.get("source"), article.get("guid")  # type: ignore

            # skip article if it is a duplicate
            if does_article_exists(source, guid):  # type: ignore
                continue

            # insert article into database
            insert_article(article)


main()
