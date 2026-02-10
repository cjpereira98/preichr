import os
import sys
import time
import csv
from datetime import datetime, timedelta
import pandas as pd
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import FC

# Initialize the driver using the existing FirefoxIntegration class
driver = FirefoxIntegration.get_authenticated_driver()

# Function to convert PST to UTC in the required format
def convert_pst_to_utc(pst_date, pst_start_time, pst_end_time):
    pst_format = "%Y/%m/%d %H:%M"
    start_datetime = datetime.strptime(f"{pst_date} {pst_start_time}", pst_format)
    end_datetime = datetime.strptime(f"{pst_date} {pst_end_time}", pst_format)
    
    # If end time is before start time, end date should be the next day
    if end_datetime < start_datetime:
        end_datetime += timedelta(days=1)

    # Convert to UTC
    start_datetime_utc = start_datetime + timedelta(hours=7)
    end_datetime_utc = end_datetime + timedelta(hours=7)

    # Return formatted strings
    start_str = start_datetime_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_datetime_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    return start_str, end_str

# Define the date and time ranges in PST
dates = ['2024/08/31']
times = [('15:30', '16:00'), ('17:00', '17:30'), ('18:00', '18:30'), 
         ('18:45', '19:15'), ('20:00', '20:30'), ('20:30', '21:00'), 
         ('21:45', '22:15'), ('22:45', '23:15'), ('23:45', '00:15')]

# Iterate through dates and times
results = []
for i, date in enumerate(dates):
    for start, end in times:
        start_utc, end_utc = convert_pst_to_utc(date, start, end)
        
        # Construct the URL with the converted UTC start and end times
        url = (f"https://monitorportal.amazon.com/igraph?SchemaName1=Search&Pattern1=dataset%3D%24Prod%24%20marketplace%3D%24{FC}%24%20hostgroup%3D%24ALL%24%20host%3D%24ALL%24%20"
               f"servicename%3D%24FCReceiveWebUIWebsiteClient%24%20methodname%3D%24DecoupledSort%24%20metric%3D%24aft.receive.sortedItemsCount.%20schemaname%3DService%20instance%3D%24ALL%24&"
               f"Period1=OneMinute&Stat1=sum&LiveData1=true&SchemaName2=Search&Pattern2={FC}%20marketplace%3D%24{FC}-OPEX%20fclm%20methodname%3D%24itemDiverted%24&Stat2=n&"
               f"SchemaName3=Search&Pattern3={FC}%20stow%20case%20clean%20schemaname%3DService%20metric%3D%24Count.Call.Service.StowService.cleanContainer%24&Stat3=sum&"
               f"YAxisPreference3=right&SchemaName4=Search&Pattern4={FC}%20stow%20move%20servicename%3D%24FCStowService%24%20methodname%3D%24ALL%24%20schemaname%3DService%20metric%3D%24CaseToToteConductor.eachMove%24&"
               f"SchemaName5=Search&Pattern5=schemaname%3D%24Service%24%20dataset%3D%24Prod%24%20marketplace%3D%24{FC}%24%20hostgroup%3D%24ALL%24%20host%3D%24ALL%24%20"
               f"servicename%3D%24ItemSortationService%24%20methodname%3D%28%24processDamagedItem%24%20OR%20%24pushThroughContainer%24%20OR%20%24processUnboundItem%24%29%20"
               f"client%3D%24ALL%24%20metricclass%3D%24NONE%24%20instance%3D%24NONE%24%20metric%3D%24Time%24&Stat5=n&LiveData5=false&"
               f"YAxisPreference5=left&SchemaName6=Search&Pattern6=SLOT_SORTED_ITEMS_COUNT%20{FC}%20schemaname%3DService%20methodname%3D%24itemPlacedInSlot%24&"
               f"Stat6=sum&HeightInPixels=400&WidthInPixels=800&GraphTitle=Sort%20Volume%20vs%20Decant%20Volume&ShowXAxisLabel=false&"
               f"GraphType=pie&TZ=EST@TZ%3A%20EST&ShowGaps=false&StartTime1={start_utc}&EndTime1={end_utc}&FunctionExpression1=SUM%28S1%2CS2%2C%20S5%2C%20S6%29&"
               f"FunctionLabel1=Sort%20Volume%20Processed%3A%20%7Bsum%7C%25%2C1.0f%7D&FunctionYAxisPreference1=left&FunctionExpression2=SUM%28S4%29&"
               f"FunctionLabel2=Decant%20Volume%20Processed%3A%20%7Bsum%7C%25%2C1.0f%7D&FunctionYAxisPreference2=left")

        # Navigate to the URL and process the data
        driver.get(url)

        # Wait for the CSV link to be clickable and download the CSV
        csv_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'csvLink'))
        )
        csv_link.click()
        time.sleep(2)  # Wait for the download to complete

        # Process the downloaded CSV
        csv_file = os.path.join(os.getcwd(), 'data.csv')  # Adjust the path if necessary
        if os.path.exists(csv_file):
            data = pd.read_csv(csv_file)
            # Convert the column to numeric, forcing non-numeric values to NaN
            data.iloc[:, 2] = pd.to_numeric(data.iloc[:, 2], errors='coerce')
            # Summing values from row 7 onwards in column C (2nd index)
            total_sorted_items = data.iloc[6:, 2].sum()
            results.append((date, start, end, total_sorted_items))
            os.remove(csv_file)  # Remove the f
# Output results to CSV
output_file = 'sort_data_report.csv'
with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Date', 'Start Time', 'End Time', 'Total Sorted Items'])
    csvwriter.writerows(results)

print(f"Results written to {output_file}")

# Close the driver
driver.quit()