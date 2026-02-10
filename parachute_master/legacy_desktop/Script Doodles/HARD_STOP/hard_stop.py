from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


# Firefox profile, if needed, for authentication purposes
#firefox_profile = webdriver.FirefoxProfile()

# Set up the Firefox driver
driver = webdriver.Firefox()

# Function to clear the contents of badges.txt
def clear_badges_file():
    open('badges.txt', 'w').close()

# Function to append a badge ID to badges.txt
def append_badge_to_file(badge_id):
    with open('badges.txt', 'a') as file:
        file.write(f"{badge_id}\n")

# Read employees from employees.txt
with open('employees.txt', 'r') as file:
    employee_ids = file.readlines()

# Clear badges.txt content
clear_badges_file()

# Iterate over each employee
for employee_id in employee_ids:
    employee_id = employee_id.strip()
    # Navigate to the employee time details page
    driver.get(f'https://fclm-portal.amazon.com/employee/timeDetails?warehouseId=SWF2&employeeId={employee_id}')
    
    # Wait for the page to load the element
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'td.title span.fold-control'))
        WebDriverWait(driver, 10).until(element_present)
        
        # Extract login from the text
        element = driver.find_element(By.CSS_SELECTOR, 'td.title span.fold-control')
        login = element.text.split('(')[-1].split(')')[0]
        
        # Navigate to the employee dashboard
        driver.get(f'https://adapt-iad.amazon.com/#/employee-dashboard/{login}')
        
        # Wait for the badge ID element to load
        badge_id_present = EC.presence_of_element_located((By.ID, 'employee-info-table-badgeId'))
        WebDriverWait(driver, 10).until(badge_id_present)
        
        # Extract and write the badge barcode ID to file
        badge_id = driver.find_element(By.ID, 'employee-info-table-badgeId').text
        append_badge_to_file(badge_id)
        
    except Exception as e:
        print(f"Error processing employee {employee_id}: {e}")

# Wait for manual authentication if needed
#sleep(20)

# Navigate to the fcmenu page
driver.get('http://fcmenu-iad-regionalized.corp.amazon.com/')


# Assume manual authentication has been completed here
sleep(10)

# Navigate to the labor tracking kiosk for a specific FC
driver.get('http://fcmenu-iad-regionalized.corp.amazon.com/SWF2/laborTrackingKiosk')

# Paste the "ISTOP" code into the indirect work code input and press enter
try:
    calm_code_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'calmCode'))
    )
    calm_code_input.send_keys('ISTOP')
    calm_code_input.send_keys(Keys.ENTER)
except Exception as e:
    print(f"Error entering calm code: {e}")

# Read the badge ids from badges.txt and interact with the page for each badge
try:
    with open('badges.txt', 'r') as file:
        badges = file.readlines()
    for badge in badges:
        print(badge)
        badge = badge.strip()
        print(badge)
        badge_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'trackingBadgeId'))
        )
        badge_input.clear()  # Clear the input field before sending new input
        badge_input.send_keys(badge)
        badge_input.send_keys(Keys.ENTER)
        sleep(1)  # Wait a moment for the page to process the badge entry
except Exception as e:
    print(f"Error processing badges: {e}")

sleep(20)
# Remember to close the driver at the end of your script
driver.quit()
