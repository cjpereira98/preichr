# retrieve LA data from fcquality

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time, csv, os

# Launch Firefox for manual authentication
print("Launching Firefox for Midway auth... you have 20 seconds.")
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", os.getcwd())
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
driver = webdriver.Firefox(options=options)
driver.get("https://atoz.amazon.work/")

time.sleep(20)  # Wait for manual login and cert push

print("Auth window complete. Continuing...")
driver.get("https://fcquality.amazon.com/inventory_adjustments/large_adjustment_list?utf8=%E2%9C%93&start_date=2025-08-03&end_date=2025-12-31&warehouse_id=SWF2&research_status=&search_asin=&delinquent_status=&topmenu_selection=SOX&commit=Apply+Filter")
time.sleep(3)

driver.execute_script("document.body.style.zoom='30%'")

rows = driver.find_elements(By.CSS_SELECTOR, "tr.even, tr.odd")
table_data = []

for i in range(len(rows)):
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.even, tr.odd")
    row = rows[i]
    asin = row.find_element(By.TAG_NAME, "td")
    try:
        asin.click()
    except Exception as e:
        print(f"Error clicking row {i}: {e}")
        time.sleep(10)
        asin = row.find_element(By.TAG_NAME, "td")
        asin.click()
    time.sleep(1)

#time.sleep(30)

active_rows = driver.find_elements(By.CSS_SELECTOR, "tr.active")

for i in range(len(active_rows)):

    active_row = active_rows[i]
    cells = active_row.find_elements(By.TAG_NAME, "td")
    row_data = [cell.text.strip() for cell in cells]

    note = driver.find_element(By.ID, "research_fields_81").get_attribute("value").strip()
    row_data.append(note)
    table_data.append(row_data)

# Export to CSV
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "LargeAdjustmentData.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(table_data)

driver.quit()
