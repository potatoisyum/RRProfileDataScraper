"""
This file interacts with Output/royalroad.db to analyze the data in there for relational data

TODO a dict reconstructor given a user ID
TODO a generalized full sheet printer
TODO a gneralized individual searcher for ALL sheets
"""

db_path = "Output/royalroad.db"

import sqlite3


# Prints out all the contents in the database
class readDatabase():
    def __init__(self):
        self.getAllUsers()
        self.getUser(2, ('Favorited',))
        
    # Prints all user data
    def getAllUsers(self):
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT Userid, Page_Exists, Username, Joined, Last_Active, Image_Time, Birthday, Gender, Location, Website, Twitter, Facebook, Bio, Follows, Ratings, Reviews, Comments, Fictions, Total_Words, Total_Reviews_Received, Total_Ratings_Received, Followers, Favorites, Favorited FROM users')
                rows = cur.fetchall()
                for row in rows:
                    print(row)
        except sqlite3.OperationalError as e:
            print(e)

    # Returns the information of a user based on a tuple of requested keys
    def getUser(self, userid, keys):
        try:
            search = " Userid"
            for key in keys:
                search += ', ' + key
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT' + search + ' FROM users WHERE Userid=?', (userid,))
                rows = cur.fetchone()
                print(rows)
        except sqlite3.OperationalError as e:
            print(e)

if __name__ == '__main__':
    readDatabase()