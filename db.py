import sqlite3

# create new database connection
conn = sqlite3.connect("articles.db")

# create database cursor
cursor = conn.cursor()

# open file with table schema
with open("sql/schema.sql", "r") as f:
    schema_sql = f.read()


# execute the sql script
cursor.executescript(schema_sql)
