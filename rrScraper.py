"""
Royal Road doesn't do any authentication so it's possible to scrape the data directly with a request. No funny stuff needed. 
"""
batchSize = 10 #The number of users put in one json file
batches = 1 #number of json files generated

# A list of all tags that are forcefully converted from str to int for storage in the json dumps
convertInt = ["Joined", "Last Active", "Follows", "Favorites", "Ratings", "Reviews", "Comments", "Fictions", "Total Words", "Total Reviews Received", "Total Ratings Received", "Followers"]
db_path = "Output/royalroad.db"

from scrapers import makeSoup
from bs4 import BeautifulSoup
import time
import sqlite3


class scrapeRRUser(): 
    # Initialize the library for the user in question
    def __init__(self, userID):
        self.user = dict({}) # dict to store all user data
        self._userID = userID # var for userID
        self._rr = "https://www.royalroad.com/profile/" + str(userID) + "/" # HTTP path to royalroad profile of userID
        self._soupMain = makeSoup(self._rr) # Main profile page TODO make a seperate script with a timer that queues HTTP requests
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
            if (key in convertInt): # TODO make convertInt a proper file and load it at the start with something # TODO Currently loses user favorites because favorites is both the tag for author and reader. Currently ignoring user favorites and letting it override. Probably a bad idea. 
                try:
                    self.user[key.replace(" ", "_")] = int(value.replace(",", "")) # Removes , and turns it to an int
                except: 
                    print("Something went wrong with the forceful int change.")
                    self.user[key] = value
            else:
                self.user[key] = value

    # Scrapes the favorites
    def rrScrapeUserFavorites(self): 
        # Creates an ordered list for fiction IDs
        favoriteList = []
        # Goes through all the favorite pages to actually find all the favorites
        i = 1 # Page counter
        while True: 
            # Locates the cover image links to extract fiction IDs
            _soupFavorites = makeSoup(self._rr + "favorites?page=" + str(i)) # Profile favorites page
            favorites = _soupFavorites.find_all("img", class_="cover")
            if favorites == []:
                break
            for favorites in favorites:
                ficIDLong = str(favorites["id"])
                ficID = ficIDLong.split("-")[1]
                # Add ficID to favoriteList to be later added to user favorites. Force it to be an int. IT MUST BE INT AHHHHHHHHH
                try:
                    favoriteList.append(int(ficID))
                except: 
                    favoriteList.append(ficID)
            if(i>255):
                print("Over 255 pages of favorites for user " + str(self._userID))
                break
            i+=1 # Increase page counter
        
        # Put it into user
        self.user ["Favorited"] = len(favoriteList)
        self.user ["FavoriteIDs"] = favoriteList

    # Scrapes the fictions
    def rrScrapeUserFictions(self):
        # Creates an ordered list for fiction IDs TODO Potentially use threading to scrape at the same time in a different class
        fictionsList = []
        i = 1 # Page counter
        while True:
            # Locates cover image links to extract fiction IDs
            self._soupFictions = makeSoup(self._rr + "fictions?page=" + str(i)) # Profile fictions page
            fictions = self._soupFictions.find_all("img", class_="cover")
            if fictions == []:
                break
            for fictions in fictions:
                ficIDLong = str(fictions["id"])
                ficID = ficIDLong.split("-")[1]
                
                # Add ficID to fictionsList to be later added to user fictions. Force it to be an int. IT MUST BE INT AHHHHHHHHH
                try:
                    fictionsList.append(int(ficID))
                except: 
                    fictionsList.append(ficID)
            if(i>255):
                print("Over 255 pages of fictions for user" + str(self._userID))
                break
            i+=1 # Increase page counter

        # Put it into user
        self.user ["FictionsIDs"] = fictionsList

    # Scrapes the reviews and ratings and stores them as tuples 
    def rrScrapeUserReviews(self):
        # Creates an ordered list for fiction IDs TODO Potentially use threading to scrape at the same time in a different class
        reviewList = {}
        i = 1 # Page counter
        while True:
            # Locates cover image links to extract fiction IDs
            self._soupFictions = makeSoup(self._rr + "reviews?page=" + str(i)) # Profile fictions page
            reviewsContent = self._soupFictions.find_all("div", class_="row review")
            reviewsRating = self._soupFictions.find_all("div", class_="row hidden-xs visible-sm visible-md visible-lg")
            if reviewsContent == []:
                break
            for j in range(0,len(reviewsContent)):
                review = {}
                review ["Content"] = reviewsContent[j].find("div", class_="review-content").text
                ratings = reviewsRating[j].find_all("div", tabindex="-1")
                for rating in ratings:
                    rating = str(rating["aria-label"]).replace(" score: ", " ").replace(" out of ", " ").split(" ")
                    review [rating[0]] = float(rating[1])
                # Add to review list
                reviewList[str(reviewsContent[j].find("div", class_="review-content")["id"]).split("-")[2]] = review
            if(i>255):
                print("Over 255 pages of reviews for user" + str(self._userID))
                break
            i+=1 # Increase page counter
        
        print(reviewList)

        # Put it into user
        # self.user ["FictionsIDs"] = fictionsList

    # Initatees all the other methods to do the stuff
    def populate(self): 
        retrieve = self.rrExistingPage()
        if (retrieve == True):
            self.user ["Page_Exists"] = True
            self.rrScrapeUsername()
            self.rrScrapeUserProfile()
            self.rrScrapeUserFictions()
            self.rrScrapeUserFavorites()
            self.rrScrapeUserReviews()
        elif (retrieve == False):
            print("UserID " + str(self._userID) + " could not be found.")
            self.user ["Page_Exists"] = False
        else:
            print("Existing account error")
        self.user ["Image_Time"] = round(time.time())

