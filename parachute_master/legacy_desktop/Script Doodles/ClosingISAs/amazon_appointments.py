from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load the list of appointment numbers from the file
with open('appointments.txt', 'r') as file:
    appointment_numbers = [line.strip() for line in file]

# Setup the Firefox driver
options = webdriver.FirefoxOptions()
options.add_argument('--start-maximized')
driver = webdriver.Firefox(options=options)

try:
    # Navigate to the initial authentication page
    driver.get('https://atoz.amazon.work/')
    
    # Wait for 20 seconds to allow for manual authentication
    time.sleep(40)

    # Loop through each appointment number and perform the specified actions
    for appointment_number in appointment_numbers:
        try:
            url = f'https://fc-inbound-dock-hub-na.aka.amazon.com/en_US/#/dockmaster/appointment/SWF2/view/{appointment_number}/appointmentDetail'
            driver.get(url)
            
            #so I can see where it is crashing
            print(appointment_number)

            # Wait for the page to load
            time.sleep(5)

            for _ in range(5):
                # Click the first button
                #button1 = driver.find_element(By.CSS_SELECTOR, 'button[data-target="#nextStatusModal"]')
                button1 = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@data-target="#nextStatusModal"]'))
                )

                button1.click()
                
                # Wait for the modal to appear
                time.sleep(1)
                
                # Click the Confirm button
                button2 = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="nextStatusModal"]//button[contains(text(), "Confirm")]'))
                )
                button2.click()
                
                # Wait between each click sequence
                #time.sleep(2)
            
            # Optionally wait a bit before moving to the next appointment
            time.sleep(1)
        except Exception as e:
            print(f'Error processing appointment number {appointment_number}: {e}')
            continue

finally:
    # Close the browser
    driver.quit()
