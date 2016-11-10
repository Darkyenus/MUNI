import wiki_grapher_db
import sqlite3
import time


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

            start_time = time.time()

            def print_timing():
                print("({:.0f} seconds elapsed)".format(time.time() - start_time))

            # Already visited articles -> path to that article in chain of titles
            tried = dict()
            tried[from_id] = (from_id,)
            current_distance = 0
            max_distance = 128

            to_try_next = [from_id]

            while True:
                if to_id in to_try_next:
                    print("Distance is "+str(current_distance)+", path is:")
                    print(" -> ".join(list(map(wiki_grapher_db.find_title_of, tried[to_id]))))
                    print("Visited "+str(len(tried) - len(to_try_next))+" articles in the process")
                    print_timing()
                    return True

                if current_distance > max_distance:
                    print("Distance can't be determined, too far?")
                    print_timing()
                    return True

                print("... not "+str(current_distance)+" ", end="")
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
                    print(to_title+" is unreachable from "+from_title)
                    return True

                current_distance += 1

        return False
    except Exception as ex:
        print(str(ex))
        print("Need help?")
        print("id_references_id <id>")
        return True


def start_console():
    while True:
        line = input(">")
        if line is None or line == "quit":
            print("Goodbye")
            break
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
