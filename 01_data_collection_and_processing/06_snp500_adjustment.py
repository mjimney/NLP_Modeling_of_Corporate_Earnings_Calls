import pickle
import datetime as dt
import pandas as pd
import numpy as np

snp_history_file = './supplemental_data/SNP.csv'

with open('pickle_data/prices.pkl', 'rb') as picklefile: 
    df = pickle.load(picklefile)

with open('pickle_data/ticker_betas.pkl', 'rb') as picklefile: 
    ticker_betas = pickle.load(picklefile)

def bench_t1(row,bench_df=snp_df):
    call_flag = row['time_tag']
    if call_flag == 'mid_day':
        b_p0 = bench_df[bench_df['Date'] == row['t0']]['Open'].values[0]
        b_p1 = bench_df[bench_df['Date'] == row['t1']]['Close'].values[0]
    else:
        b_p0 = bench_df[bench_df['Date'] == row['t0']]['Close'].values[0]
        b_p1 = bench_df[bench_df['Date'] == row['t1']]['Close'].values[0]
    row['b_p0'] = b_p0
    row['b_p1'] = b_p1
    return row

def bench_t2(row,bench_df=snp_df):
    try:
        b_p2 = bench_df[bench_df['Date'] == row['t2']]['Close'].values[0]
    except:
        b_p2 = np.NaN
    row['b_p2'] = b_p2
    return row

snp_df = pd.read_csv(snp_history_file,parse_dates=['Date'])

# Calculate S&P return during same return period
df = df.apply(bench_t1,axis=1)
df = df.apply(bench_t2,axis=1)
df['bench_p1_delta'] = (df['b_p1'] / df['b_p0'] - 1) * 100
df['bench_p2_delta'] = (df['b_p2'] / df['b_p1'] - 1) * 100
df = df.drop(columns=['b_p0','b_p1','b_p2'])

# Adjust benchmark returns to account for 3 month company beta
df['beta'] = df['call_id'].transform(lambda x: ticker_betas[x])
df.drop([7961,1056],inplace=True) #remove errors with these rows
df['bench_p1_delta_adj'] = df['bench_p1_delta'] * df['beta']
df['bench_p2_delta_adj'] = df['bench_p2_delta'] * df['beta']

with open('pickle_data/prices_adj.pkl', 'wb') as picklefile:
    pickle.dump(df, picklefile)