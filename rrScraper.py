"""
Royal Road doesn't do any authentication so it's possible to scrape the data directly with a request. No funny stuff needed. 
"""
batchSize = 100 #The number of users put in one json file
batches = 1 #number of json files generated

# A list of all tags that are forcefully converted from str to int for storage in the json dumps
convertInt = ["Joined", "Last Active", "Follows", "Favorites", "Ratings", "Reviews", "Comments", "Fictions", "Total Words", "Total Reviews Received", "Total Ratings Received", "Followers"]


from scrapers import makeSoup
from bs4 import BeautifulSoup
import json
import sqlite3


class scrapeRRUser(): 
    # Initialize the library for the user in question
    def __init__(self, userID):
        self.user = dict({}) # dict to store all user data
        self._userID = userID # var for userID
        __rr = "https://www.royalroad.com/profile/" + str(userID) + "/" # HTTP path to royalroad profile of userID
        self._soupMain = makeSoup(__rr) # Main profile page
        self._soupFictions = makeSoup(__rr + "fictions") # Profile fictions page
        self._soupFavorites = makeSoup(__rr + "favorites") # Profile favorites page
        self.populate()
    
    # Verifies an existing profile
    def rrExistingPage(self): 
        # Part is the section we want to search through
        part = self._soupMain.find("div", class_="number font-red-sunglo") # The big 404 on page not found error page
        if (part == None):
            return True
        elif (part.text.strip() == "404"):
            print("404 error at " + str(self._userID))
            return False
        else:
            print("Something went wrong with the existing page detection.")

    # Method adds "Username" field to user
    def rrScrapeUsername(self):
        username = self._soupMain.find("div", class_="text-center username").text.strip()
        self.user["Username"] = username # Adds to user

    # Scrapes main user profile and returns a list of html soup with all the data
    def rrScrapeUserProfile(self): 
        part = self._soupMain.find_all("tr")
        for part in part:
            # Finds the key and value parts of the part scraped from main soup
            key = part.find("th").text.replace(":", "").strip()
            value = part.find("td").text.strip()
            if (value == ''):
                continue
            # Check if Field contains a time tag to replace Field with a unix int instead of a string
            elif (part.find("time") != None): 
                # Extract the int from the timeTag 
                timeTag = part.find("time")
                value = timeTag["unixtime"]
            
            # Compare dataHead with convertInt for match, if match, remove commas and make an int. Print error for debugging if something weird happens
            if (key in convertInt): # TODO make convertInt a proper file and load it at the start with something
                try:
                    self.user[key] = int(value.replace(",", "")) # Removes , and turns it to an int
                except: 
                    print("Something went wrong with the forceful int change.")
                    self.user[key] = value
            else:
                self.user[key] = value

    # Scrapes the favorites
    def rrScrapeUserFavorites(self): 
        # Creates an ordered list for fiction IDs
        favoriteList = []

        # Locates the cover image links to extract fiction IDs
        favorites = self._soupFavorites.find_all("img", class_="cover")

        for favorites in favorites:
            ficIDLong = str(favorites["id"])
            ficID = ficIDLong.split("-")[1]
            
            # Add ficID to favoriteList to be later added to user favorites. Force it to be an int. IT MUST BE INT AHHHHHHHHH
            try:
                favoriteList.append(int(ficID))
            except: 
                favoriteList.append(ficID)

        # Put it into user
        self.user ["FavoriteIDs"] = favoriteList

    def rrScrapeUserFictions(self):
        # Creates an ordered list for fiction IDs
        fictionsList = []

        # Locates cover image links to extract fiction IDs
        fictions = self._soupFictions.find_all("img", class_="cover")

        for fictions in fictions:
            ficIDLong = str(fictions["id"])
            ficID = ficIDLong.split("-")[1]
            
            # Add ficID to fictionsList to be later added to user fictions. Force it to be an int. IT MUST BE INT AHHHHHHHHH
            try:
                fictionsList.append(int(ficID))
            except: 
                fictionsList.append(ficID)

        # Put it into user
        self.user ["FictionsIDs"] = fictionsList

    # Initatees all the other methods to do the stuff
    def populate(self): 
        retrieve = self.rrExistingPage()
        if (retrieve == True):
            self.user ["Page Exists"] = True
            self.rrScrapeUsername()
            self.rrScrapeUserProfile()
            self.rrScrapeUserFictions()
            self.rrScrapeUserFavorites()
        elif (retrieve == False):
            print("UserID " + str(self._userID) + " could not be found.")
            self.user ["Page Exists"] = False
            print(self.user)
        else:
            print("Existing account error")

