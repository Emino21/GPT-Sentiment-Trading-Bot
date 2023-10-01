import os
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np

# Initialize DataFrame for all data
final_dataframe = pd.DataFrame()

# Stock Pricing Path
stocks_path = './IVV_Constitutents_Price_Data_Dec_2022'

for stock in os.listdir(stocks_path):
    if stock.endswith(".csv"):
        #  Full file path
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

# Calculate mean adjusted close price for each day
mean_adj_close = final_dataframe.mean(axis=1)

# Portofolio Value = 10.000
initial_portfolio_value = 10000

# Number of Stocks
num_stocks = len(final_dataframe.columns)

# Investment per stock
initial_investment_per_stock = initial_portfolio_value / num_stocks

# Calculate portfolio value
portfolio_value = mean_adj_close * num_stocks * initial_investment_per_stock / mean_adj_close.iloc[0]

# Plot
plt.figure(figsize=(14, 7))
plt.plot(portfolio_value, label='Portfolio Value Over Time')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value in $')
plt.legend()
plt.grid(True)
# mplcursors.cursor(hover=True)
plt.show()

# Total Returns
total_return = (portfolio_value[-1] - initial_portfolio_value) / initial_portfolio_value * 100
print(f"Total Return: {total_return:.2f}%")

# Data span (in years)
start_date = pd.Timestamp('2022-03-01')
end_date = pd.Timestamp('2023-07-28')
years = (end_date - start_date).days / 365.25

# Annualized Returns
annualized_return = (portfolio_value[-1] / initial_portfolio_value) ** (1 / years) - 1
annualized_return *= 100
print(f"Annualized Return: {annualized_return:.2f}%")

# Max Drawdown
running_max = np.maximum.accumulate(portfolio_value)
running_drawdown = (portfolio_value - running_max) / running_max
max_drawdown = np.min(running_drawdown) * 100
print(f"Max Drawdown: {max_drawdown:.2f}%")

# Sharpe Ratio
daily_returns = portfolio_value.pct_change().dropna()
risk_free_rate = 0.0089
annualized_return_decimal = annualized_return / 100
sharpe_ratio = (annualized_return_decimal - risk_free_rate) / (daily_returns.std() * np.sqrt(252))
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")