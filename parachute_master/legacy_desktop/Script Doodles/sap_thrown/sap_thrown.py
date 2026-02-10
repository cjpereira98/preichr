import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


def run_task():
    
    # Step 1: Navigate to the CloudWatch dashboard URL
    url = "https://cw-dashboards.aka.amazon.com/cloudwatch/dashboardInternal?accountId=353718705239&awsPartition=aws&name=Process_Path_Automation_Metrics&state=%2Fcloudwatch%2FdashboardInternal%3FaccountId%3D353718705239%26awsPartition%3Daws%26name%3DProcess_Path_Automation_Metrics#dashboards/dashboard/Process_Path_Automation_Metrics"
    driver.get(url)

    # Step 2: Wait for 20 seconds to allow for authentication
    print("Waiting for authentication...")
    time.sleep(20)

    # Scroll to the bottom of the page
    #print("Scrolling to the bottom of the page...")
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #driver.execute_script("window.scrollBy(0, 500);")
    # Scroll down the page using keyboard actions
    #actions = ActionChains(driver)
    #actions.send_keys(Keys.PAGE_DOWN).perform()  # Scroll down one page
#time.sleep(1)  # Allow content to load
    #time.sleep(5)  # Allow time for any dynamic content to load

    # Step 3: Locate the input element and update its value
    wait = WebDriverWait(driver, 30)
    input_element = wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "awsui_input_2rhyz_6kb1z_149")
        )
    )
    input_element.clear()
    input_element.send_keys(f"warehouseId={warehouse}")
    input_element.send_keys(Keys.RETURN)
    print(f"Updated the input field with 'warehouseId={warehouse}'.")

    time.sleep(3)

    button = driver.find_element(By.XPATH, "//button[@aria-label='1 Hour']")
    button.click()
    print("Clicked the '1 Hour' button.")

    # Step 4: Locate the 26th table container
    time.sleep(10)  # Wait for the table to load
    all_tables = wait.until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "react-grid-item")
        )
    )

    if len(all_tables) >= 8:
        target_table = all_tables[7]  # 0-based index for the 26th occurrence
        print("Scrolling to the 8th table...")
        target_table.location_once_scrolled_into_view  # Scrolls the table into view
        time.sleep(20)  # Allow time for content to stabilize

        # Step 5: Find all "query-results-cell" elements inside the table
        data_elements = target_table.find_elements(By.CLASS_NAME, "body-row")

        for e in data_elements:
            cells = e.find_elements(By.CLASS_NAME, "Grid__cell")
            userID = cells[2].text.strip()
            pallet_bypass_count = cells[2].text.strip()

            print(f"User ID: {userID}, Pallet Bypass Count: {pallet_bypass_count}")
        
        #if len(data_elements) >= 6:
            # Extract the second occurrence
        #    data_value = data_elements[5].text.strip()  # Index 1 is the second element
        #    print(f"Extracted data value: {data_value}")

            # Step 6: Send the value to Slack
        #    slack_message = f"{data_value} SAP pallets were depalletized in the last 3 hours."
        #    slack_payload = {"image": slack_message}

        #    response = requests.post(slack_url, json=slack_payload)
        #    if response.status_code == 200:
        #        print("Message sent to Slack successfully!")
        #    else:
        #       print(f"Failed to send to Slack. Status code: {response.status_code}, Response: {response.text}")
        #else:
        #    print("The second 'query-results-cell' element was not found inside the table.")

    else:
        print("The 26th occurrence of the table was not found on the page.")


# Main loop to run every hour
# Setup variables
warehouse = "SWF2"
slack_url = "https://hooks.slack.com/triggers/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"  # Replace with your webhook URL

# Setup the Firefox WebDriver in headless mode
options = Options()
options.headless = False  # Set to True for headless mode
driver = webdriver.Firefox(options=options)

    

while True:
    try:
        print("Starting task...")
        run_task()
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")
    print("Task completed. Sleeping for 1 hour...")
    time.sleep(3600)  # Wait for 1 hour before the next run
