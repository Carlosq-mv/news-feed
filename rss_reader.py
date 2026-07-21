import requests
import feedparser
import logging
import time

from datetime import datetime


logger = logging.getLogger(__name__)


def get_rss(rss: dict[str, str]) -> str | None:
    """Fetch the ram XML content of RSS feed.

    Args:
        rss: A dict with 'source' and 'url' identifying the feed.

    Returns:
        The raw XML feed as a string or None if an error occurred or
        the request failed.
    """

    rss_source = rss.get("source")
    rss_url = rss.get("url")

    # check if there is a url and source
    if rss_url is None or rss_source is None:
        logger.error(f"Invalid feed config: {rss}")
        return None

    logger.info(f"Checking feed: source {rss_source.upper()}")

    try:
        # get the rss feed from the given url
        res = requests.get(rss_url, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch feed: {e}")
        return None

    logger.info(f"Successfully fetched feed: {rss_source.upper()}")
    xml_doc = res.text
    return xml_doc


def parse_rss(xml_doc: str, source: str) -> list[dict]:
    """Parse the XML string representation of the RSS feed to retrieve the desired fields.

    Args:
        xml_doc: A string representation of the raw XML feed
        source: A string that gives the name of the article provider (i.e. Variety)

    Returns:
        A list of dict that contains only the desired fields, extracted from the XML RSS feed,
        or an empty list if the XML RSS feed contains no articles
    """

    logger.info(f"Parsing XML feed: {source.upper()}")

    xml = feedparser.parse(xml_doc)

    # check if the xml is malformed
    if xml.bozo:
        logger.warning(f"Feed has a parse issuse: {xml.bozo_exception}")

    # check if there are usable entries in the parsed xml
    if not xml.entries:
        logger.warning(f"Feed {source} has returned no usable entries")
        return []

    # gather and retrieve relevant information of every article
    logger.info(f"Gathering and retrieving articles: {source.upper()}")
    articles = []
    for article in xml.entries:
        # change format of published time
        date_posted = datetime.fromtimestamp(
            time.mktime(article.get("published_parsed"))
        )

        # add articles to list with appropriate fields
        articles.append(
            {
                "guid": article.get("guid"),
                "source": source,
                "title": article.get("title"),
                "author": article.get("author"),
                "link": article.get("link"),
                "date_posted": date_posted,
            }
        )
    logger.info(f"Successfully gathered articles: {source.upper()}")

    return articles
