import logging
import sys
import time

from rss_reader import fetch_rss_xml, parse_rss_xml
from db import insert_article, does_article_exists, has_any_articles, init_db, close_db
from feed_config import load_feed_config, validate_fields
from notifier import notify, should_notify
from config import DISCORD_WEBHOOK_URL


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def load_prompt(path: str = "preferences/prompt.txt") -> str:
    with open(path, "r") as f:
        prompt = f.read().strip()
    return prompt


def main():
    try:
        init_db()
        # load llm prompt
        prompt_template = load_prompt()

        # retrieve the feeds with source and url from json file
        feeds = load_feed_config(sys.argv[1])

        # validate the feeds
        valid_feeds = validate_fields(feeds)

        for feed in valid_feeds:
            raw_xml_data = fetch_rss_xml(feed)

            if not raw_xml_data:
                logger.warning(
                    f"Skipping feed, no XML data returned: {feed.get('source')}"
                )
                continue

            # NOTE: guid is guaranteed non-empty by validation in parse_rss_xml
            # and source is guaranteed non-empty by validation in valid_feeds
            source = feed.get("source", "")

            # get list of articles for the particular source
            parsed_xml_data = parse_rss_xml(raw_xml_data, source)

            # first time seeing this source, seed silently and don't notify
            if not has_any_articles(source):
                # insert newest article only
                if parsed_xml_data:
                    insert_article(parsed_xml_data[0])

                logger.info(f"Seeded first article for new source: {source.upper()}")
                continue

            for article in parsed_xml_data:
                # check if article exists is in database
                guid = article.get("guid", "")

                # skip article if it is a duplicate
                if does_article_exists(source, guid):
                    break

                # insert article into database
                inserted = insert_article(article)

                if inserted and should_notify(article, prompt_template):
                    notify(article, DISCORD_WEBHOOK_URL)
                time.sleep(2.1)
    finally:
        close_db()


if __name__ == "__main__":
    main()
