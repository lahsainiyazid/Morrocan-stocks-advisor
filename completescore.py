import pandas as pd 
import cloudscraper 
from bs4 import BeautifulSoup 
urls=["https://www.investing.com/equities/itissalat-al-maghrib"]
scraper=cloudscraper.create_scraper()
response=scraper.get(url)
soup=BeautifulSoup(response.text,"html.parser")

