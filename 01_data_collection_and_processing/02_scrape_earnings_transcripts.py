import requests
import re
import pickle
import time
from bs4 import BeautifulSoup

with open('../pickle_data/all_urls.pkl', 'rb') as picklefile: 
    urls = pickle.load(picklefile)

all_ids = list(urls.keys())

all_pages = {}

for i in all_ids:
    url = urls[i]
    response = requests.get(url)
    page = response.text
    all_pages[i] = page
    print (i,' complete')
    time.sleep(3)

with open('../pickle_data/all_pages.pkl', 'wb') as picklefile:
    pickle.dump(all_pages, picklefile)