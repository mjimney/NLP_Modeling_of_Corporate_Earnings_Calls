import requests
import pickle
import time
from bs4 import BeautifulSoup

pages = 530

urls = {}

for t in range(1,pages):
    # Loads each page of urls (about 20 links per page)
    url = 'https://www.fool.com/earnings-call-transcripts/?page={}'.format(t)
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page)

    # Records each url present on the page (about 20)
    for i,j in enumerate(soup.find_all('h4')):
        urls['{}.{}'.format(t,i)] = 'https://www.fool.com' + j.find('a')['href']
        time.sleep(4)

with open('../pickle_data/all_urls.pkl', 'wb') as picklefile:
    pickle.dump(urls, picklefile)
