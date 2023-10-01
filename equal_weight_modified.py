import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Initialize DataFrame for all data
final_dataframe = pd.DataFrame()

# Stock Pricing Path
stocks_path = './IVV_Constitutents_Price_Data_Dec_2022'

for stock in os.listdir(stocks_path):
    if stock.endswith(".csv"):
        # Full file path
        final_path = os.path.join(stocks_path, stock)
        
        # Load stock data
        price_data = pd.read_csv(final_path, index_col=0, parse_dates=True)
        
        # Rename 'Adj Close' to the ticker symbol
        price_data = price_data[['Adj Close']].rename(columns={'Adj Close': stock[:-4]})
        
        # Insert in all_data DataFrame
        if final_dataframe.empty:
            final_dataframe = price_data
        else:
            final_dataframe = final_dataframe.join(price_data, how='outer')

# Load sentiments
sentiment_data = pd.read_csv('Sentiments.csv', parse_dates=['date'])
sentiment_data.set_index('date', inplace=True)

# Calculate quarterly average sentiment scores
quarterly_sentiments = sentiment_data.groupby([sentiment_data.index.to_period("Q"), 'ticker'])['sentiment score'].mean().unstack()

# Replace NaN values in the quarterly sentiments with 0
quarterly_sentiments.fillna(0, inplace=True)

# Calculate equal weight
num_stocks = len(final_dataframe.columns)
equal_weights = pd.Series(1.0/num_stocks, index=quarterly_sentiments.columns)

# List for portfolio values each day
portfolio_values_adjusted = []

# Portfolio distribution
portfolio_distribution_adjusted = equal_weights

for idx, row in final_dataframe.iterrows():
    # Calculate portfolio value for the day
    day_value = (row * portfolio_distribution_adjusted).sum()
    portfolio_values_adjusted.append(day_value)

    # Check if day is the last day of a quarter
    if idx.is_quarter_end:
        # Fetch sentiment data for the quarter
        quarter = idx.to_period("Q")

        # For the first quarter, we don't adjust weights based on sentiment
        if quarter == '2022Q1':
            continue

        if quarter in quarterly_sentiments.index:
            stock_sentiments = quarterly_sentiments.loc[quarter]
            
            # Adjust weights using the sentiment scores directly
            final_weights_adjusted = equal_weights + stock_sentiments
            final_weights_adjusted /= final_weights_adjusted.sum()

            # Update portfolio distribution based on new weights
            portfolio_distribution_adjusted = final_weights_adjusted

# Convert portfolio_values_adjusted to a pandas Series for further analysis
portfolio_value_adjusted = pd.Series(portfolio_values_adjusted, index=final_dataframe.index)
portfolio_value_adjusted *= 10000 / portfolio_value_adjusted[0]

print(portfolio_value_adjusted)
# Plot
plt.figure(figsize=(14, 7))
plt.plot(portfolio_value_adjusted, label='Adjusted Portfolio Value Over Time')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value in $')
plt.legend()
plt.grid(True)
plt.show()

# Total Returns
total_return_adjusted = (portfolio_value_adjusted[-1] - portfolio_value_adjusted[0]) / portfolio_value_adjusted[0] * 100
print(f"Adjusted Total Return: {total_return_adjusted:.2f}%")

# Data span (in years)
start_date = pd.Timestamp('2022-03-01')
end_date = pd.Timestamp('2023-07-28')
years = (end_date - start_date).days / 365.25

# Annualized Returns
annualized_return_adjusted = ((portfolio_value_adjusted[-1] / portfolio_value_adjusted[0]) ** (1 / years) - 1) * 100
print(f"Adjusted Annualized Return: {annualized_return_adjusted:.2f}%")

# Max Drawdown
running_max = np.maximum.accumulate(portfolio_value_adjusted)
running_drawdown = (portfolio_value_adjusted - running_max) / running_max
max_drawdown_adjusted = np.min(running_drawdown) * 100
print(f"Adjusted Max Drawdown: {max_drawdown_adjusted:.2f}%")

# Sharpe Ratio
daily_returns_adjusted = portfolio_value_adjusted.pct_change().dropna()
risk_free_rate = 0.0089
annualized_return_decimal_adjusted = annualized_return_adjusted / 100
sharpe_ratio_adjusted = (annualized_return_decimal_adjusted - risk_free_rate) / (daily_returns_adjusted.std() * np.sqrt(252))
print(f"Adjusted Sharpe Ratio: {sharpe_ratio_adjusted:.2f}")