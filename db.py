import sqlite3
import logging

logger = logging.getLogger(__name__)

# create new database connection
conn = sqlite3.connect("articles.db")

# create database cursor
cursor = conn.cursor()


def init_db() -> None:
    """Initialize the database schema from sql/schema.sql.
    Creates the articles table if it doesn't already exist. Raises the
    underlying exception after logging, since the program cannot
    proceed without a valid schema.
    """
    try:
        # open file with table schema
        with open("sql/schema.sql", "r") as f:
            schema_sql = f.read()

        # execute the sql script
        cursor.executescript(schema_sql)
        logger.info("Database schema initialized")

    except (OSError, sqlite3.Error) as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise


def close_db() -> None:
    """Close the database connection."""

    try:
        conn.close()
        logger.info("Database connection closed")
    except sqlite3.Error as e:
        logger.error(f"Error closing database connection: {e}")


def insert_article(article: dict[str, str]) -> bool:
    """Insert new article into the database.

    Args:
        article: a dict representing the article with the following fields.
        guid, source, title, author, link and date_posted.

    Returns:
        True if the article was successfully inserted and False if the article
        was not inserted (duplicate or database error occurred).
    """

    statement = """
        INSERT INTO articles (guid, source, title, author, link, summary, date_posted)
        VALUES (:guid, :source, :title, :author, :link, :summary, :date_posted)
    """
    article_id = f"<{article.get('source')}-{article.get('guid')}>"

    try:
        cursor.execute(statement, article)
        conn.commit()
        logger.info(f"Successfully inserted article: {article_id}")
        return True

    except sqlite3.IntegrityError as e:
        logger.error(f"Duplicate article insert attempted: {article_id}: {e}")
        return False

    except sqlite3.Error as e:
        logger.error(f"Database error inserting article {article_id}: {e}")
        return False


def does_article_exists(source: str, guid: str) -> bool:
    """Checks if a particular article exists in the database.

    Args:
        source: A string that represents the source of the news outlet.
        guid: A string the represents the guid of the article.

    Returns:
        True if the article exists, False otherwise (including database errors).
    """

    statement = """
        SELECT 1 FROM articles
        WHERE source = ? AND guid = ?
    """
    article_id = f"<{source}-{guid}>"
    try:
        cursor.execute(statement, (source, guid))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Database error checking article: {article_id}: {e}")
        return False


def has_any_articles(source: str) -> bool:
    """Checks if any articles have been committed for a committed source.

    Args:
        source: A string that represents the source of the news outlet.

    Returns:
        True if the source has any articles False otherwise (including database errors).

    """

    statement = """
        SELECT 1 FROM articles
        WHERE source = ?
        LIMIT 1
    """
    try:
        cursor.execute(statement, (source,))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Database error checking source: {source.upper()}: {e}")
        return False
