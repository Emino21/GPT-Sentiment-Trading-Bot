import pandas as pd

# Read file
news_data = pd.read_csv('Alpha_Vantage_News_Data.csv', on_bad_lines='warn')

# Group 'date' and 'ticker' and select the first article
filtered_news = news_data.groupby(['date', 'ticker']).first().reset_index()

# Save CSV
filtered_news.to_csv('News_Data_Final.csv', index=False)