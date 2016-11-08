import sqlite3

connection = sqlite3.connect("wiki-db.db")
connection.execute("CREATE TABLE IF NOT EXISTS article (article_id INTEGER PRIMARY KEY NOT NULL, article_title TEXT NOT NULL)")
connection.execute("CREATE TABLE IF NOT EXISTS article_unresolved_reference (article_id INTEGER NOT NULL, to_article_title TEXT NOT NULL, is_redirect INTEGER NOT NULL, PRIMARY KEY(article_id, to_article_title)) WITHOUT ROWID")
connection.execute("CREATE TABLE IF NOT EXISTS article_reference (article_id INTEGER NOT NULL, to_article_id INTEGER NOT NULL, is_redirect INTEGER NOT NULL, PRIMARY KEY(article_id, to_article_id)) WITHOUT ROWID")# , FOREIGN KEY (article_id, to_article_id) REFERENCES article(article_id, article_id) omitted for performance
connection.commit()


def create_article(title):
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO article (article_id, article_title) VALUES (NULL, ?)", (title,))
    article_id, = cursor.execute("SELECT article_id FROM article WHERE article_title=?", (title,)).fetchone()
    return article_id


def create_unresolved_reference(article_origin_id, article_target_title, redirect):
    connection.execute("INSERT OR IGNORE INTO article_unresolved_reference (article_id, to_article_title, is_redirect) VALUES (?, ?, ?)", (article_origin_id, article_target_title, 1 if redirect else 0))


def commit():
    connection.commit()


def resolve_references():
    s = "SELECT article_unresolved_reference.article_id, article.article_id FROM article_unresolved_reference INNER JOIN article ON article_unresolved_reference.to_article_title = article.article_title"
    connection.execute("INSERT INTO article_reference (article_id, to_article_id, is_redirect) "+s)
    #connection.execute("DELETE FROM article_unresolved_reference")