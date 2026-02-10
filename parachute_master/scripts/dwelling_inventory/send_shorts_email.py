from datetime import datetime
import os
import sys
import pandas as pd

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ampy.integrations.outlook import OutlookIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import FC



def generate_shorts_report():
    # File paths
    csv_file_path = os.path.join(os.path.dirname(__file__), 'short_containers.csv')

    # Read the CSV into a pandas DataFrame
    #df = pd.read_csv(csv_file_path)

    #df = df[df['Reconcile'] != 1]

    # Filter data for the three tables
    #all_freight = df.copy()  # No filter on 'Pallets for Reconcile'
    #floor_loaded = df[df['Pallets for Reconcile'] == 0]  # 'Pallets for Reconcile' = 0
    #palletized = df[df['Pallets for Reconcile'] != 0]  # 'Pallets for Reconcile' != 0

    # Helper function to create a table
    #def create_table(filtered_df):
    #    table_html = """
    #    <table border="1" style="border-collapse: collapse;">
    #        <tr>
    #            <th>Arrived</th>
    #            <th>Received</th>
    #            <th>Description</th>
    #            <th>Units Pending Reconcile</th>
    #            <th>Loads</th>
    #        </tr>
       # """
       # conditions = [
       #     {'Arrived': None, 'Received': None, 'Description': 'Dwelling in AFT'},
       #     {'Arrived': None, 'Received': 'Y', 'Description': 'Just Received'},
       #     {'Arrived': 'Y', 'Received': None, 'Description': 'Just Arrived'},
       #     {'Arrived': 'Y', 'Received': 'N', 'Description': 'Arrived AND Not Received'},
       #     {'Arrived': 'N', 'Received': 'Y', 'Description': 'Received AND Not Arrived'}
       # ]
       # 
       # for condition in conditions:
       #     print(filtered_df)
       #     # Apply the filters based on the condition
       #     arrived_filter = (filtered_df['YMS Arrival Time'].notna() if condition['Arrived'] == 'Y' else 
       #                       filtered_df['YMS Arrival Time'].isna() if condition['Arrived'] == 'N' else 
       #                       pd.Series([True] * len(filtered_df), index=filtered_df.index))
       #     print(len(arrived_filter))
       #     print(arrived_filter)#

        #    received_filter = (filtered_df['Received Time'].notna() if condition['Received'] == 'Y' else 
        #                       filtered_df['Received Time'].isna() if condition['Received'] == 'N' else 
        #                       pd.Series([True] * len(filtered_df), index=filtered_df.index))
        #    #print(received_filter)
            #print(len(received_filter))

            #print(len(filtered_df))
        #    print(filtered_df)

         #   filtered_condition_df = filtered_df[arrived_filter & received_filter]
            #print(len(filtered_df))
            #filtered_df = filtered_df[received_filter]
            #print(len(filtered_df))
            
        #    units_pending_reconcile = filtered_condition_df['Units for Reconcile'].sum()
        #    loads = filtered_condition_df['Shipment Reference Id'].nunique()
            
        #    table_html += f"""
        #    <tr>
        #        <td>{condition['Arrived'] if condition['Arrived'] else 'NULL'}</td>
        #        <td>{condition['Received'] if condition['Received'] else 'NULL'}</td>
        #        <td>{condition['Description']}</td>
        #        <td>{units_pending_reconcile}</td>
        #        <td>{loads}</td>
        #    </tr>
        #    """
        
        #table_html += "</table>"
        #return table_html

    # Generate HTML for the email body with three tables
    email_body = f"""
    <html>
    <body>
        <p>Finished running scrub_dwelling_inventory.py</p>
    </body>
    </html>
    """

    # Send the email with the attached CSV file
    outlook = OutlookIntegration()
    outlook.create_html_email(
        to_addresses=["adamzisk@amazon.com", "giojust@amazon.com", "maxdycko@amazon.com", "preichr@amazon.com"],
        subject='Dwelling Inventory Scrubbed ' + datetime.now().strftime('%Y-%m-%d'),
        html_body=email_body,
        attachments=[csv_file_path],
        send_immediately=True
    )

if __name__ == "__main__":
    generate_shorts_report()
