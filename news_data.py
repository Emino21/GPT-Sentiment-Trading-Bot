import requests
import pandas as pd
from get_stocks import get_dir_stocks
from datetime import timedelta
import time

# Parameters for request
api_key = "xxx"
tickers = get_dir_stocks()
limit = 1000
start_date = pd.to_datetime('2022-03-01')
end_date = pd.to_datetime('2023-07-31')

filename = "Alpha_Vantage_news_data.csv"

days_interval = 20

# Select date range
date_range = pd.date_range(start_date, end_date, freq=f'{days_interval}D')

# Convert dates into right format
for start, end in zip(date_range[:-1], date_range[1:]):
    time_from = start.strftime('%Y%m%dT%H%M')
    time_to = end.strftime('%Y%m%dT%H%M')

# Get requests for each ticker
    for ticker in tickers:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&time_from={time_from}&time_to={time_to}&limit={limit}&apikey={api_key}"
        response = requests.get(url)

        print(f"Status code for {ticker} on {start.date()} to {end.date()}: {response.status_code}")
        if response.status_code != 200:
            print(f"Error getting data for {ticker}, skipping...")
            continue

        data = response.json()

        # Only save right existing data in dataframe
        try:
            feed_data = data['feed']
        except KeyError:
            print(f"No feed data for {ticker} on {start.date()} to {end.date()}, skipping...")
            continue

        # Convert dates back
        for article in feed_data:
            article['time_published'] = pd.to_datetime(article['time_published'], format='%Y%m%dT%H%M%S').date()
            article['ticker'] = ticker

        df = pd.DataFrame(feed_data)

        if not df.empty:
            df = df[['time_published', 'ticker', 'title', 'summary', 'source']].rename(columns={'time_published': 'date'})

            # Save into CSV
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                df.to_csv(f, header=f.tell()==0, index=False)
                
        # Avoid rate limit
        time.sleep(2)
