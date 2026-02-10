import pandas as pd
import logging
from dateutil import parser
import pytz

# Configure logging
logging.basicConfig(filename='update_reconciles.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define a dictionary for mapping timezone abbreviations to UTC offsets using pytz
tzinfos = {
    'EDT': pytz.timezone('US/Eastern'),  # Eastern Daylight Time (UTC-4/UTC-5)
    'EST': pytz.timezone('US/Eastern'),  # Eastern Standard Time (UTC-5)
    # Add other timezones as needed
}

def update_reconciles():
    logging.info("Starting the update_reconciles process.")
    csv_file = 'AFT Transshipment Hub.csv'
    output_file = 'reconciles.txt'
    
    # Read the CSV file using pandas
    df = pd.read_csv(csv_file)

    # Filter rows with 'Details' as 'Stowing Progress' and 'YMS Arrival Time' not blank
    filtered_df = df[(df['Details'] == 'Stowing Progress') & (df['YMS Arrival Time'].notna())]

    shipment_ids = []

    for index, row in filtered_df.iterrows():
        try:
            # Parse the received time with tzinfos
            received_time = parser.parse(row['Received Time'], tzinfos=tzinfos)
            # Convert received_time to UTC for uniformity
            received_time_utc = received_time.astimezone(pytz.utc)

            # Check conditions including '% Remaining' <= 3%
            if (float(row['Units for Reconcile']) < 300 and 
                float(row['% Remaining']) <= .03):
                shipment_ids.append(row['Shipment Reference Id'])
                df.at[index, 'Reconcile'] = 1  # Set Reconcile to 1
                logging.info(f"Shipment ID {row['Shipment Reference Id']} added to the list.")
        except Exception as e:
            logging.error(f"Error parsing date for row {row.to_dict()}: {e}")

    # Write the shipment IDs to the output file
    with open(output_file, 'w') as file:
        for shipment_id in shipment_ids:
            file.write(f"{shipment_id}\n")
            logging.info(f"Shipment ID {shipment_id} written to {output_file}.")

    # Write the modified DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)

    logging.info("Completed the update_reconciles process.")

if __name__ == "__main__":
    update_reconciles()
