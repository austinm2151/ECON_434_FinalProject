import pandas as pd
import numpy as np

# Load dataset
data = pd.read_csv("output.csv")

# Handle zero or negative values in consumption
data['ndcons'] = data['ndcons'].apply(lambda x: max(x, 1e-10))  # Total non-durable consumption
data['log_consumption'] = np.log(data['ndcons'])  # Log of total consumption

# Define consumption categories
consumption_columns = [
    "carins", "carrepair", "parking", "gasoline", "pubtransport", "taxi", "othtransport", 
    "utilities", "clothing", "phone", "trips", "entert", "repairs", "homeins", 
    "yearlyrent", "school", "othrschool", "totalhltcare", "childcare", "totfood"
]

# Compute total inequality in consumption
total_inequality_consumption = pd.DataFrame({
    "Metric": ["Variance of Log Consumption", "P90/P10 (Consumption)"],
    "Value": [
        data['log_consumption'].var(),
        np.percentile(data['ndcons'], 90) / np.percentile(data['ndcons'], 10)
    ]
})

# Inequality Across Groups
group_columns = ['educ_hd', 'region', 'age_hd', 'race_hd']
inequality_across_groups_consumption = []

for group in group_columns:
    grouped = data.groupby(group).agg(
        average_consumption=('ndcons', 'mean'),
        variance_log_consumption=('log_consumption', 'var')
    ).reset_index()
    grouped['group'] = group
    inequality_across_groups_consumption.append(grouped)

inequality_across_groups_consumption_df = pd.concat(inequality_across_groups_consumption, ignore_index=True)

# Inequality Within Groups
within_group_inequality_consumption = []
for group in group_columns:
    group_data = data.groupby(group)
    for name, group_df in group_data:
        within_group_inequality_consumption.append({
            "Group": group,
            "Group Value": name,
            "Variance of Log Consumption": group_df['log_consumption'].var()
        })

within_group_inequality_consumption_df = pd.DataFrame(within_group_inequality_consumption)

# Evolution of Consumption Inequality Over Time
inequality_over_time_consumption = data.groupby('year').agg(
    variance_log_consumption=('log_consumption', 'var'),
    p90_p10_consumption=('ndcons', lambda x: np.percentile(x, 90) / np.percentile(x, 10))
).reset_index()

# Save results to an Excel file
output_path = "consumption_inequality_analysis.xlsx"
with pd.ExcelWriter(output_path) as writer:
    total_inequality_consumption.to_excel(writer, sheet_name="Total Inequality", index=False)
    inequality_across_groups_consumption_df.to_excel(writer, sheet_name="Across Groups", index=False)
    within_group_inequality_consumption_df.to_excel(writer, sheet_name="Within Groups", index=False)
    inequality_over_time_consumption.to_excel(writer, sheet_name="Over Time", index=False)

print(f"Consumption inequality analysis results saved to {output_path}")