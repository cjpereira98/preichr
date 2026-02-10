import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By

# Load logins from file
with open('logins.txt', 'r') as file:
    logins = file.read().splitlines()

# Calculate the number of fails
num_fails = random.randint(int(len(logins) * 0.6), int(len(logins) * 0.9))

# Set up the WebDriver
driver = webdriver.Chrome()  # Or use another driver for a different browser

# Navigate to the URL
driver.get('https://durable.corp.amazon.com/SWF2/simba/')
time.sleep(20)  # Wait for manual authentication

for login in logins:
    # Click the 'New Audit' button
    driver.find_element(By.CSS_SELECTOR, 'a.btn.btn-primary.simba-nav-btn[href="/SWF2/simba/audits/new_audit"]').click()

    # Enter the login
    driver.find_element(By.ID, 'audited_login').send_keys(login)

    if num_fails > 0:
        # Click 'At Risk' and 'FHD' buttons
        driver.find_element(By.ID, 'risk-btn').click()
        driver.find_element(By.XPATH, "//button[contains(text(), 'FHD')]").click()

        # Randomly click one of the specified category buttons
        categories = ["Fluid Loading/Unloading", "Body Mechanics"]
        chosen_category = random.choice(categories)
        driver.find_element(By.XPATH, f"//button[text()='{chosen_category}']").click()

        # Click a failure code button based on the chosen category
        if chosen_category == 'Fluid Loading/Unloading':
            # Your buttons for Fluid Loading/Unloading seem identical. Adjust as necessary.
            fluid_failures = ["Failure to use stepladder when needed", "Failure to use stepladder when needed"]
            chosen_failure = random.choice(fluid_failures)
            driver.find_element(By.XPATH, f"//button[contains(text(), '{chosen_failure}')]").click()
        else:
            # Choose randomly from the Body Mechanics failure codes
            mechanics_failures = ["Awkward postures used", "Lifting with back / bending at the waist", 
                                  "Not lifting by corners / Inadequate C-grip", "Not testing the weight"]
            chosen_failure = random.choice(mechanics_failures)
            driver.find_element(By.XPATH, f"//button[contains(text(), '{chosen_failure}')]").click()

        # Click the department button and 'Coached'
        # Click the department button and 'Coached'
        driver.find_element(By.XPATH, "//button[contains(text(), 'IB Line Loader (PMT)')]").click()
        driver.find_element(By.XPATH, "//button[contains(text(), 'Coached')]").click()

        # Decrement fails
        num_fails -= 1
    else:
        # If not fails, follow the else part logic
        # Click 'At Risk' and 'FHD' buttons
        driver.find_element(By.ID, 'safe-btn').click()
        driver.find_element(By.XPATH, "//button[contains(text(), 'FHD')]").click()

        # Randomly click one of the specified category buttons
        categories = ["Fluid Loading/Unloading", "Body Mechanics"]
        chosen_category = random.choice(categories)
        driver.find_element(By.XPATH, f"//button[text()='{chosen_category}']").click()

        driver.find_element(By.XPATH, "//button[contains(text(), 'IB Line Loader (PMT)')]").click()


    # Click the 'Submit' button
    driver.find_element(By.ID, 'nextBtn').click()

    # Add a pause or wait for the page to reload if necessary

driver.quit()

