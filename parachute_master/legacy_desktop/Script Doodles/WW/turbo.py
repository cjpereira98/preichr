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

def batch_process(driver, badges, instructor_badge):
    """Process badges until there are 9 successful entries."""
    success_count = 0
    badge_index = 0
    total_badges = len(badges)
    success_badges = []

    while badge_index < total_badges:

        while badge_index < total_badges:
            badge = badges[badge_index]
            badge_input = driver.find_element(By.CLASS_NAME, "styles_badgeIdInput__1_cPx")
            badge_input.clear()
            badge_input.send_keys(badge + Keys.ENTER)
            
            try:
                # Wait for 1 second to see if the close button appears
                close_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "styles_closePopupX__1zIcr"))
                )
                close_button.click()
            except:
                # No close button appeared, increment success count
                print(badge)
                success_badges.append(badge)
                success_count += 1
                if success_count == 9:
                    break
            
            badge_index += 1
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "styles_badgeIdInput__1_cPx")))

        if success_count > 0:
            success_count = 0

            # Perform actions after all badges in the batch are entered
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_endScan__2Zfnq"))
            ).click()
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_startVideo__3UbuI"))
            ).click()
            
            # Select English-US-ASL
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "locale-list"))
            )
            select = driver.find_element(By.NAME, "locale-list")
            for option in select.find_elements(By.TAG_NAME, 'option'):
                if option.text == 'English-US-ASL':
                    option.click()
                    break
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_startVideo__2n1wc"))
            ).click()
            
            # Enable end button
            #WebDriverWait(driver, 10).until(
            #    EC.element_to_be_clickable((By.ID, "endButton"))
            #)
            driver.execute_script("document.getElementById('endButton').disabled = false;")
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "endButton"))
            ).click()
            
            print(success_badges)

            # Re-enter badges for training credit
            for badge in success_badges:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "styles_badgeIdInput__3pblF"))).send_keys(badge + Keys.ENTER)
                time.sleep(1)
                #badge_input_credit.clear()
                #badge_input_credit.send_keys(badge + Keys.ENTER)
                

            success_badges = []
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_endScan__1vuE3"))
            ).click()
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_goHomeButton__1a6b_"))
            ).click()
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_clickHuddleButton___fODU"))
            ).click()
        else:
            print("Not enough successful entries. Only {} successful entries were recorded.".format(success_count))


def main(instructor_badge_number):   
    # Selenium WebDriver setup
    options = Options()
    options.headless = True  # Change to False if you want to see the browser
    driver = webdriver.Firefox(options=options)

    try:
        # Fetch badge numbers
        badge_numbers = [num for num in open("turbo_huddle_config.txt").read().split()]

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
