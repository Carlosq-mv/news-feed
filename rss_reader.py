import requests
import feedparser
import logging

logger = logging.getLogger(__name__)


VARIETY_URL = "https://variety.com/feed/"


def get_rss(rss: dict[str, str]) -> str | None:
    rss_source = rss.get("source")
    rss_url = rss.get("url")

    if rss_url is None or rss_source is None:
        logger.error(f"Invalid feed config: {rss}")
        return None

    logger.info(f"Checking feed: source {rss_source}")

    try:
        res = requests.get(rss_url, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch feed: {e}")
        return None

    logger.info(f"Successfully fetched feed: {rss_source}")
    xml_doc = res.text
    return xml_doc
