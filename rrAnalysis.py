"""
This file interacts with Output/royalroad.db to analyze the data in there for relational data
"""

db_path = "Output/royalroad.db"

import sqlite3


# Prints out all the contents in the database
class readDatabase():
    def __init__(self):
        self.getAllUsers()
        
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
    
    # Returns the information of a user
    def getUser(self, userid):
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT Userid, Page_Exists, Username FROM users')
        except sqlite3.OperationalError as e:
            print(e)

if __name__ == '__main__':
    readDatabase()