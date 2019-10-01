import quandl
import pickle
import datetime as dt
import pandas as pd
import numpy as np

# Quandl API Key

api_key_file = 'quandl_api_key.txt'

def load_api_key(filename):
    ''' 
    Load the api key from a given filename.
    Expect the file to have a single line, containing the api key.
    '''
    try:
        with open(filename, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print('File not found: "%s"' % filename)

quandl.ApiConfig.api_key = load_api_key(api_key_file)

# Get Sectors

with open('pickle_data/all_tickers.pkl', 'rb') as picklefile: 
    all_tickers = pickle.load(picklefile)

unique_tickers = list(set(all_tickers.values()))

all_sectors = quandl.get_table('SHARADAR/TICKERS',
                               table='SEP',
                               ticker=unique_tickers,
                               qopts={'columns':['ticker','sector']})


# Get Dates and Prices

def check_time(row):
    if row.time() < dt.time(8, 30):
        # Call happens before open - check prev close to today close
        return 'before_open'
    elif row.time() < dt.time(16, 0):
        # Call happens during trading day - check today open to today close
        return 'mid_day'
    else:
        # Call happens after close - check today close to tomorrow close
        return 'after_close'

def call_quandl(ticker,t0,t1):
    return quandl.get_table('SHARADAR/SEP',
                            date={'gte':t0, 'lte':t1},
                            ticker=ticker,
                            qopts={"columns":['ticker','date','open','close']})
def find_price_t1(row):
    ticker = row['ticker']
    call_day = row['call_time'].date()
    call_flag = row['time_tag']
    try:
        if call_flag == 'before_open':
            t0 = call_day - dt.timedelta(days=1)
            if t0.weekday() > 4:  # check if weekend, if so, move to friday
                t0 -= dt.timedelta(days=t0.weekday()-4)
            t1 = call_day
            if t1.weekday() > 4:  # check if weekend, if so, move to monday
                t1 += dt.timedelta(days=7 - t1.weekday())
            px_df = call_quandl(ticker,t0,t1)
            p0 = px_df[px_df['date'] == t0]['close'].values[0]
            p1 = px_df[px_df['date'] == t1]['close'].values[0]

        elif call_flag == 'mid_day':
            t0 = call_day
            if t0.weekday() > 4:
                t0 -= dt.timedelta(days=t0.weekday()-4)
            t1 = t0
            px_df = call_quandl(ticker,t0,t1)
            p0 = px_df[px_df['date'] == t0]['open'].values[0]
            p1 = px_df[px_df['date'] == t1]['close'].values[0]

        elif call_flag == 'after_close':
            t0 = call_day
            if t0.weekday() > 4:
                t0 -= dt.timedelta(days=t0.weekday()-4)
            t1 = call_day + dt.timedelta(days=1)
            if t1.weekday() > 4:
                t1 += dt.timedelta(days=7 - t1.weekday())
            px_df = call_quandl(ticker,t0,t1)
            p0 = px_df[px_df['date'] == t0]['close'].values[0]
            p1 = px_df[px_df['date'] == t1]['close'].values[0]

        else:
            t0 = np.NaN
            t1 = np.NaN
            p0 = np.NaN
            p1 = np.NaN
    except:
        t0 = np.NaN
        t1 = np.NaN
        p0 = np.NaN
        p1 = np.NaN

    row['t0'] = t0
    row['t1'] = t1
    row['p0'] = p0
    row['p1'] = p1

    return row

def find_price_t2(row):
    ticker = row['ticker']
    call_day = row['t1']
    try:
        if dt.date.today() < (call_day + dt.timedelta(365/12)):
            t2 = np.NaN
            p2 = np.NaN
        else:
            t2 = call_day + dt.timedelta(365/12)
            if t2.weekday() > 4:  # check if weekend, if so, move to friday
                t2 += dt.timedelta(days=t2.weekday()-4) #double check this works, had as days=t0.weekay...
            px_df = call_quandl(ticker,t2,t2)
            p2 = px_df[px_df['date'] == t2]['close'].values[0]
    except:
        t2 = np.NaN
        p2 = np.NaN

    row['t2'] = t2
    row['p2'] = p2

    return row
    
with open('pickle_data/all_dates.pkl', 'rb') as picklefile: 
    all_dates = pickle.load(picklefile)

df = pd.DataFrame([all_tickers,all_dates]).transpose().reset_index()
df.columns = ['call_id','ticker','call_time']
df['call_time'] = pd.to_datetime(df['call_time'])
df = df.merge(all_sectors,on='ticker',how='left')
df['time_tag'] = df['call_time'].apply(check_time)
df.dropna(inplace=True)
df = df.apply(find_price_t1,axis=1)
df.dropna(inplace=True)
df = df.apply(find_price_t2,axis=1)
df['p1_delta'] = (df['p1'] / df['p0'] - 1) * 100
df['p2_delta'] = (df['p2'] / df['p1'] - 1) * 100


with open('pickle_data/prices.pkl', 'wb') as picklefile:
    pickle.dump(df, picklefile)
