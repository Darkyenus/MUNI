from wiki_grapher_db import *


def distance_between(from_title, to_title):
    if not article_exists(from_title) or not article_exists(to_title):
        return None
