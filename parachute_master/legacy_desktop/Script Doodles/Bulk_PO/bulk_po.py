from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the web application
driver.get("https://aft-carton-preditor-app-iad.iad.proxy.amazon.com/wf?version=moveOut")

# Wait for authentication (adjust the sleep duration as needed)
time.sleep(20)

driver.get("https://aft-carton-preditor-app-iad.iad.proxy.amazon.com/wf?version=moveOut")

# Read purchase orders from po.txt
with open('po.txt', 'r') as po_file:
    purchase_orders = [line.strip() for line in po_file.readlines()]

# Read frx from frx.txt
with open('frx.txt', 'r') as frx_file:
    frx = frx_file.readline().strip()

# Function to execute JavaScript for scanning
def scan_item(barcode_data, symbology_type="Code128", timestamp="2024-06-26T12:00:00Z"):
    js_command = f"receivedScanDelayWrapper('{barcode_data}', '{symbology_type}', '{timestamp}')"
    driver.execute_script(js_command)

# Scan the frx into the page
scan_item(frx)

# Scan each purchase order into the page
for po in purchase_orders:
    scan_item(po)

# Send the enter key (you may need to adjust this if there's a specific element to focus on before sending the key)
body = driver.find_element(By.TAG_NAME, 'body')
body.send_keys(Keys.ENTER)

# Pause for 10 seconds to verify success
time.sleep(10)

# Close the WebDriver
driver.quit()
