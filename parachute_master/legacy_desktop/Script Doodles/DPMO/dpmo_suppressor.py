import time
import logging
import threading
import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(filename='dpmo_suppressor.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Global driver variable
options = Options()
options.add_argument("--headless")  # Uncomment if you want headless mode
driver = webdriver.Firefox(options=options)
authorized = False
first_link = True

def get_user_input():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    username = simpledialog.askstring("Input", "Enter your Amazon username:")
    pin = simpledialog.askstring("Input", "Enter your security key PIN:", show='*')
    
    root.destroy()  # Destroy the root window after input
    return username, pin

def do_auth():
    global authorized, driver, first_link

    #Reset first_link
    first_link = True

    # Restart the driver to refresh auth
    driver.close()

    # Get username and PIN from CLI
    username, pin = get_user_input()

    # Set up WebDriver
    options = Options()
    #options.add_argument("--headless")  # Uncomment if you want headless mode
    driver = webdriver.Firefox(options=options)

    # Navigate to the login page
    driver.get("https://atoz.amazon.work/home")

    # Wait for the username field to be visible and enter the username
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "user_name_field")))
    username_field = driver.find_element(By.ID, "user_name_field")
    username_field.send_keys(username + Keys.ENTER)

    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "password_field")))
    password_field = driver.find_element(By.ID, "password_field")
    password_field.send_keys(pin + Keys.ENTER)

    # Wait for the security key prompt
    time.sleep(15)

    # Mark authorized
    authorized = True

def wait_and_set_authorized():
    global authorized

    time.sleep(18000)  # Wait 5 hours (18000 seconds)
    authorized = False
    logging.info("Waiting another 5 hours to authorize.")

def fix_item_not_on_po(pid):
    global first_link

    # Implement the function to fix the item not on PO
    logging.info(f"Fixing item not on PO for PID {pid}")
    # Your implementation here
    try:

        # Navigate to the specified URL
        driver.get("https://tunnel-insights-na.aka.amazon.com/en_US/pid/search")


        # Select the warehouse option 'SWF2'
        warehouse_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'warehouseId')))
        Select(warehouse_select).select_by_value('SWF2')

        # Wait for the device dropdown to be present and then select the device option 'PID-{pid}'
        device_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'deviceId')))
        time.sleep(5)
        Select(device_select).select_by_value(f'PID-{pid}')

        # Click the search button
        search_button = driver.find_element(By.ID, 'search-button')
        search_button.click()

        # Wait for the dropdown to be present and then select '100' from the dropdown to show 100 results
        results_length_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'search-results-table_length')))
        Select(results_length_select).select_by_value('100')

        # Pause for 5 seconds to allow for the next steps
        time.sleep(5)

        # Scrape all links and iterate through them
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            if 'http://fcresearch-na.aka.amazon.com' in link['href']:
                #driver.execute_script("window.open('');")
                #driver.switch_to.window(driver.window_handles[-1])
                driver.get(link['href'])

                if first_link:
                    # Handle authentication
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, 'Switch to secure sign in (w)'))
                    ).click()
                    
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'badgeBarcodeId'))
                    ).send_keys("308321" + Keys.ENTER)
                    
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'password'))
                    ).send_keys("L6pr0m0!" + Keys.ENTER)
                    
                    driver.find_element(By.ID, 'password').send_keys("\n")

                    first_link = False
                
                # Wait for the page to load
                time.sleep(5)
                
                # Find and print the necessary information
                failure_reason = driver.find_elements(By.XPATH, "//th[contains(text(), 'Failure Reason')]/following-sibling::td")
                if failure_reason:
                    failure_reason_text = failure_reason[0].text
                    if 'ITEMS_NOT_ON_PO' in failure_reason_text:
                        shipment_number = driver.find_element(By.XPATH, "//th[contains(text(), 'Shipment')]/following-sibling::td/a").text
                        freight_labels = driver.find_element(By.XPATH, "//th[contains(text(), 'FREIGHT_LABEL')]/following-sibling::td").text
                        
                        logging.info(f'FC Research Link: {link}')
                        logging.info(f'Shipment Number: {shipment_number}')
                        logging.info(f'Freight Labels: {freight_labels}')
                        
                        #insert new code here

                        break

                # Close the current tab
                #driver.close()
                #driver.switch_to.window(driver.window_handles[0])

    finally:
        # Ensure the browser is closed in case of an error
        #driver.quit()
        logging.info("Had to do something here.")

def check_item_not_on_po():
    logging.info("Checking for item not on PO")
    
    general_monitor_url = "https://monitorportal.amazon.com/monitors/overview?id=us-east-1:SWF2_INOPO_1_Min"
    driver.get(general_monitor_url)
    
    try:
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "alarmstatus")))
        alarm_status = driver.find_element(By.ID, "alarmstatus").text
        
        logging.info("Found monitor - checking Alarm status.")
        if "Alarm is not OK" in alarm_status:
            logging.info("STATUS: INOPO ALARMING")
            for pid in range(1, 7):
                logging.info(f"Checking PID {pid}")
                pid_monitor_url = f"https://monitorportal.amazon.com/monitors/overview?id=us-east-1:SWF2_INOPO_1_Min_PID{pid}"
                driver.get(pid_monitor_url)
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "alarmstatus")))
                pid_alarm_status = driver.find_element(By.ID, "alarmstatus").text
                if "Alarm is not OK" in pid_alarm_status:
                    logging.info(f"PID {pid} is alarming. Fixing item not on PO.")
                    fix_item_not_on_po(pid)
                else:
                    logging.info(f"PID {pid} is not alarming.")
        else:
            logging.info("STATUS: INOPO NOT ALARMING")
    
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Error while checking item not on PO: {e}")

def main():
    logging.info("Starting DPMO Suppressor")
    while True:
        if not authorized:
            do_auth()
            wait_thread = threading.Thread(target=wait_and_set_authorized)
            wait_thread.start()

        check_item_not_on_po()
        time.sleep(60)  # Run the check_item_not_on_po function every 60 seconds

if __name__ == "__main__":
    main()
