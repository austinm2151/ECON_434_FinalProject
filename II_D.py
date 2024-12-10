import pandas as pd
import numpy as np

# Load dataset
data = pd.read_csv("output.csv")

# Handle zero or negative values in income and consumption
data['ly'] = data['ly'].apply(lambda x: max(x, 1e-10))  # Individual income
data['wly'] = data['wly'].apply(lambda x: max(x, 1e-10))  # Family income
data['ndcons'] = data['ndcons'].apply(lambda x: max(x, 1e-10))  # Total consumption

# Add log-transformed income and consumption columns
data['log_individual_income'] = np.log(data['ly'])
data['log_family_income'] = np.log(data['wly'])
data['log_consumption'] = np.log(data['ndcons'])

# Create age variable based on birth year and survey year
data['age'] = data['year'] - data['yrbirth']

# Group by birth cohort (yrbirth) and survey year (age proxy)
cohort_analysis = data.groupby(['yrbirth', 'age']).agg(
    variance_log_individual_income=('log_individual_income', 'var'),
    variance_log_family_income=('log_family_income', 'var'),
    variance_log_consumption=('log_consumption', 'var'),
    p90_p10_individual_income=('ly', lambda x: np.percentile(x, 90) / np.percentile(x, 10)),
    p90_p10_family_income=('wly', lambda x: np.percentile(x, 90) / np.percentile(x, 10)),
    p90_p10_consumption=('ndcons', lambda x: np.percentile(x, 90) / np.percentile(x, 10)),
    average_individual_income=('ly', 'mean'),
    average_family_income=('wly', 'mean'),
    average_consumption=('ndcons', 'mean')
).reset_index()

# Save results for cohort analysis
output_path = "cohort_inequality_analysis.xlsx"
cohort_analysis.to_excel(output_path, index=False)
print(f"Birth cohort inequality analysis saved to {output_path}")