import requests
import re
import pickle
import time
from bs4 import BeautifulSoup

with open('../pickle_data/all_tickers.pkl', 'rb') as picklefile: 
    all_tickers = pickle.load(picklefile)

def get_beta(ticker):
    try:
        summary_path = 'https://finance.yahoo.com/quote/{0}?p={0}'.format(ticker)
        response = requests.get(summary_path)
        page = response.text
        soup = BeautifulSoup(page)
        beta = float(soup.find('td', attrs={'data-test': 'BETA_3Y-value'}).text)
        return beta
    except:
        return 1

ticker_betas = {}
for i,j in all_tickers.items():
    print (i)
    ticker_betas[i] = get_beta(j)
    time.sleep(3)
print ('Complete')

with open('../pickle_data/ticker_betas.pkl', 'wb') as picklefile:
    pickle.dump(ticker_betas, picklefile)
