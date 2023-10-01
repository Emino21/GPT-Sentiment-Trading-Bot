import yfinance as yf
import os
from get_stocks import get_ivv_stocks

# Get list of tickers
tickers = get_ivv_stocks('IVV_holdings_Dec_2022.csv')

output_path = './IVV_Constitutents_Price_Data_Dec_2022'

# Download pricing data for each ticker
for ticker in tickers:
    cur_ticker = yf.download(ticker, start='2022-03-01', end='2023-07-31')
    cur_ticker.to_csv(os.path.join(output_path, f"{ticker}.csv"))