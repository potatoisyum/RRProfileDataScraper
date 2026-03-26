import requests
from bs4 import BeautifulSoup

# Scrapes a page and spits out the soup without any authentication
def makeSoup(URL):
    # Takes URL and requests it very simply
    page = requests.get(URL)
    return BeautifulSoup(page.content,"html.parser")
