import wiki_grapher_db
import sqlite3

while True:
    line = input("SQL>")
    if line is None or line == "quit":
        print("Goodbye")
        break
    elif line == "commit":
        wiki_grapher_db.connection.commit()
    elif line == "rollback":
        wiki_grapher_db.connection.rollback()
    else:
        try:
            result_cursor = wiki_grapher_db.connection.execute(line)
            result = result_cursor.fetchall()
            print("Success ("+str(len(result))+"):")
            if result_cursor.description is not None:
                columns, = result_cursor.description
                for column_name in columns:
                    if column_name is None:
                        break
                    else:
                        print("{:32} |".format(column_name), end="")
                print()
            for result_line in result:
                for r in result_line:
                    print("{:32} |".format(r), end="")
                print()
        except sqlite3.Error as err:
            print("Error:")
            print(err)