class rrSQLite():
    # Initialize the database # tag represents favorite, author, or review
    def __init__(self): 
        sql_statements = [
            """CREATE TABLE IF NOT EXISTS users (
            Userid INTEGER PRIMARY KEY, 
            Page_Exists INT, 
            Username TEXT, 
            Joined INT, 
            Last_Active INT, 
            Image_Time INT, 
            Birthday INT, 
            Gender TEXT, 
            Location TEXT, 
            Website TEXT, 
            Twitter TEXT, 
            Facebook TEXT, 
            Bio varchar(3000), 
            Follows INT, 
            Ratings INT, 
            Reviews INT, 
            Comments INT, 
            Fictions INT, 
            Total_Words INT, 
            Total_Reviews_Received INT, 
            Total_Ratings_Received INT, 
            Followers INT, 
            Favorites INT, 
            Favorited INT
            );""",  
            """CREATE TABLE IF NOT EXISTS relations (
            Userid INT,
            Fictionid INT, 
            Relation TEXT,
            Overall double,
            Style double, 
            Story double, 
            Grammar double, 
            Character double,
            Content TEXT,
            PRIMARY KEY (Userid, Fictionid), 
            FOREIGN KEY (Userid) REFERENCES users (Userid)
            FOREIGN KEY (Fictionid) REFERENCES fictions (Fictionid)
            );""", 
            """CREATE TABLE IF NOT EXISTS fictions (
            Fictionid INT PRIMARY KEY 
            );"""
        ]

        try:
            with sqlite3.connect(db_path) as conn: # connects to the local database
                cursor = conn.cursor()
                for statement in sql_statements:
                    cursor.execute(statement)
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
    
    # Add user to user table
    def addUser(self, userid, page_exists, conn):
        # Table insert
        sql = '''INSERT OR IGNORE INTO users(Userid, Page_Exists) VALUES(?, ?)'''
        user = (userid, page_exists)
        cur = conn.cursor()
        cur.execute(sql, user)
        conn.commit()
        
    # Modify user data
    def updateUser(self, key, value, userid, conn):
        # Table update
        sql = "UPDATE users SET " + key + "=? WHERE Userid = ?"
        cur = conn.cursor()
        cur.execute(sql, (value, userid))
        conn.commit()

    # Add fiction to fiction table
    def addFiction(self, fictionid, conn):
        # Table insert
        sql = '''INSERT OR IGNORE INTO fictions(fictionid) VALUES(?)'''
        cur = conn.cursor()
        cur.execute(sql, (fictionid,))
        conn.commit()

    # Add relation to relation table
    def addRelation(self, userid, fictionid, relation, review, conn): 
        # Table insert
        sql = '''INSERT OR IGNORE INTO relations(Userid, fictionid, Relation) VALUES(?, ?, ?)'''  
        cur = conn.cursor()
        cur.execute(sql, (userid, fictionid, relation))
        # , review["Overall"], review["Style"], review["Story"], review["Grammar"], review["Character"], review["Content"])
        conn.commit()

    # Modify relation data
    def updateRelation(self, userid, fictionid, key, value, conn):
        # Table insert
        sql = "UPDATE relations SET " + key + "=? WHERE (Userid,Fictionid) = (?)"
        cur = conn.cursor()
        cur.execute(sql, (value, (userid,fictionid)))
        conn.commit()

    # Takes a dict and adds it to all the SQL stuff
    def dictCovert(self, user_dict, userid): 
        try:
            with sqlite3.connect(db_path) as conn:
                # Adds the user if they aren't in and also puts in if the page exists or not
                page_exists = user_dict ["Page_Exists"]
                image = user_dict ["Image_Time"]
                del user_dict ["Page_Exists"] 
                del user_dict ["Image_Time"]
                self.addUser(userid, page_exists, conn)
                self.addUser(userid, image, conn)
                if page_exists == True:
                    for key in user_dict.keys():
                        if key == "FictionsIDs":
                            for fictionid in user_dict[key]:
                                self.addFiction(fictionid, conn)
                                self.addRelation(userid, fictionid, "Fiction", None, conn)
                        elif key == "FavoriteIDs":
                            for fictionid in user_dict[key]:
                                self.addFiction(fictionid, conn)
                                self.addRelation(userid, fictionid, "Favorite", None, conn)
                        elif key == "ReviewIDs":
                            for fictionid in user_dict[key].keys():
                                self.addFiction(fictionid, conn)
                                self.addRelation(userid, fictionid, "Review", conn)
                                for reviewkeys in user_dict[key][fictionid].keys():
                                    self.updateRelation(userid, fictionid, reviewkeys, user_dict[key][fictionid][reviewkeys], conn)
                        else:
                            self.updateUser(key, user_dict[key], userid, conn)

        except sqlite3.OperationalError as e:
            print(e)


if __name__ == '__main__':
    # Initializes the rr.json files, opens them up, and then puts the batches in them
    db = rrSQLite()
    for i in range(0,batchSize):
        rruser = scrapeRRUser(i)
        db.dictCovert(rruser.user, i)
    print("In database.")