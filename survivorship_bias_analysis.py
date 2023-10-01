import os
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from sklearn.metrics import mean_squared_error
import numpy as np

# Pricing data path
dir_path = './IVV_Constitutents_Price_Data_Dec_2022'

# Initializing DataFrame for the average weekly percentual changes
average_weekly_percentual_change = pd.DataFrame()

# Go through each CSV file
for file in os.listdir(dir_path):
    if file.endswith('.csv'):
        # Read CSV
        df = pd.read_csv(os.path.join(dir_path, file))
        
        # Convert to datetime type
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Daily percentual change in adjusted close price
        df['Daily Percentual Change'] = df['Adj Close'].pct_change() * 100
        
        # Resample to weekly data
        weekly_df = df.set_index('Date').resample('W').sum()
        
        # Append the weekly percentual change
        if average_weekly_percentual_change.empty:
            average_weekly_percentual_change['Date'] = weekly_df.index
        
        average_weekly_percentual_change[file[:-4]] = weekly_df['Daily Percentual Change'].values

# Drop the NaN values
average_weekly_percentual_change.dropna(inplace=True)

# Calculate the average weekly percentual change across all constituents
average_weekly_percentual_change['Average'] = average_weekly_percentual_change.iloc[:, 1:].mean(axis=1)

# Loading RSP Data and calculating daily percentual changes
rsp_data = pd.read_csv('RSP.csv')
rsp_data['Date'] = pd.to_datetime(rsp_data['Date'])
rsp_data['Daily Percentual Change'] = rsp_data['Adj Close'].pct_change() * 100

# Resample to weekly data
rsp_weekly_data = rsp_data.set_index('Date').resample('W').sum()

# Merge RSP data with average weekly percentual change DataFrame
merged_data = pd.merge(rsp_weekly_data.reset_index(), average_weekly_percentual_change, on='Date', how='inner')

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(merged_data['Date'], merged_data['Daily Percentual Change'], label='RSP', color='blue')
plt.plot(merged_data['Date'], merged_data['Average'], label='S&P 500 Constituents (Average)', color='red')
plt.title('Weekly Percentual Change in Adjusted Close Price from March 2022 to July 2023')
plt.xlabel('Date')
plt.ylabel('Weekly Percentual Change (%)')
plt.legend()
plt.grid(True)
# mplcursors.cursor(hover=True)
plt.show()

# Correlation coefficient
correlation_coefficient = np.corrcoef(merged_data['Daily Percentual Change'], merged_data['Average'])[0, 1]

# Mean squared error
mse = mean_squared_error(merged_data['Daily Percentual Change'], merged_data['Average'])

print(f"Correlation Coefficient = {correlation_coefficient}")
print(f"Mean Squared Error = {mse}") 