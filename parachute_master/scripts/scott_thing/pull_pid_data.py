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

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ampy.integrations.firefox import FirefoxIntegration  # Replace 'your_module' with the actual module name

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
        url = (f"https://monitorportal.amazon.com/igraph?SchemaName1=Service&DataSet1=Prod&Marketplace1={FC}&HostGroup1=ALL&Host1=ALL&"
               f"ServiceName1=AFTCartonDataService&MethodName1=CreateCartonFromFreightLabel&Client1=ALL&MetricClass1=NONE&Instance1=NONE&"
               f"Metric1=CartonEventPublish.Created&Period1=OneMinute&Stat1=sum&LiveData1=true&Label1=Manual%20Cartons&UserLabel1=Manual%20Cartons&"
               f"SchemaName2=Service&ServiceName2=AFTInboundDirectorService&MethodName2=PendingCartonLockSQSConsumer&MetricClass2=HANDSCANNER&"
               f"Instance2=ALL&Metric2=FirstPerformanceForCarton&Label2=cPrEditor%20NVF%20A&UserLabel2=cPrEditor%20NVF%20A&SchemaName3=Service&"
               f"MetricClass3=UNKNOWN&Label3=cPrEditor%20NVF%20B&UserLabel3=cPrEditor%20NVF%20B&SchemaName4=Service&MetricClass4=PID&Label4=PID%20NVF&"
               f"UserLabel4=PID%20NVF&SchemaName5=Service&MetricClass5=AROS&Label5=AROS%20NVF&UserLabel5=AROS%20NVF&SchemaName6=Service&"
               f"MetricClass6=MARS&Label6=MARS%20NVF&UserLabel6=MARS%20NVF&HeightInPixels=250&WidthInPixels=600&GraphTitle={FC}%20NVF%20Only%20"
               f"%22PID%22%20Cartons%20Created&DecoratePoints=true&GraphType=zoomer&StartTime1={start_utc}&EndTime1={end_utc}&"
               f"FunctionExpression1=M1&FunctionLabel1=Manual%20Cartons&FunctionYAxisPreference1=left&FunctionExpression2=SUM%28M2%2C%20M3%29&"
               f"FunctionLabel2=cPrEditor%20Cartons&FunctionYAxisPreference2=left&FunctionExpression3=SUM%28M4%29&FunctionLabel3=PID%20Cartons&"
               f"FunctionYAxisPreference3=left&FunctionExpression4=SUM%28M5%29&FunctionLabel4=AROS%20Cartons&FunctionYAxisPreference4=right&"
               f"FunctionExpression5=SUM%28M6%29&FunctionLabel5=MARS%20Cartons&FunctionYAxisPreference5=left&FunctionExpression6=SUM%28M1%2CM2%2CM3%2CM4%2CM5%2CM6%29&"
               f"FunctionLabel6=Total%20%22PID%22%20Cartons%20%28sum%20of%20sums%3A%20%7Bsum%7D%29&FunctionYAxisPreference6=left&FunctionColor6=default")
        
        # Navigate to the URL and process the data
        driver.get(url)
        #time.sleep(2)  # Ensure the page loads

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
            data.iloc[:, 6] = pd.to_numeric(data.iloc[:, 6], errors='coerce')
            # Summing values from row 7 onwards in column G (6th index)
            total_pid_cartons = data.iloc[6:, 6].sum()
            results.append((date, start, end, total_pid_cartons))
            os.remove(csv_file)  # Remove the file after processing

# Output results to CSV
output_file = 'deep_dive_report.csv'
with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Date', 'Start Time', 'End Time', 'Total PID Cartons'])
    csvwriter.writerows(results)

print(f"Results written to {output_file}")

# Close the driver
driver.quit()
