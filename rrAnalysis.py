"""
This file interacts with Output/royalroad.db to analyze the data in there for relational data
"""

db_path = "Output/royalroad.db"

import sqlite3


# Prints out all the contents in the database
class readDatabase():
    def __init__(self):
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT Userid FROM users')
                rows = cur.fetchall()
                for row in rows:
                    print(row)
        except sqlite3.OperationalError as e:
            print(e)

if __name__ == '__main__':
    readDatabase()