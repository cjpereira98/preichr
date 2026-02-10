import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


def run_scrape():
    
    

    #Wait for the tables to load
    time.sleep(5)
    all_tables = wait.until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "react-grid-item")
        )
    )

    if len(all_tables) >= 8:
        #find the 8th table for Pallet Barcodes Bypass (non-FBA)
        target_table = all_tables[7] 
        print("Scrolling to the 8th table...")
        target_table.location_once_scrolled_into_view  # Scrolls the table into view so it will load
        time.sleep(20)  # Allow time for content to load

        #Look at all of the table rows
        data_elements = target_table.find_elements(By.CLASS_NAME, "body-row")

        #Grab the 3rd and 4th cells in the row
        for e in data_elements:
            cells = e.find_elements(By.CLASS_NAME, "Grid__cell")
            userID = cells[2].text.strip()
            pallet_bypass_count = cells[3].text.strip()

            #Instead of this, need to add to a list if the pallet bypass count is greater than 0
            print(f"User ID: {userID}, Pallet Bypass Count: {pallet_bypass_count}")
        
    else:
        print("Unable to find the table.")

    #Send to CES Client here


# Main 

# Setup the Firefox WebDriver
options = Options()
options.headless = False  # Set to True for headless mode, can't authenticate in headless mode
driver = webdriver.Firefox(options=options)
driver.maximize_window()


try:
    print("Starting scrape")
    #Navigate to the CloudWatch dashboard URL
    url = "https://cw-dashboards.aka.amazon.com/cloudwatch/dashboardInternal?accountId=353718705239&awsPartition=aws&name=Process_Path_Automation_Metrics&state=%2Fcloudwatch%2FdashboardInternal%3FaccountId%3D353718705239%26awsPartition%3Daws%26name%3DProcess_Path_Automation_Metrics#dashboards/dashboard/Process_Path_Automation_Metrics"
    driver.get(url)

    #Wait for 20 seconds to allow for authentication
    print("Waiting for authentication...")
    time.sleep(20)

    #Define wait
    wait = WebDriverWait(driver, 30)

    #Click the "Custom" button to set the time range
    custom_button = driver.find_element(By.XPATH, "//span[@class='awsui_content_vjswe_lssc8_153 awsui_label_1f1d4_ocied_5'][.//span[normalize-space(text())='Custom']]")
    custom_button.click()
    time.sleep(2)
    #Set the time range to 5 minutes
    fiv_min_button = driver.find_element(By.XPATH, "//button[@data-testid='date-time-range-relative-option-300000']")
    fiv_min_button.click()

    while True:
        run_scrape()

        print("Task completed. Sleeping for 5 minutes...")

        time.sleep(300)  # Wait for 5 minutes before next scrape

        
        #refresh
        refresh_button = driver.find_element(By.XPATH, "//button[@data-test-id='refresh-dashboard-button']")
        refresh_button.click()

        
except Exception as e:
    print(f"An error occurred in the main loop: {e}")
    
    
