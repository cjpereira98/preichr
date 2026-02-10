from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
from datetime import datetime, timedelta
import requests

# Set up the headless Firefox driver with download settings
options = webdriver.FirefoxOptions()
options.headless = True  # Run in headless (hidden) mode
profile = webdriver.FirefoxProfile()

# Set download directory to current working directory
cwd = os.getcwd()
profile.set_preference("browser.download.dir", cwd)
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")
profile.set_preference("browser.download.manager.showWhenStarting", False)
options.profile = profile

print("Initializing headless Firefox driver...")
driver = webdriver.Firefox(options=options)

try:
    # Navigate to the URL
    print("Navigating to the Alarm History Reports page...")
    driver.get("http://10.225.139.3/gsmi/AlarmHistoryReports.aspx")

    # Wait for the Alarm Detail button to be visible and click it
    time.sleep(5)
    print("Clicking on the download button...")
    download_button = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_Tab3ReportViewer_ctl06_ctl04_ctl00_Button')
    download_button.click()

    time.sleep(1)
    print("Selecting the Excel format for download...")
    download_selection_list = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_Tab3ReportViewer_ctl06_ctl04_ctl00_Menu')
    excel_selection_button = download_selection_list.find_elements(By.TAG_NAME, "div")[0]
    excel_selection_button.click()

    # Wait for the download to complete
    download_path = os.path.join(cwd, "AlarmsHistory.xls")
    print("Waiting for the file to download...")
    while not os.path.exists(download_path):
        time.sleep(5)  # Check every 5 seconds

    print("Download completed. Quitting the driver.")
    driver.quit()  # Quit the driver as soon as the file is downloaded

    # Load Excel file into a pandas DataFrame starting from row 9
    df = pd.read_excel(download_path, skiprows=8)  # Row 9 corresponds to skipping the first 8 rows

    # Remove the downloaded file after loading it into the DataFrame
    os.remove(download_path)

    # Get current time minus 5 minutes
    current_time = datetime.now()
    time_threshold = current_time - timedelta(minutes=5)

    # Process each row to find actively jamming items
    for index, row in df.iterrows():
        try:
            active_time = row['Active Time']  # This is already a pandas.Timestamp object
            duration_minutes = row['Duration \n(min)']  # Column with newline in the header
            end_time = active_time + timedelta(minutes=duration_minutes)
            
            if end_time >= time_threshold and duration_minutes > 10:
                # Actively jamming
                location = row['Description']
                duration = str(duration_minutes)
                department = row['Area']
                
                # Convert the active_time to a formatted string
                active_time_str = active_time.strftime("%m/%d/%Y %I:%M:%S %p")
                
                # Prepare the payload
                payload = {
                    "Location": location,
                    "Duration": duration,
                    "Department": department,
                    "Start Timestamp": active_time_str  # Formatted timestamp string
                }
                
                # Send Slack message
                response = requests.post(
                    "https://hooks.slack.com/workflows/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",
                    json=payload
                )
                print(f"Sent to Slack: {response.status_code}")
        
        except Exception as e:
            print(f"Error processing row {index}: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
    driver.quit()