class rrBatchDump(scrapeRRUser):
    # Initialize the dump
    def __init__(self, size, batch):
        self._dump = dict({})
        self._batch = batch
        self._size = size
        self.populate()

    # Produces the dump json
    def getDumpJson(self): 
        path = "Output/rr" + str(self._batch) + ".json" # Path for the dump
        open(path, "w"). write(json.dumps(self._dump, indent=4)) # Overwrites whatever is here
        print("Dump " + str(self._batch) + " produced in " + path) # Says the dump was produced

    # Scrapes the batch defined in init
    def populate(self): 
        # Bounds of the batch
        start = self._size*self._batch + 1
        end = self._size*(self._batch+1) + 1
        for userID in range(start, end):
            try:
                u = scrapeRRUser(userID) # Instantiate a scrape of an RR user
                self._dump[userID] = u.user
            except:
                print("Error in batch " + str(self._batch) + " of user " + str(userID))

class rrSQLite():
    # Initialize the database # tag represents favorite, author, or review
    def __init__(self): 
        sql_statements = [
            """CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY, 
            page_exists INT, 
            username TEXT, 
            joined INT, 
            last_active INT, 
            image_time INT, 
            birthday INT, 
            gender TEXT, 
            location TEXT, 
            website TEXT, 
            twitter TEXT, 
            facebook TEXT, 
            bio varchar(3000), 
            follows INT, 
            favorites INT, 
            ratings INT, 
            reviews INT, 
            comments INT, 
            fictions INT, 
            total_words INT, 
            author_total_reviews_received INT, 
            author_total_ratings_recived INT, 
            author_followers INT, 
            author_favorites INT
            );""",  
            """CREATE TABLE IF NOT EXISTS relations (
            userid INT,
            fictionid INT, 
            relation TEXT,
            PRIMARY KEY (userid, fictionid), 
            FOREIGN KEY (userid) REFERENCES users (userid)
            FOREIGN KEY (fictionid) REFERENCES fictions (fictionid)
            );""", 
            """CREATE TABLE IF NOT EXISTS fictions (
            fictionid INT PRIMARY KEY 
            );"""
        ]

        try:
            with sqlite3.connect("Output/royalroad.db") as conn: # connects to the local database
                cursor = conn.cursor()
                for statement in sql_statements:
                    cursor.execute(statement)
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
    
    # Add user to user table
    def addUser(self, userid, page_exists, conn):
        # Table insert
        sql = '''INSERT INTO users(userid, page_exists) VALUES(?, ?)'''
        user = (userid, page_exists)
        cur = conn.cursor()
        cur.execute(sql, user)
        conn.commit()
        
    # Modify user data
    def updateUser(self, key, value, userid, conn):
        # Table update
        sql = '''UPDATE users SET ?=? WHERE userid = ?'''
        cur = conn.cursor()
        cur.execute(sql, (key, value, userid))
        conn.commit()

    # Add fiction to fiction table
    def addFiction(self, fictionid, conn):
        # Table insert
        sql = '''INSERT INTO fictions(fictionid) VALUES(?)'''
        cur = conn.cursor()
        cur.execute(sql, (fictionid))
        conn.commit()

    # Add relation to relation table
    def addRelation(self, userid, fictionid, relation, conn): 
        # Table insert
        sql = '''INSERT INTO relations(userid, fictionid, relation) VALUES(?, ?, ?)'''  
        cur = conn.cursor()
        cur.execute(sql, (userid, fictionid, relation))
        conn.commit()

    # Takes a dict and adds it to all the SQL stuff
    def dictCovert(self, user_dict, userid): 
        try:
            """
            username TEXT, 
            joined INT, 
            last_active INT, 
            image_time INT, 
            birthday INT, 
            gender TEXT, 
            location TEXT, 
            website TEXT, 
            twitter TEXT, 
            facebook TEXT, 
            bio varchar(3000), 
            follows INT, 
            favorites INT, 
            ratings INT, 
            reviews INT, 
            comments INT, 
            fictions INT, 
            total_words INT, 
            author_total_reviews_received INT, 
            author_total_ratings_recived INT, 
            author_followers INT, 
            author_favorites INT"""
        except sqlite3.OperationalError as e:
            print(e)


if __name__ == '__main__':
    # Initializes the rr.json files, opens them up, and then puts the batches in them
    db = rrSQLite()
    for i in range(0,batches):
        b = rrBatchDump(batchSize, i)
        b.getDumpJson()
    print("Image complete.")