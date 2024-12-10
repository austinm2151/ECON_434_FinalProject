import pandas as pd

# Path to your .dta file
file_path = "/Users/austinm2151/Desktop/ECON 434 - Final Project/PSIDconsumption_data.dta"

# Load the .dta file into a pandas DataFrame
data = pd.read_stata(file_path)

# Display the first few rows
print(data.head())

# Optional: Save as CSV for easier viewing
data.to_csv("output.csv", index=False)
