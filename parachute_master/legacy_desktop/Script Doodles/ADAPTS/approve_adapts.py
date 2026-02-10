from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Read manager logins from the file
with open('managers.txt', 'r') as file:
    manager_list = file.read().splitlines()

# Initialize the web driver (make sure the driver is installed and in your PATH)
driver = webdriver.Firefox()
driver.get('https://adapt-iad.amazon.com/')
time.sleep(20)

for manager in manager_list:
    # Navigate to the specific URL for each manager
    driver.get(f'https://adapt-iad.amazon.com/#/employee-dashboard/{manager}')
    

    # Wait for the checkbox to be present and then click it
    try:
        checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="checkbox"]'))
        )
        if not checkbox.is_selected():
            checkbox.click()

        # Click the 'Approve feedback' button
        approve_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Approve feedback")]'))
        )

        time.sleep(10)

        approve_button.click()
    except Exception as e:
        print(f"An error occurred with manager {manager}: {e}")

# Close the browser once done
driver.quit()
