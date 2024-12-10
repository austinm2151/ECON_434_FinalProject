import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Load dataset (assumed CSV format)
data = pd.read_csv("output.csv")

# Compute total expenditure (ndcons) and log of total expenditure
data['log_ndcons'] = np.log(data['ndcons'])

# Define the list of commodities to analyze
commodities = [
    "carins", "carrepair", "parking", "gasoline", "pubtransport", 
    "taxi", "othtransport", "utilities", "clothing", "phone", "trips", 
    "entert", "repairs", "homeins", "yearlyrent", "school", "othrschool", 
    "totalhltcare", "childcare", "totfood"
]

# Compute share of total expenditure for each commodity
for commodity in commodities:
    data[f'share_{commodity}'] = data[commodity] / data['ndcons']

# Prepare results storage
results = []

# Generate regression results and enhanced interpretation
for commodity in commodities:
    formula = f"share_{commodity} ~ log_ndcons + age_hd + nchild + marstat + educ_hd + C(year)"
    model = smf.ols(formula=formula, data=data).fit()
    
    # Extract regression details
    beta_log_ndcons = model.params['log_ndcons']
    p_value = model.pvalues['log_ndcons']
    avg_share = data[f'share_{commodity}'].mean()  # Average share of expenditure
    significance = "Significant" if p_value < 0.05 else "Not Significant"
    classification = "Luxury" if beta_log_ndcons > 0 else "Necessity"
    
    # Append results for interpretation
    results.append({
        "Commodity": commodity,
        "Beta_log_ndcons": beta_log_ndcons,
        "P-Value": p_value,
        "Average Share": avg_share,
        "Significance": significance,
        "Classification": classification
    })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Save the enhanced results to a CSV file
results_df.to_csv("engel_curve_interpretation.csv", index=False)
print("Enhanced Engel curve results saved to 'engel_curve_interpretation.csv'.")

# Function to plot and save individual Engel curves
def plot_individual_engel_curve(commodity):
    plt.figure(figsize=(8, 6))
    # Scatterplot of share vs. log total expenditure
    sns.scatterplot(x=data['log_ndcons'], y=data[f'share_{commodity}'], alpha=0.5, label="Data")
    
    # Fit a simple Engel curve regression line
    formula = f"share_{commodity} ~ log_ndcons"
    model = smf.ols(formula=formula, data=data).fit()
    predicted = model.predict(data['log_ndcons'])
    
    # Plot the regression line
    sns.lineplot(x=data['log_ndcons'], y=predicted, color='red', label="Engel Curve")
    
    # Customize the plot
    plt.title(f"Engel Curve for {commodity.capitalize()}")
    plt.xlabel("Log of Total Expenditure")
    plt.ylabel("Share")
    plt.legend()
    
    # Save the individual plot
    os.makedirs("images", exist_ok=True)
    plt.savefig(f"images/{commodity}_engel_curve.png", bbox_inches='tight')
    plt.close()
    print(f"Saved individual Engel curve for {commodity} to 'images/{commodity}_engel_curve.png'")

# Generate and save individual plots
for commodity in commodities:
    plot_individual_engel_curve(commodity)

# Combine all graphs into a single image
def plot_combined_engel_curves():
    rows, cols = 5, 4  # Adjust layout to fit all graphs (5 rows x 4 columns for 20 commodities)
    fig, axes = plt.subplots(rows, cols, figsize=(20, 15))
    axes = axes.flatten()
    
    # Plot each commodity
    for i, commodity in enumerate(commodities):
        sns.scatterplot(x=data['log_ndcons'], y=data[f'share_{commodity}'], alpha=0.5, ax=axes[i], label="Data")
        formula = f"share_{commodity} ~ log_ndcons"
        model = smf.ols(formula=formula, data=data).fit()
        predicted = model.predict(data['log_ndcons'])
        sns.lineplot(x=data['log_ndcons'], y=predicted, color='red', ax=axes[i], label="Engel Curve")
        axes[i].set_title(f"{commodity.capitalize()}")
        axes[i].set_xlabel("Log of Total Expenditure")
        axes[i].set_ylabel("Share")
    
    # Remove any empty subplots
    for j in range(len(commodities), len(axes)):
        fig.delaxes(axes[j])
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the combined image
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = f"images/engel_curves_combined_{date_str}.png"
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Combined Engel curves saved to {output_path}")

# Create the combined plot
plot_combined_engel_curves()
