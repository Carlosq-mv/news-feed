import logging
import requests


logger = logging.getLogger(__name__)


def notify(article: dict[str, str], webhook_url: str):
    """Send a notification for a new article to a Discord webhook.

    Args:
        article: A dict with guid, source, title, author, link, and date_posted fields.
        webhook_url: The Discord webhook URL to send the message to.

    Returns:
        True if the notification was sent successfully, False if the request failed.
    """

    article_id = f"<{article.get('source')}-{article.get('guid')}>"
    title = article.get("title", "Untitled")
    link = article.get("link", "")
    source = article.get("source", "")

    payload = {"content": f"**{title}**\n{source.upper()}\n{link}"}

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        res.raise_for_status()
        logger.info(f"Successfully sent notification: {article_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send notification {article_id}: {e}")
        return False
