import bz2
import xml.etree.ElementTree
import xml.parsers.expat
import wiki_grapher_db
import wiki_grapher_wikitext
import time


class BZip2Reader:

    def __init__(self, file_name):
        self.file = open(file_name, mode="rb")
        import os
        self.file_size = os.path.getsize(file_name)
        self.decompresor = bz2.BZ2Decompressor()

    def read(self, length):
        block_size = 16384
        result_bytes = bytearray()
        while len(result_bytes) < length:
            block = self.file.read(block_size)
            if len(block) == 0:
                break
            else:
                # noinspection PyArgumentList
                result_bytes.extend(self.decompresor.decompress(block))
        return result_bytes

    @property
    def percent_read(self):
        return self.file.tell() / self.file_size


def wiki_tag(tag_name):
    return '{http://www.mediawiki.org/xml/export-0.10/}'+tag_name

TAG_SITE_INFO = wiki_tag("siteinfo")
TAG_PAGE = wiki_tag("page")
TAG_TITLE = wiki_tag("title")
TAG_REVISION = wiki_tag("revision")
TAG_TEXT = wiki_tag("text")
TAG_REDIRECT = wiki_tag("redirect")


def is_valid_page_title(title):
    return isinstance(title, str) and not (title.startswith("Wikipedia:")
                or (title.startswith(":") and len(title) > 3 and title[3] == ":" and not title.startswith(":en:")) # Links to different language wikis
                or title.startswith("File:")
                or title.startswith("Media:")
                or title.startswith("Mediawiki:")
                or title.startswith("Image:")
                or title.startswith("Category:")
                or title.startswith("Help:")
                or title.startswith("Portal:")
                or title.startswith("Template:")
                or title.startswith("Draft:")
                or title.startswith("Book:")
                or title.startswith("TimedText:")
                or title.startswith("Wiktionary:")
                # Common
                or title.startswith("Zh-yue:")
                or title.startswith("Wiktionary:")
                or title.startswith("Wikt:")
                # Match errors
                or "\n" in title
                or "[" in title)


def process_page(page_element):
    title = page_element.find(TAG_TITLE).text
    if not is_valid_page_title(title):
        return
    redirect = page_element.find(TAG_REDIRECT)
    article_id = wiki_grapher_db.create_article(title)
    if redirect is not None:
        redirected_to = redirect.get("title")
        wiki_grapher_db.create_unresolved_reference(article_id, redirected_to, True)
    else:
        text = page_element.find(TAG_REVISION).find(TAG_TEXT).text
        if isinstance(text, str):
            links_to = wiki_grapher_wikitext.extract_links(text)
            for link in links_to:
                if is_valid_page_title(link):
                    wiki_grapher_db.create_unresolved_reference(article_id, link, False)
            if len(links_to) != 0:
                return
        else:
            print("WARN: did not get string but ", text)
    #wiki_grapher_db.commit() Done outside for performance


start_time = time.time()


def print_progress():
    current_time = time.time()
    time_elapsed = current_time - start_time
    percent_complete = reader.percent_read
    time_remaining = (time_elapsed / percent_complete) * (1 - percent_complete)
    print("{:.2%} of file processed, {:.0f} seconds elapsed, {:.0f} remaining".format(percent_complete, time_elapsed, time_remaining))

stat_counter = 0
reader = BZip2Reader("enwiki-latest-pages-articles.xml.bz2")
for (event, element) in xml.etree.ElementTree.iterparse(reader):
    if element.tag == TAG_SITE_INFO:
        element.clear()
    elif element.tag == TAG_PAGE:
        process_page(element)
        element.clear()
        stat_counter += 1
        if stat_counter % 10000 == 0:
            # Commit is slow, therefore done only infrequently
            wiki_grapher_db.commit()
            print_progress()
wiki_grapher_db.commit()
print_progress()
print("Resolving references...")
wiki_grapher_db.resolve_references()
print("Done")
