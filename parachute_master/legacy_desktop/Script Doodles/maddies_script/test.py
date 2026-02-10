import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time, csv, os

# Setup Selenium
options = Options()
driver = webdriver.Firefox(options=options)
driver.get("https://atoz.amazon.work/")
time.sleep(20)  # Manual login

# Go to target page
driver.get("https://fcquality.amazon.com/inventory_adjustments/large_adjustment_list?utf8=%E2%9C%93&start_date=2024-01-01&end_date=2025-12-31&warehouse_id=SWF2&research_status=&search_asin=&delinquent_status=&topmenu_selection=SOX&commit=Apply+Filter")
time.sleep(5)

# Pull cookies from the Selenium session
selenium_cookies = driver.get_cookies()
cookie_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

# Grab user-agent
user_agent = driver.execute_script("return navigator.userAgent;")

# Get all AJAX hrefs using BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
ajax_links = [
    "https://fcquality.amazon.com" + a["href"]
    for a in soup.select("a[data-remote='true'][href*='large_adjustment_line_item_detail']")
]

driver.quit()  # Done with browser

# Set up a requests session
session = requests.Session()
session.headers.update({"User-Agent": user_agent})
session.cookies.update(cookie_dict)

# Extract data
table_data = []

for i, url in enumerate(ajax_links):
    try:
        res = session.get(url)
        res.raise_for_status()

        detail_soup = BeautifulSoup(res.text, "html.parser")

        # Extract your target data
        active_row = detail_soup.select_one("tr.active")
        if not active_row:
            print(f"Missing active row for URL {url}")
            continue

        row_data = [td.get_text(strip=True) for td in active_row.select("td")]

        note_input = detail_soup.select_one("#research_fields_81")
        note = note_input.get("value", "").strip() if note_input else ""
        row_data.append(note)

        table_data.append(row_data)

    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Output
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "LargeAdjustmentData.csv")

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(table_data)
