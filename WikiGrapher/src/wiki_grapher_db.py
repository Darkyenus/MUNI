import sqlite3

connection = sqlite3.connect("wiki-db.db")
connection.execute("CREATE TABLE IF NOT EXISTS article (article_title TEXT PRIMARY KEY NOT NULL) WITHOUT ROWID")
connection.execute("CREATE TABLE IF NOT EXISTS article_redirect (from_article TEXT NOT NULL, to_article TEXT NOT NULL, PRIMARY KEY(from_article, to_article)) WITHOUT ROWID")
connection.execute("CREATE TABLE IF NOT EXISTS article_reference (from_article TEXT NOT NULL, to_article TEXT NOT NULL, PRIMARY KEY(from_article, to_article)) WITHOUT ROWID")
connection.commit()


def create_article(title):
    connection.execute("INSERT OR IGNORE INTO article VALUES (?)", (title,))


def create_redirect(article_origin, article_target):
    connection.execute("INSERT OR IGNORE INTO article_redirect VALUES (?, ?)", (article_origin, article_target))


def create_reference(article_origin, article_target):
    connection.execute("INSERT OR IGNORE INTO article_reference VALUES (?, ?)", (article_origin, article_target))


def commit():
    connection.commit()
