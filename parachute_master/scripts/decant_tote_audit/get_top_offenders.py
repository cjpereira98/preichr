import os
import sys
import pandas as pd
from datetime import datetime

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ampy.integrations.apollo import ApolloIntegration
from ampy.integrations.slack import SlackIntegration

def get_top_offenders():
    # Set the audit ID and date range for the previous day
    audit_id = 291

    # Set the date range to the last hour
    end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_date = (datetime.now() - pd.Timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

    # Get audit results from ApolloIntegration
    results = ApolloIntegration.get_audit_results(audit_id, start_date, end_date)

    if not results:
        print("No audit results found.")
        return

    # Convert results to a DataFrame
    df = pd.DataFrame(results)

    # Ensure 'Defective Qty' column is numeric
    df['Defective Qty'] = pd.to_numeric(df['Defective Qty'], errors='coerce')

    # Filter out unwanted logins
    df = df[~df['Associate Login'].isin(['N/A', 'aft-ps', 'dc-owl', 'not_found'])]

    # Calculate the sum of defective quantities and the count of occurrences for each login
    offender_summary = df.groupby('Associate Login').agg(
        Defective_Quantity=('Defective Qty', 'sum'),
        Defective_Containers=('Associate Login', 'count')
    ).reset_index()

    # Find the login with the most defective units
    top_offender = offender_summary.loc[offender_summary['Defective_Quantity'].idxmax()]

    print(f"Top offender: {top_offender['Associate Login']}")

    # Prepare the Slack message
    slack_message = {
        "Employee Login": str(top_offender['Associate Login']),
        "Defective Quantity": str(top_offender['Defective_Quantity']),
        "Defective Containers": str(top_offender['Defective_Containers'])
    }

    # Send the message via SlackIntegration
    webhook_url = 'https://hooks.slack.com/workflows/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'
    SlackIntegration.send_message(webhook_url, slack_message)

if __name__ == "__main__":
    get_top_offenders()
