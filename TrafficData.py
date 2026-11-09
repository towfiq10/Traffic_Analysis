import pandas as pd
import numpy as np

# Setup random seed
np.random.seed(101)
n_rows = 500

# Step 1

timestamps = pd.date_range(start='2026-10-01', periods=n_rows, freq='h').astype(str)
legs = ['North Approach', 'South Approach', 'East Approach', 'West Approach', 'north', 'SOUTH', None, 'West']
movements = ['Left Turn', 'Right Turn', 'Through Turn', 'through', 'LEFT', None, 'Unknown']
crash_types = ['None', 'Rear-end', 'T-bone', 'Side-swipe', 'Pedestrian', 'none', 'REAR-END', None]
base_lat, base_lon = 47.6062, -122.3321

print(timestamps)
print(legs)
print(movements)
print(crash_types)
print(base_lat)
print(base_lon)

# Step 2
data = {
    'Timestamp': timestamps,
    'Approach_Leg': np.random.choice(legs, n_rows, p=[0.2, 0.2, 0.2, 0.15, 0.05, 0.05, 0.05, 0.1]),
    'Movement' : np.random.choice(movements, n_rows, p=[0.3, 0.3, 0.2, 0.05, 0.05, 0.05, 0.05]),
    'Traffic_Volume': np.random.poisson(lam=110, size=n_rows).astype(float),
    'Speed_Avg': np.random.normal(loc=35, scale=6, size=n_rows),
    'Latitude': base_lat + np.random.normal(loc=0, scale=0.0015, size=n_rows),
    'Longitude': base_lon + np.random.normal(loc=0, scale=0.0015, size=n_rows),    
    'Crash_Type': np.random.choice(crash_types, n_rows, p=[0.6, 0.1, 0.08, 0.05, 0.02, 0.05, 0.05, 0.05])
    #'Crash_Type': np.random.choice(crash_types, n_rows, p=[0.6, 0.1, 0.08, 0.05, 0.02, 0.05, 0.05, 0.05])
}
df = pd.DataFrame(data)
print(df)

# 3
# Inject missing values
df.loc[np.random.choice(df.index, 25), 'Traffic_Volume'] = np.nan
df.loc[np.random.choice(df.index, 25), 'Speed_Avg'] = np.nan

df.loc[np.random.choice(df.index, 5), 'Traffic_Volume'] = -999
df.loc[np.random.choice(df.index, 3), 'Traffic_Volume'] = 88888 # Outlier

df.loc[np.random.choice(df.index, 10), 'Latitude'] = 0.0
df.loc[np.random.choice(df.index, 10), 'Longitude'] = 0.0
print(df)

#4
# Save the csv file 
df.to_csv('messy_traffic_data.csv', index=False)
print("Messy dataset 'messy_traffic_data.csv' successfully created")

# PART 2: CLEANING & FEATURE ENGINEERING
# Step 1

print("--- STEP 2: CLEANING & FEATURE ENGINEERING ---")
# Reload the file to simulate starting fresh from a saved source
file_name = 'messy_traffic_data.csv'
df = pd.read_csv('messy_traffic_data.csv')
print(f"-> Loaded '{file_name}' into memory for cleaning...")
print(df)

# 2
# Handle Missing Values (Imputation)

df['Traffic_Volume'] = df['Traffic_Volume'].fillna(df['Traffic_Volume'].median())
df['Speed_Avg'] = df['Speed_Avg'].fillna(df['Speed_Avg'].mean())

# Fill missing categorical text with 'Unknown' or 'None'

df['Approach_Leg'] = df['Approach_Leg'].fillna('Unknown')
df['Movement'] = df['Movement'].fillna('None')
df['Crash_Type'] = df['Crash_Type'].fillna('None')

# 3. Filter Outliers & Erroneous Values
# Remove negative numbers, extreme
df = df[(df['Traffic_Volume'] >=0) & (df['Traffic_Volume'] <=5000)]
df = df[(df['Latitude'] !=0.0) & (df['Longitude'] != 0.0)]

print(df)

# 4
# Standardize Text Strings & Casing 

df['Approach_Leg'] = df['Approach_Leg'].astype(str).str.strip().str.title()
Leg_mapping = {
    'North': 'North Approach',
    'South': 'South Approach',
    'East': 'East Approach',
    'West': 'West Approach',
}

df['Approach_Leg'] = df['Approach_Leg'].replace(Leg_mapping)
df['Movement'] = df['Movement'].astype(str).str.strip().str.title()
df['Crash_Type'] = df['Crash_Type'].astype(str).str.strip().str.title()
print(df)

# 5
# Convert Timestamp & Feature Engineering Adding

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour
df['Day_of_Week'] = df['Timestamp'].dt.day_name()

#Map Accident Types
severity_mapping = {
    'None': 0,
    'Rear-end': 1,
    'Side-swipe': 1,
    'T-bone': 2,
    'Pedestrian': 3
    
}

df['Crash_Severity_Score'] = df['Crash_Type'].map(severity_mapping).fillna(0)
print(f"-> Data cleaning & feature engineering complete!")
print(f"-> Final clean dataset contains {len(df)} valid rows.\n")

print("--- SAMPLE OF YOUR FINAL CLEAN DATAFRAME ---")
print(df[['Timestamp', 'Approach_Leg', 'Traffic_Volume', 'Hour', 'Day_of_Week', 'Crash_Severity_Score']].head(3))