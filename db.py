import sqlite3
import logging

logger = logging.getLogger(__name__)

# create new database connection
conn = sqlite3.connect("articles.db")

# create database cursor
cursor = conn.cursor()

# open file with table schema
with open("sql/schema.sql", "r") as f:
    schema_sql = f.read()


# execute the sql script
cursor.executescript(schema_sql)


def insert_article(article: dict[str, str]):
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
