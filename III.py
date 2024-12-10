import pandas as pd
import numpy as np

# Load poverty thresholds file, skipping description rows
poverty_thresholds_raw = pd.read_excel(
    "poverty_thresholds.xlsx",
    skiprows=4  # Adjusted based on the file structure
)

# Rename columns based on actual structure
poverty_thresholds_raw.columns = [
    "family_size", "weighted_average_threshold", "none", "one", "two", "three", 
    "four", "five", "six", "seven", "eight_or_more"
]

# Drop any rows with NaN in critical columns
poverty_thresholds_raw = poverty_thresholds_raw.dropna(subset=["family_size", "weighted_average_threshold"])

# Reshape the table to long format
child_columns = ["none", "one", "two", "three", "four", "five", "six", "seven", "eight_or_more"]
poverty_thresholds = poverty_thresholds_raw.melt(
    id_vars=["family_size", "weighted_average_threshold"],
    value_vars=child_columns,
    var_name="children",
    value_name="threshold"
)

# Clean and convert data types
poverty_thresholds['family_size'] = poverty_thresholds['family_size'].str.extract('(\d+)').astype(float)
poverty_thresholds['children'] = poverty_thresholds['children'].str.extract('(\d+)').fillna(0).astype(int)
poverty_thresholds['threshold'] = poverty_thresholds['threshold'].astype(float)

# Add year column for 2023 poverty thresholds
poverty_thresholds['year'] = 2023

# Save cleaned poverty thresholds for verification (optional)
poverty_thresholds.to_csv("cleaned_poverty_thresholds.csv", index=False)

# Load household data
data = pd.read_csv("output.csv")

# Handle zero or negative values in family income
data['wly'] = data['wly'].apply(lambda x: max(x, 1e-10))  # Family income

# Merge poverty thresholds into household data
data = data.merge(poverty_thresholds, how='left', left_on=['year', 'famsze', 'nchild'], right_on=['year', 'family_size', 'children'])

# Adjust poverty threshold to real dollars using CPI
data['real_threshold'] = data['threshold'] / data['cpi'] * 100  # Adjust to base year (e.g., 2000 = 100)

# Classify households as below or above the poverty line
data['below_poverty_line'] = data['wly'] < data['real_threshold']

# Calculate poverty rate by year
poverty_rate_by_year = data.groupby('year').agg(
    total_households=('wly', 'count'),
    households_below_poverty=('below_poverty_line', 'sum')
).reset_index()

poverty_rate_by_year['poverty_rate'] = poverty_rate_by_year['households_below_poverty'] / poverty_rate_by_year['total_households']

# Save the results
poverty_rate_by_year.to_excel("poverty_rate_analysis.xlsx", index=False)

print("Poverty rate analysis saved to 'poverty_rate_analysis.xlsx'.")