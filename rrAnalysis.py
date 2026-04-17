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
        action = str(input("Action (user/fiction/relation):")) #TODO add fiction to this list which lists fictions rating from reviews that are logged and all of the reviews/favorited users attributed to them
        if action == "user":
            target = int(input("userID:"))
            print(self.makeDict(target))
        if action == "fiction":
            print(self.getAllRelations())
        if action == "relation":
            target = int(input("fictionID:"))
            relations = self.getFictionRelation(target)

        
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

    # Prints all relation data
    def getAllRelations(self):
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT Userid, Fictionid, Relation, Overall, Style, Story, Grammar, Character, Content FROM relations')
                rows = cur.fetchall()
                for row in rows:
                    print(row)
        except sqlite3.OperationalError as e:
            print(e)

    # Returns the information of a user based on a list of requested keys
    def getUser(self, userid: int, keys: list):
        try:
            # Loops through the key list to format the sql
            search = ''
            for key in keys:
                search += key + ','
            search = search[:len(search)-1]
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT ' + search + ' FROM users WHERE Userid=?', (userid,))
                rows = cur.fetchone()
                return(rows)
        except sqlite3.OperationalError as e:
            print(e)
    
    # Returns the relational data in a tuple given a Userid
    def getUserRelation(self, userid: int):
        try:
            with sqlite3.connect(db_path) as conn:
                # Pulls the row
                cur = conn.cursor()
                cur.execute('SELECT Userid, Fictionid, Relation, Overall, Style, Story, Grammar, Character, Content FROM relations WHERE Userid=?', (userid,))
                rows = cur.fetchall()
                return(rows)
        except sqlite3.OperationalError as e:
            print(e)

    # Returns the entries that refer to a fiction
    def getFictionRelation(self, fictionid:int):
        try:
            with sqlite3.connect(db_path) as conn:
                # Pulls the row
                cur = conn.cursor()
                cur.execute('SELECT Userid, Fictionid, Relation, Overall, Style, Story, Grammar, Character, Content FROM relations WHERE Fictionid=?', (fictionid,))
                rows = cur.fetchall()
                return(rows)
        except sqlite3.OperationalError as e:
            print(e)


    # Dict reconstructor given a userID. Returns dict
    def makeDict(self, userid: int):
        _attributes = ['Userid', 'Page_Exists', 'Username', 'Joined', 'Last_Active', 'Image_Time', 'Birthday', 'Gender', 'Location', 'Website', 'Twitter', 'Facebook', 'Bio', 'Follows', 'Ratings', 'Reviews', 'Comments', 'Fictions', 'Total_Words', 'Total_Reviews_Received', 'Total_Ratings_Received', 'Followers', 'Favorites', 'Favorited']
        information = self.getUser(userid, _attributes)
        user = dict({})
        # Loops through everything to assign to the dict in the same order as requested from the database
        for i in range(0,len(_attributes)):
            # Skip the null information to make it cleaner
            if information[i] == None:
                pass
            else:
                user[_attributes[i]] = information[i]
        fictions = []
        favorites = []
        reviews = {}
        userRelations = self.getUserRelation(userid)
        for fiction in userRelations:
            if fiction[2] == "Fiction":
                fictions.append(fiction[1])
            elif fiction[2] == "Favorite":
                favorites.append(fiction[1])
            elif fiction[2] == "Review":
                for data in range(0, 9):
                    review = {}
                    if data == 0: # Userid
                        pass
                    if data == 1: # Fictionid
                        pass
                    reviewstructure = ['Userid', 'Fictionid', 'Relation', 'Overall', 'Style', 'Story', 'Grammar', 'Character', 'Content']
                    review[reviewstructure[data]] = fiction[data]
                reviews[fiction[1]] = review
        user ["FictionIDs"] = fictions
        user ["FavoriteIDs"] = favorites
        user ["Reviews"] = reviews

        return user


if __name__ == '__main__':
    readDatabase()