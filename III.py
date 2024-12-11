import pandas as pd
import numpy as np

# Load poverty thresholds data
poverty_thresholds_raw = pd.read_csv("poverty_thresholds_cleaned.csv")

# Cap family size at 9 and children at 8 (9 and 8 represent "9 and more" and "8 and more")
poverty_thresholds_raw['FamilySize'] = poverty_thresholds_raw['FamilySize'].apply(lambda x: min(x, 9))
poverty_thresholds_raw['Kids'] = poverty_thresholds_raw['Kids'].apply(lambda x: min(x, 8))

# Pivot the poverty thresholds dataset to separate ThresholdType into columns
poverty_thresholds = poverty_thresholds_raw.pivot(
    index=["FamilySize", "Kids"],
    columns="ThresholdType",
    values="ThresholdValue"
).reset_index()

# Rename columns for clarity
poverty_thresholds.columns = ["family_size", "children", "threshold", "threshold_65_plus"]

# Load household data
data = pd.read_csv("output.csv")

# Cap family size and number of children in the household dataset
data['famsze'] = data['famsze'].apply(lambda x: min(x, 9))
data['nchild'] = data['nchild'].apply(lambda x: min(x, 8))

# Ensure data types for merging
data['famsze'] = data['famsze'].astype(int)
data['nchild'] = data['nchild'].astype(int)

# Merge poverty thresholds into household data
data = data.merge(
    poverty_thresholds[['family_size', 'children', 'threshold']],
    how='left',
    left_on=['famsze', 'nchild'],
    right_on=['family_size', 'children']
)

# Check for missing thresholds and print them
missing_thresholds = data[data['threshold'].isnull()]
if not missing_thresholds.empty:
    print("Warning: Missing poverty thresholds for these family sizes and children combinations:")
    print(missing_thresholds[['famsze', 'nchild']].drop_duplicates())

# Extrapolate thresholds for missing values if necessary
def extrapolate_threshold(row):
    if pd.isnull(row['threshold']):
        if row['famsze'] == 9:
            return poverty_thresholds[poverty_thresholds['family_size'] == 9]['threshold'].max()
        elif row['nchild'] == 8:
            return poverty_thresholds[poverty_thresholds['children'] == 8]['threshold'].max()
    return row['threshold']

data['threshold'] = data.apply(extrapolate_threshold, axis=1)

# Adjust thresholds and incomes to 2016 dollars using CPI
data['real_threshold'] = data['threshold'] / (data['cpi'] / 100)
data['real_income'] = data['wly'] / (data['cpi'] / 100)

# Classify households as below or above the poverty line
data['below_poverty_line'] = data['real_income'] < data['real_threshold']

# Calculate poverty rate by year
poverty_rate_by_year = data.groupby('year').agg(
    total_households=('wly', 'count'),
    households_below_poverty=('below_poverty_line', 'sum')
).reset_index()

poverty_rate_by_year['poverty_rate'] = poverty_rate_by_year['households_below_poverty'] / poverty_rate_by_year['total_households']

# Save the results
poverty_rate_by_year.to_excel("poverty_rate_analysis.xlsx", index=False)

print("Poverty rate analysis saved to 'poverty_rate_analysis.xlsx'.")