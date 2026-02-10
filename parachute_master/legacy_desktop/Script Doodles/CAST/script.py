import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load the CSV file without headers
df = pd.read_csv('needs_cast.csv', header=None)

# Add a new column to the dataframe for the badge numbers
df[1] = ""

# Setup Selenium with Firefox
options = webdriver.FirefoxOptions()
#options.add_argument('--headless')  # Run in headless mode, remove this if you want to see the browser
driver = webdriver.Firefox(options=options)

try:
    # Navigate to the URL
    print("Navigating to the URL...")
    driver.get('https://fclm-portal.amazon.com/reports/processPathRollup?warehouseId=SWF2')

    # Wait for user to authenticate (20 seconds)
    print("Waiting for authentication...")
    time.sleep(20)
    print("Authentication wait time over, proceeding with data extraction...")

    for index, row in df.iterrows():
        employee_id = row[0]  # Assuming the existing column with employee IDs is index 0

        print(f"Processing employee ID: {employee_id}")

        # Wait until the employee search input is visible
        search_input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, 'navEmployeeSearch'))
        )
        
        # Enter the employee ID into the search input
        search_input.clear()
        search_input.send_keys(employee_id)
        print(f"Entered employee ID: {employee_id}")

        # Click the search button
        search_button = driver.find_element(By.CSS_SELECTOR, 'input.fcpn-search-click.fcpn-sprite')
        search_button.click()
        print("Clicked the search button")

        # Wait until the badge number is visible in the employee details section
        badge_number_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//dt[text()='Badge']/following-sibling::dd"))
        )

        # Extract the badge number
        badge_number = badge_number_element.text
        print(f"Extracted badge number: {badge_number}")

        # Insert the badge number into the new column (index 1) of the dataframe
        df.at[index, 1] = badge_number

finally:
    # Save the updated dataframe back to the CSV file with two columns
    df.to_csv('needs_cast.csv', index=False, header=False)
    print("Updated CSV file saved with two columns.")

    # Close the browser
    driver.quit()
    print("Browser closed.")
