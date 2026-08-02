CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    guid TEXT,
    source TEXT,
    title TEXT,
    author TEXT,
    link TEXT,
    summary TEXT,
    date_posted DATETIME,
    UNIQUE (source, guid)
);
