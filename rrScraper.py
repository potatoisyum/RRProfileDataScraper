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


class scrapeRRUser(): 
    # Initialize the library for the user in question
    def __init__(self, userID):
        self.user = dict({}) # dict to store all user data
        self._userID = userID # var for userID
        self._soupMain = makeSoup("https://www.royalroad.com/profile/" + str(userID))
        self._soupFavorites = makeSoup("https://www.royalroad.com/profile/" + str(userID) + "/favorites")
        self.populate()
    
    # Verifies an existing profile
    def rrExistingPage(self): 
        # Part is the section we want to search through
        part = self._soupMain.find("div", class_="number font-red-sunglo") # The big 404 on page not found error page
        if part == None:
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
        # Creates a non ordered list for fiction IDs
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

    # Initatees all the other methods to do the stuff
    def populate(self): 
        retrieve = self.rrExistingPage()
        if retrieve == True:
            self.rrScrapeUsername()
            self.rrScrapeUserProfile()
            self.rrScrapeUserFavorites()
        elif retrieve == False:
            print("UserID " + self._userID + " could not be found.")
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
        print("Dump " + str(self._batch) + " produced in " + path)

    # Scrapes the batch defined in init
    def populate(self): 
        # Bounds of the batch
        start = self._size*self._batch + 1
        end = self._size*(self._batch+1)
        for userID in range(start, end):
            u = scrapeRRUser(userID) # Instantiate a scrape of an RR user
            self._dump[userID] = u.user


if __name__ == '__main__':
    # Initializes the rr.json files, opens them up, and then puts the batches in them
    for i in range(0,batches):
        b = rrBatchDump(batchSize, i)
        b.getDumpJson()
    print("Image complete.")