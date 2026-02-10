import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
#from bs4 import BeautifulSoup
#import requests

# Set up download directory
download_dir = os.getcwd()
file_path = os.path.join(download_dir, "AFT Transshipment Hub.csv")

# Remove old file if it exists
if os.path.exists(file_path):
    os.remove(file_path)

# Set up Firefox options for downloading files
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", download_dir)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

# Start Firefox browser with options
driver = webdriver.Firefox(options=options)

# Navigate to the URL
driver.get("https://afttransshipmenthub-na.aka.amazon.com/SWF2/view-transfers/inbound/")

# Wait for authentication
time.sleep(20)

# Wait until the element is visible and select 100 from the dropdown
wait = WebDriverWait(driver, 10)
dropdown = wait.until(EC.visibility_of_element_located((By.NAME, "inboundTransfersTable_length")))
dropdown.click()
option = driver.find_element(By.XPATH, "//option[@value='100']")
option.click()

# Wait 1 second
time.sleep(1)

# Click the CSV download button
csv_button = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-default.buttons-csv.buttons-html5")
csv_button.click()

# Wait for the download to complete (optional)
time.sleep(5)

# Close the browser
#driver.quit()

# Wait for the download to complete (optional)
time.sleep(10)

# Close the browser
#driver.quit()

# Load the CSV file
df = pd.read_csv(file_path)

# Remove rows with "View Contents" in the "Details" column
df = df[df['Details'] != 'View Contents']

# Use Selenium to scrape the links
#driver = webdriver.Firefox(options=options)
#driver.get("https://afttransshipmenthub-na.aka.amazon.com/SWF2/view-transfers/inbound/")

# Wait for the table to load and get the links
wait = WebDriverWait(driver, 10)
table = wait.until(EC.visibility_of_element_located((By.ID, "inboundTransfersTable")))
links = table.find_elements(By.XPATH, "//a[contains(@href, 'stowing-in-progress')]")

stowing_links = [link.get_attribute('href') for link in links]

# Add the "Units For Reconcile" column
df['Units For Reconcile'] = ''

for link in stowing_links:
    driver.get(link)
    wait = WebDriverWait(driver, 60)
    
    try:
        load_id_element = wait.until(EC.visibility_of_element_located((By.ID, 'loadId')))
        load_id = load_id_element.text
        quantity_element = wait.until(EC.visibility_of_element_located((By.ID, 'quantityItemsReconcile')))
        quantity = quantity_element.text
        
        # Update the CSV file
        df.loc[df['Load ID'] == load_id, 'Units For Reconcile'] = quantity
    except Exception as e:
        print(f"Error processing link {link}: {e}")

# Close the browser
driver.quit()

# Save the updated CSV file
df.to_csv(file_path, index=False)