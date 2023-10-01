import pandas as pd
import os

# Get list of stocks from CSV file
def get_ivv_stocks(file):
    ivv_holdings = pd.read_csv(file)
    tickers = ivv_holdings['Ticker']
    return tickers

# Get stocks from directory which are CSV format in a list
def get_dir_stocks(directory):
    return [file.split('.')[0] for file in os.listdir(directory) if file.endswith(".csv")]