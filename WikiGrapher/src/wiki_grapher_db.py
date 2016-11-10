import sqlite3

connection = sqlite3.connect("wiki-db.db")
connection.execute("CREATE TABLE IF NOT EXISTS article (article_id INTEGER PRIMARY KEY NOT NULL, article_title TEXT NOT NULL)")
connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS article_title_index ON article(article_title)")
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
    s = "SELECT article_unresolved_reference.article_id, article.article_id, article_unresolved_reference.is_redirect FROM article_unresolved_reference INNER JOIN article ON article_unresolved_reference.to_article_title = article.article_title"
    connection.execute("INSERT INTO article_reference (article_id, to_article_id, is_redirect) "+s)
    connection.execute("DELETE FROM article_unresolved_reference WHERE article_id IN (SELECT article_id FROM article_reference)")
    connection.commit()


def find_id_of(article_title):
    found = connection.execute("SELECT article_id FROM article WHERE article_title=?", (article_title,)).fetchone()
    if found is not None:
        return found[0]
    else:
        return None


def find_title_of(article_id):
    found = connection.execute("SELECT article_title FROM article WHERE article_id=?", (article_id,)).fetchone()
    if found is not None:
        return found[0]
    else:
        return None


def article_ids_references_ids(article_ids):
    result = set()
    if article_ids is None:
        return None
    for article_id in article_ids:
        for row in connection.execute("SELECT to_article_id FROM article_reference WHERE article_id=?", (article_id,)).fetchall():
            result.add(row[0])
    return result


def article_id_references_ids(article_id):
    result = []
    for row in connection.execute("SELECT to_article_id FROM article_reference WHERE article_id=?", (article_id,)).fetchall():
        result.append(row[0])
    return result