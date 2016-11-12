import wiki_grapher_db
import sqlite3
import time


def compute_distance(from_id, to_id, verbose, max_distance=128):
    start_time = time.time()

    def print_timing():
        print("({:.0f} seconds elapsed)".format(time.time() - start_time))

    # Already visited articles -> path to that article in chain of titles
    tried = dict()
    tried[from_id] = (from_id,)
    current_distance = 0

    to_try_next = [from_id]

    while True:
        if to_id in to_try_next:
            if verbose:
                print("Distance is "+str(current_distance)+", path is:")
                print(" -> ".join(list(map(wiki_grapher_db.find_title_of, tried[to_id]))))
                print("Visited "+str(len(tried) - len(to_try_next))+" articles in the process")
                print_timing()
            return current_distance

        if current_distance > max_distance:
            if verbose:
                print("Distance can't be determined, too far?")
                print_timing()
            return None

        if verbose:
            print("... not {}, trying {} more articles ".format(str(current_distance), len(to_try_next)), end="")
            print_timing()


        new_to_try_next = []

        for next_to_try in to_try_next:
            references = wiki_grapher_db.article_id_references_ids(next_to_try)
            for reference in references:
                if reference in tried:
                    continue
                tried[reference] = tried[next_to_try] + (reference,)
                new_to_try_next.append(reference)

        to_try_next = new_to_try_next

        if len(new_to_try_next) == 0:
            if verbose:
                print("Article is unreachable")
            return None

        current_distance += 1


def analyze_command(command):
    try:
        args = command.split(" ")
        if args[0] == "id_references_id":
            ref_set = wiki_grapher_db.article_ids_references_ids([int(args[1])])
            if ref_set is None:
                print("ID "+args[1]+" does not exist")
                return True
            print("ID "+args[1]+" references "+str(len(ref_set))+" articles:")
            for r in ref_set:
                print(str(r))
            return True
        if args[0] == "title_of":
            for i in args[1:]:
                print("Title of "+i+" is "+str(wiki_grapher_db.find_title_of(int(i))))
            return True
        if args[0] == "id_of":
            title = " ".join(args[1:])
            print("Id of "+title+" is "+str(wiki_grapher_db.find_id_of(title)))
            return True
        if args[0] == "titles_like":
            title = " ".join(args[1:])
            found_titles_like = wiki_grapher_db.find_article_titles_of_title_like(title)
            print("Found "+str(len(found_titles_like))+" articles with name like \""+title+"\":")
            i = 0
            for t in found_titles_like:
                i += 1
                if i % 10 == 0:
                    inp = input("Enter to continue...")
                    if len(inp) != 0:
                        print("Aborted")
                        break
                print(t)
            return True
        if args[0] == "resolve":
            title = " ".join(args[1:])
            original_id = wiki_grapher_db.find_id_of(title)
            if original_id is None:
                print("Article "+title+" does not exist")
            redirects_to_id = wiki_grapher_db.resolve_id_redirect(original_id)
            print(title+" ("+str(original_id)+") redirects to "+wiki_grapher_db.find_title_of(redirects_to_id)+" ("+str(redirects_to_id)+")")
            return True
        if args[0] == "references":
            title = " ".join(args[1:])
            title_id = wiki_grapher_db.find_id_of(title)
            ref_set = wiki_grapher_db.article_ids_references_ids([title_id])
            if ref_set is None:
                print("Title "+title+" does not exist")
                return True
            title_set = map(wiki_grapher_db.find_title_of, ref_set)
            print(title+" references "+str(len(ref_set))+" articles:")
            for r in title_set:
                print(r)
            return True
        if args[0] == "distance":
            from_title = " ".join(args[1:])
            from_id = wiki_grapher_db.find_id_of(from_title)
            if from_id is None:
                print("Article "+from_title+" does not exist")
                return True

            to_title = input("to: ")
            to_id = wiki_grapher_db.find_id_of(to_title)
            if to_id is None:
                print("Article "+to_title+" does not exist")
                return True
            to_id_resolves_to = wiki_grapher_db.resolve_id_redirect(to_id)
            if to_id_resolves_to != to_id:
                print("Article "+to_title+" redirects to "+wiki_grapher_db.find_title_of(to_id_resolves_to)+", finding distance to that")
                to_id = to_id_resolves_to

            compute_distance(from_id, to_id, True)
        if args[0] == "average_distance":
            sample_count = int(args[1])
            verbose = True if len(args) >= 3 and args[2].startswith("v") else False
            random_article_iterator = wiki_grapher_db.RandomOrderArticleIdIterator()
            lengths = []

            max_distance = -1
            max_distance_pair = None

            for _ in range(0, sample_count):
                from_id = random_article_iterator.next()
                to_id = random_article_iterator.next()

                if verbose:
                    print("Searching path from {} to {}".format(wiki_grapher_db.find_title_of(from_id), wiki_grapher_db.find_title_of(to_id)))

                distance = compute_distance(from_id, to_id, verbose)
                if distance is not None:
                    lengths.append(distance)

                    if distance > max_distance:
                        max_distance = distance
                        max_distance_pair = (from_id, to_id)

            print("\nSampling complete\nResults:")
            print("Scanned {} samples, found {} paths {:%}".format(sample_count, len(lengths), len(lengths) / sample_count))
            lengths.sort(reverse=True)
            print("Average path length is {:.4}".format(sum(lengths) / len(lengths)))
            print("Median path length is {:.2}".format((lengths[len(lengths) // 2] + lengths[(len(lengths) + 1) // 2]) / 2))
            print("Longest path is {} long, between {} and {}".format(max_distance, wiki_grapher_db.find_title_of(max_distance_pair[0]), wiki_grapher_db.find_title_of(max_distance_pair[1])))
            return True

        return False
    except Exception as ex:
        print(str(ex))
        print("Need help?")
        print("id_references_id <id>            Print ID's of all articles referenced by <id>")
        print("title_of <id>                    Print title of article with <id>")
        print("id_of <title>                    Print id of article with <title>")
        print("titles_like <title pattern>      Print titles of articles with titles matched by SQL LIKE pattern <title pattern>")
        print("resolve <title>                  Print title of article to which <title> redirects (or <title> if it does not redirect)")
        print("references <title>               Print titles of articles which <title> references")
        print("distance <from_title>            (Asks for destination later) Print shortest referential distance from")
        print("                                 given title to second given title, with arbitrary chain of articles which gives such distance")
        print("average_distance <samples> [v]   Randomly computes <samples> path distances between any articles and prints statistical report")
        return True


def start_console():
    while True:
        line = input(">")
        if line is None or line == "quit":
            print("Goodbye")
            break
        elif line == "":
            pass
        elif line == "commit":
            wiki_grapher_db.connection.commit()
        elif line == "rollback":
            wiki_grapher_db.connection.rollback()
        elif line == "resolve_references":
            wiki_grapher_db.resolve_references()
        elif analyze_command(line):
            pass
        else:
            try:
                result_cursor = wiki_grapher_db.connection.execute(line)
                result = result_cursor.fetchall()
                print("Success ("+str(len(result))+"):")
                columns = result_cursor.description
                if columns is not None:
                    for column_name_tuple in columns:
                        print("{:32} |".format(column_name_tuple[0]), end="")
                    print()
                for result_line in result:
                    for r in result_line:
                        print("{:32} |".format(r), end="")
                    print()
            except sqlite3.Error as err:
                print("Error:")
                print(err)

if __name__ == "__main__":
    start_console()
