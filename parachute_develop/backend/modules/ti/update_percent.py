import pandas as pd

# Load the CSV file
file_path = 'AFT Transshipment Hub.csv'
df = pd.read_csv(file_path)

# Fill 'Units for Reconcile' with 'Total Quantity' if it's blank
df['Units for Reconcile'] = df.apply(
    lambda row: row['Total Quantity'] if pd.isna(row['Units for Reconcile']) else row['Units for Reconcile'],
    axis=1
)

# Calculate '% Remaining' column and truncate to two decimal places
df['% Remaining'] = (df['Units for Reconcile'] / df['Total Quantity']).round(4)

# Save the updated DataFrame back to the CSV file
df.to_csv(file_path, index=False)
