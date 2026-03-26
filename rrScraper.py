"""
Royal Road doesn't do any authentication so it's possible to scrape the data directly with a request. No funny stuff needed. 
"""
batchSize = 100 #The number of users put in one json file
batches = 1 #number of json files generated

# A list of all tags that are forcefully converted from str to int for storage in the json dumps
convertInt = ["Follows", "Favorites", "Ratings", "Reviews", "Comments", "Fictions", "Total Words", "Total Reviews Received", "Total Ratings Received", "Followers"]

from scrapers import makeSoup
from bs4 import BeautifulSoup
import json

# Checks the existence of a rooyal road page by looking for theh h3 404 line
def rrExistingPage(exists):
    # Make soup using simple soup maker
    soup = makeSoup("https://www.royalroad.com/" + str(exists))

    # Finds the big 404 letters on the 404 page
    status = soup.find("div", class_="number font-red-sunglo")
    
    # Checks if the 404 exists or not. If 404, returns a false for existing page. 
    if (status == None):
        return True
    elif (status.text.strip() == "404"):
        print("404 error at " + str(exists))
        return False
    else:
        print("Something went wrong with the existing page detection.")

# Scrapes main user profile given a userID assuming it exists
def scrapeUserProfile(userID, user):
    # Make soup using simple soup maker
    soup = makeSoup("https://www.royalroad.com/profile/" + str(userID))
    
    # tbody encloses the groups of 3 on profile page tr tags enclose each line (somehow very convinient) 
    stats = soup.find_all("tr")
    
    # An empty dict to store user data tied to the user's ID
    username = soup.find("div", class_="text-center username").text.strip()
    userData = {
        "username" : username
    }
    
    # Fill up the dict with the user data on the main profile page
    for stats in stats:
        # dataHead is the header to a stat and dataField is the text. Still can use stats to access the contents. 
        dataHead = stats.find("th").text.replace(":", "").strip()
        dataField = stats.find("td").text.strip()

        # Check if Field is empty and remove the entry to prevent bloating storage of empty fields
        if (dataField == ''):
            continue
        # Check if Field contains a time tag to replace Field with a unix int instead of a string
        elif (stats.find("time") != None): 
            # Extract the int from the timeTag 
            timeTag = stats.find("time")
            dataField = timeTag["unixtime"]
        
        # Compare dataHead with convertInt for match, if match, remove commas and make an int. Print error for debugging if something weird happens
        if (dataHead in convertInt):
            try:
                userData[dataHead] = int(dataField.replace(",", "")) # Removes , and turns it to an int
            except: 
                print("Something went wrong with the forceful int change.")
                userData[dataHead] = dataField
        
    
    user[userID] = userData
    return user
    print("User " + str(userID) + " added to user dict.")

# Scrapes user favorites given a userID given it exists
def scrapeUserFavorites(userID, user):
    # Make soup using simple soup maker
    soup = makeSoup("https://www.royalroad.com/profile/" + str(userID) + "/favorites")
    
    # Instantiate a set that will be added under the user dict of fictions
    favoritedFictions = []
    
    # Images in cover class
    favorites = soup.find_all("img", class_="cover")
    
    # Seperates out the fiction id from the image 
    for favorites in favorites:
        ficIDLong = str(favorites["id"])
        ficID = ficIDLong.split("-")[1]
        
        # Add ficID to favoritedFictions to be later added to user favorites. Force it to be an int. IT MUST BE INT AHHHHHHHHH
        try:
            favoritedFictions.append(int(ficID))
        except: 
            favoritedFictions.append(ficID)

    # Add favoritedFictions into user dict
    user[userID].update({"FavoriteIDs" : favoritedFictions})
    return user



# Function that scrapes data and checks if the user exists
def scrapeUser(userID, user):
    # Check for valid userID
    if (userID<=0):
        print("Invalid userID")

    # Check for existing user page (not 404)
    elif (rrExistingPage("profile/" + str(userID)) == False): 
        print(str(userID) + " Did not have an existing user profile.")

    else:
        # Goes and scrapes the data 
        user = scrapeUserProfile(userID, user)
        user = scrapeUserFavorites(userID, user)
    
    # Return the finished user dict for this batch
    return user

# A function that scrapes users and bunches it all up in a dict to create batches in case anything is interupted 
def batch(startUser, batchSize):
    user = {}
    for userID in range(startUser, startUser+batchSize-1): 
        user = scrapeUser(userID, user)
    # Returns the dict for it to be written to a file
    return user

if __name__ == '__main__':
    # Initializes the rr.json files, opens them up, and then puts the batches in them
    for i in range(0,batches):
        open("Output/rr" + str(i) + ".json", "w").write("")
        u = open("Output/rr" + str(i) + ".json", "a")
        batchStart = 1 + i * batchSize
        try: 
            u.write(json.dumps(batch(batchStart, batchSize), indent=4))
            print("Batch index " + str(i) + " complete.") # print out finished batches to represent the index of the batch
        except: 
            print("Batch index " + (i) + "encountered an error")
    print("Image complete.")