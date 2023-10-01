import os
import pandas as pd

# Path to data files
ivv_dir = './IVV_Constitutents_Price_Data_Dec_2022'

# Initializing a list to store results
wrong_files  = []

for file in os.listdir(ivv_dir):
    # Checking for regular file and file is csv
    if os.path.isfile(os.path.join(ivv_dir, file)) and file.endswith('.csv'):
        # Reading file
        df = pd.read_csv(os.path.join(ivv_dir, file))
        
        # Checking the start date
        start_date = pd.to_datetime(df['Date'].iloc[0])
        if start_date != pd.to_datetime('2022-03-01'):
            wrong_files.append(f"{file} (Start date: {start_date})")
        
        # Checking the end date
        end_date = pd.to_datetime(df['Date'].iloc[-1])
        if end_date != pd.to_datetime('2023-07-31'):
            wrong_files.append(f"{file} (End date: {end_date})")

print(wrong_files)