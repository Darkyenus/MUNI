import re


_LINK_REGEX = re.compile("\\[\\[([^\\]#|]+)(?:[^\\]]*)\\]\\]")


def extract_links(wiki_text):
    result = set()
    for link in _LINK_REGEX.finditer(wiki_text):
        link_content = link.group(1)

        hash_index = link_content.find("#")
        if hash_index != -1:
            link_content = link_content[0:hash_index]
        else:
            pipe_index = link_content.find("|")
            if pipe_index != -1:
                link_content = link_content[0:hash_index]

        link_content = link_content.strip()

        if len(link_content) != 0:
            result.add(link_content[0].upper() + link_content[1:])
    return result

#print(extract_links("Welcome to the Paradise [[City]], where grass is [[Green (color)|green]] and the girls are [[Beauty#pretty|pretty]]!"))
