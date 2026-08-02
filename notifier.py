import logging
import requests
import groq

from config import GROQ_KEY, MODEL_NAME

logger = logging.getLogger(__name__)

client = groq.Groq(api_key=GROQ_KEY)


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


def should_notify(article: dict, prompt_template: str) -> bool:
    """Ask an LLM  whether this article matches notification preferences.

    Args:
        article: A dict with title and summary fields.
        prompt_template: The filtering criteria, loaded from prompt.txt.

    Returns:
        True if the article should be notified on, False otherwise
        (including if the API call fails — fails closed).
    """

    title = article.get("title", "")
    summary = article.get("summary", "")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=10,
            messages=[
                {"role": "system", "content": prompt_template},
                {"role": "user", "content": f"Title: {title}\nSummary: {summary}"},
            ],
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer.startswith("YES")
    except Exception as e:
        logger.error(f"LLM filter check failed for article '{title}': {e}")
        return False
