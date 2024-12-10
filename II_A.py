import pandas as pd
import numpy as np

# Load dataset
data = pd.read_csv("output.csv")

# Handle zero or negative values in income and consumption
data['ly'] = data['ly'].apply(lambda x: max(x, 1e-10))
data['wly'] = data['wly'].apply(lambda x: max(x, 1e-10))
data['ndcons'] = data['ndcons'].apply(lambda x: max(x, 1e-10))  # Total non-durable consumption

# Add log-transformed income and consumption columns
data['log_individual_income'] = np.log(data['ly'])
data['log_family_income'] = np.log(data['wly'])
data['log_consumption'] = np.log(data['ndcons'])

# Group columns for inequality analysis
group_columns = ['educ_hd', 'region', 'age_hd', 'race_hd']

# Total Inequality Metrics
total_inequality = pd.DataFrame({
    "Metric": ["Variance of Log Individual Income", "Variance of Log Family Income", "P90/P10 (Individual Income)", "P90/P10 (Family Income)", "Variance of Log Consumption", "P90/P10 (Consumption)"],
    "Value": [
        data['log_individual_income'].var(),
        data['log_family_income'].var(),
        np.percentile(data['ly'], 90) / np.percentile(data['ly'], 10),
        np.percentile(data['wly'], 90) / np.percentile(data['wly'], 10),
        data['log_consumption'].var(),
        np.percentile(data['ndcons'], 90) / np.percentile(data['ndcons'], 10)
    ]
})

# Inequality Across Groups
inequality_across_groups = []
for group in group_columns:
    grouped = data.groupby(group).agg(
        average_individual_income=('ly', 'mean'),
        average_family_income=('wly', 'mean'),
        average_consumption=('ndcons', 'mean'),
        variance_log_individual_income=('log_individual_income', 'var'),
        variance_log_family_income=('log_family_income', 'var'),
        variance_log_consumption=('log_consumption', 'var')
    ).reset_index()
    grouped['group'] = group
    inequality_across_groups.append(grouped)

inequality_across_groups_df = pd.concat(inequality_across_groups, ignore_index=True)

# Inequality Within Groups
within_group_inequality = []
for group in group_columns:
    group_data = data.groupby(group)
    for name, group_df in group_data:
        within_group_inequality.append({
            "Group": group,
            "Group Value": name,
            "Variance of Log Individual Income": group_df['log_individual_income'].var(),
            "Variance of Log Family Income": group_df['log_family_income'].var(),
            "Variance of Log Consumption": group_df['log_consumption'].var()
        })

within_group_inequality_df = pd.DataFrame(within_group_inequality)

# Evolution of Inequality Over Time
inequality_over_time = data.groupby('year').agg(
    variance_log_individual_income=('log_individual_income', 'var'),
    variance_log_family_income=('log_family_income', 'var'),
    variance_log_consumption=('log_consumption', 'var'),
    p90_p10_consumption=('ndcons', lambda x: np.percentile(x, 90) / np.percentile(x, 10))
).reset_index()

# Analysis of Commodity Shares
commodity_columns = [
    "carins", "carrepair", "parking", "gasoline", "pubtransport", "taxi", "othtransport",
    "utilities", "clothing", "phone", "trips", "entert", "repairs", "homeins",
    "yearlyrent", "school", "othrschool", "totalhltcare", "childcare", "totfood"
]

# Compute shares of each commodity
for commodity in commodity_columns:
    data[f"share_{commodity}"] = data[commodity] / data['ndcons']

# Group by year and compute average share for each commodity
commodity_shares_over_time = data.groupby("year").agg(
    {f"share_{commodity}": "mean" for commodity in commodity_columns}
).reset_index()

# Compute variance of log shares over time for each commodity
log_share_variance = data.groupby("year").agg(
    {f"share_{commodity}": lambda x: pd.Series(np.log(x).replace(-np.inf, 0)).var() for commodity in commodity_columns}
).reset_index()

# Save all results to a single Excel file
output_path = "inequality_analysis.xlsx"
with pd.ExcelWriter(output_path) as writer:
    total_inequality.to_excel(writer, sheet_name="Total Inequality", index=False)
    inequality_across_groups_df.to_excel(writer, sheet_name="Across Groups", index=False)
    within_group_inequality_df.to_excel(writer, sheet_name="Within Groups", index=False)
    inequality_over_time.to_excel(writer, sheet_name="Over Time", index=False)
    commodity_shares_over_time.to_excel(writer, sheet_name="Commodity Shares", index=False)
    log_share_variance.to_excel(writer, sheet_name="Log Share Variance", index=False)

print(f"Inequality analysis results (including commodity shares) saved to {output_path}")