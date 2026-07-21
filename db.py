import sqlite3
import logging

logger = logging.getLogger(__name__)

# create new database connection
conn = sqlite3.connect("articles.db")

# create database cursor
cursor = conn.cursor()


def init_db() -> None:
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
    try:
        conn.close()
        logger.info("Database connection closed")
    except sqlite3.Error as e:
        logger.error(f"Error closing database connection: {e}")


def insert_article(article: dict[str, str]) -> bool:
    statement = """
        INSERT INTO articles (guid, source, title, author, link, date_posted) 
        VALUES (:guid, :source, :title, :author, :link, :date_posted)
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
    statement = """
        SELECT  1 FROM articles
        WHERE source = ? AND guid = ?
    """
    article_id = f"<{source}-{guid}>"
    try:
        cursor.execute(statement, (source, guid))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Database error checking article: {article_id}: {e}")
        return False
