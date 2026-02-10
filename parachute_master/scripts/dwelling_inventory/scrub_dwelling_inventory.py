import os
import sys
import pandas as pd

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ampy.integrations.peculiar_inventory import PeculiarInventoryIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import FC

# Thresholds in milliseconds
THRESHOLDS = {
    "PendingRepair": 3 * 24 * 60 * 60 * 1000,  # 3 days
    "PendingResearch": 3 * 24 * 60 * 60 * 1000 * .9,  # 3 days
    "Transshipment": 55 * 24 * 60 * 60 * 1000 * .9,  # 55 days
    "Inbound": 3 * 24 * 60 * 60 * 1000  # 3 days
}

def get_short_containers(file_name, bucket):
    df = pd.read_csv(file_name)
    threshold = THRESHOLDS[bucket]
    # Filter containers that exceed the dwell time threshold
    short_containers = df[df['Idle Time (ms)'] > threshold]
    
    # Group by container and sum quantities
    grouped_containers = short_containers.groupby('Container')['Quantity'].sum().reset_index()
    return grouped_containers

def process_files():
    # List of files to process
    short_buckets = ["PendingRepair", "PendingResearch", "Transshipment"]
    tqa_buckets = ["Inbound"]
    other_buckets = ["Outbound", "ProblemSolve"]
    all_short_containers = pd.DataFrame(columns=['Container', 'Quantity'])
    all_tqa_containers = pd.DataFrame(columns=['Container', 'Quantity'])

    for bucket in short_buckets:
        file_name = f"{bucket}-None.csv"
        if os.path.exists(file_name):
            short_containers = get_short_containers(file_name, bucket)
            all_short_containers = pd.concat([all_short_containers, short_containers])

    for bucket in tqa_buckets:
        file_name = f"{bucket}-None.csv"
        if os.path.exists(file_name):
            tqa_containers = get_short_containers(file_name, bucket)
            all_tqa_containers = pd.concat([all_tqa_containers, tqa_containers])

    # Write the short containers to short_containers.csv
    all_short_containers.to_csv('short_containers.csv', index=False)

    # Write the TQA containers to tqa_containers.csv
    all_tqa_containers.to_csv('tqa_containers.csv', index=False)

    # Cleanup: remove the downloaded CSV files (commented out for testing)
    for bucket in short_buckets:
        file_name = f"{bucket}-None.csv"
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted {file_name}")

    for bucket in tqa_buckets:
        file_name = f"{bucket}-None.csv"
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted {file_name}")

    # Cleanup: remove the downloaded CSV files (commented out for testing)
    for bucket in other_buckets:
        file_name = f"{bucket}-None.csv"
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted {file_name}")

def main():
    fc = FC  # Assumes there is a FULFILLMENT_CENTER value in config.py
    inventory_integration = PeculiarInventoryIntegration(fc=fc)
    # Commented out for testing
    inventory_integration.get_scrub_buckets_data()
    process_files()  # Process the files and cleanup afterwards

    # Run the short_containers.py script
    os.system('python short_containers.py')
    #os.system('python tqa_containers.py')
    os.system('python send_shorts_email.py')

if __name__ == "__main__":
    main()
