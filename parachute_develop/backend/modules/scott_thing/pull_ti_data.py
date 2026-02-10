import os
import sys
import time
import csv
from datetime import datetime, timedelta

# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from integrations.firefox import FirefoxIntegration  # Replace 'your_module' with the actual module name
from integrations.ppr import ProcessPathRollupIntegration  # Replace 'your_module' with the actual module name

# Initialize the driver using the existing FirefoxIntegration class
driver = FirefoxIntegration.get_authenticated_driver()


# Define the date and time ranges in EST
dates = ['2024/08/31']
times = [('18:30', '19:00'), ('20:00', '20:30'), ('21:00', '21:30'), 
         ('21:45', '22:15'), ('23:00', '23:30'), ('23:30', '00:00'), 
         ('00:45', '01:15'), ('01:45', '02:15'), ('02:45', '03:15')]

# Initialize the integration
ppr_integration = ProcessPathRollupIntegration(driver)

# Iterate through dates and times
results = []
for i, date in enumerate(dates):
    for start, end in times:
        start_date = datetime.strptime(f"{date} {start}", "%Y/%m/%d %H:%M")
        end_date = datetime.strptime(f"{date} {end}", "%Y/%m/%d %H:%M")
        
        if start_date.hour < 12:
            start_date += timedelta(days=1)

        # Increment date if time is before noon (as per the requirement)
        if end_date.hour < 12:
            end_date += timedelta(days=1)

        actual_volume = ppr_integration.get_case_ti(start_date, end_date)
        results.append((date, start, end, actual_volume))

# Output results to CSV
output_file = 'case_transfer_in_report.csv'
with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Date', 'Start Time', 'End Time', 'Case Transfer In Volume'])
    csvwriter.writerows(results)

print(f"Results written to {output_file}")
