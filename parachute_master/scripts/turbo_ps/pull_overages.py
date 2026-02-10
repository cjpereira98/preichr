import re
import csv
from datetime import datetime

# Define the pattern to match the log entries
log_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Processing overage container: (\w+)')

# Initialize an empty list to hold the extracted data
overaged_containers = []

# Read the turbo_ps.log file
with open('turbo_ps.log', 'r') as log_file:
    for line in log_file:
        match = log_pattern.search(line)
        if match:
            timestamp = match.group(1)
            container_id = match.group(2)
            # Append the tuple (timestamp, container_id) to the list
            overaged_containers.append((timestamp, container_id))

# Write the extracted data to overaged_containers.csv
with open('overaged_containers.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Timestamp', 'Container ID'])  # Write header
    writer.writerows(overaged_containers)  # Write the data

print(f"Extracted {len(overaged_containers)} entries into 'overaged_containers.csv'.")
