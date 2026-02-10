#Master code for completing all on prem working wells when shown at start up
#Run with the accompanying .csv file only containing the login of the manager of the AAs as the first item and the badge id of the manager getting huddle credit as the second item

import sys
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def read_logins_from_csv(filename):
    """Read logins from a CSV file into a list of strings."""
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        return [row for row in reader]

def batch_process(driver, badges, instructor_badge):
    """Process badges in batches of up to 9."""
    for i in range(0, len(badges), 9):
        batch = badges[i:i + 9]
        
        # Process each badge in the batch
        for badge in batch:
            badge_input = driver.find_element(By.CLASS_NAME, "styles_badgeIdInput__1_cPx")
            badge_input.clear()
            badge_input.send_keys(badge + Keys.ENTER)
            time.sleep(1)  # Adjust based on actual page responsiveness
        
        # Perform actions after all badges in the batch are entered
        time.sleep(1)
        driver.find_element(By.CLASS_NAME, "styles_endScan__2Zfnq").click()
        time.sleep(1)
        driver.find_element(By.CLASS_NAME, "styles_startVideo__3UbuI").click()
        
        # Select English-US-ASL
        time.sleep(3)
        select = driver.find_element(By.NAME, "locale-list")
        for option in select.find_elements(By.TAG_NAME, 'option'):
            if option.text == 'English-US-ASL':
                option.click()
                break
        
        time.sleep(3)
        driver.find_element(By.CLASS_NAME, "styles_startVideo__2n1wc").click()
        
        time.sleep(3)
        # This script line might not work directly in Selenium without executing JavaScript
        driver.execute_script("document.getElementById('endButton').disabled = false;")
        
        time.sleep(3)
        driver.find_element(By.ID, "endButton").click()
        
        # Re-enter badges for training credit
        for badge in batch:
            badge_input_credit = driver.find_element(By.CLASS_NAME, "styles_badgeIdInput__3pblF")
            badge_input_credit.clear()
            badge_input_credit.send_keys(badge + Keys.ENTER)
            time.sleep(1)  # Adjust based on actual page responsiveness
        
        driver.find_element(By.CLASS_NAME, "styles_endScan__1vuE3").click()
        time.sleep(5)
        driver.find_element(By.CLASS_NAME, "styles_goHomeButton__1a6b_").click()
        time.sleep(1)  # Adjust based on actual page responsiveness
        driver.find_element(By.CLASS_NAME, "styles_clickHuddleButton___fODU").click()
        time.sleep(1)

def fetch_badge_numbers(driver, logins):
    """For each login, fetch the corresponding badge number."""
    badge_numbers = []
    for login in logins:
        try:
            search_input = driver.find_element(By.ID, "navEmployeeSearch")
            search_input.clear()
            search_input.send_keys(login)
            search_input.send_keys(Keys.RETURN)
            time.sleep(5)  # wait for the search results to load
            badge_element = driver.find_element(By.XPATH, "//dt[text()='Badge']/following-sibling::dd")
            badge_numbers.append(badge_element.text)
        except NoSuchElementException:
            print(f"Failed to find badge for login: {login}")
            badge_numbers.append("Not found")
    return badge_numbers

def main(instructor_badge_number):
    # Read logins from CSV
    logins = read_logins_from_csv("ww_config.csv")

    # Selenium WebDriver setup
    options = Options()
    options.headless = True  # Change to False if you want to see the browser
    driver = webdriver.Firefox(options=options)
    
    try:
        # Navigate to the specified URL
        driver.get("https://fclm-portal.amazon.com/reports/processPathRollup?reportFormat=HTML&warehouseId=SWF2&maxIntradayDays=1&spanType=Intraday&startDateIntraday=2024%2F04%2F07&startHourIntraday=8&startMinuteIntraday=0&endDateIntraday=2024%2F04%2F07&endHourIntraday=8&endMinuteIntraday=15&_adjustPlanHours=on&_hideEmptyLineItems=on&employmentType=AllEmployees")
        time.sleep(20)
        
        # Fetch badge numbers
        badge_numbers = fetch_badge_numbers(driver, logins)

        # Print the list of badge numbers
        print(badge_numbers)
    finally:
        driver.get("https://central.prod.wellnesskiosk.whs.amazon.dev/")

        # Select SWF2 from the dropdown
        time.sleep(3)

        site_dropdown = driver.find_element(By.CLASS_NAME, "styles_siteDropDown__3YxOn")
        site_dropdown.send_keys("SWF2" + Keys.ENTER)

        # Input instructor badge number
        time.sleep(3)
        instructor_badge_input = driver.find_element(By.CLASS_NAME, "styles_badgeIdInput__3bOWb")
        instructor_badge_input.send_keys(instructor_badge_number + Keys.ENTER)
        
        # Click the Core-2024-HF (IXD) button
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "styles_clickHuddleButton___fODU"))).click()

        # Processing badges in batches
        batch_process(driver, badge_numbers, instructor_badge_number)

        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <instructor_badge_number>")
        sys.exit(1)
    instructor_badge_number = sys.argv[1]
    main(instructor_badge_number)
