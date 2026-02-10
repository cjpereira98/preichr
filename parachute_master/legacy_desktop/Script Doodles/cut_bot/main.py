import json
import requests
import csv
import time
import os
from selenium import webdriver
#from seleniumwire import webdriver as selenium_wire_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import glob
from datetime import datetime

# CONTROLS
# test mode
test_mode = False  # Set to True for testing, will slow down execution

# slackbot url
SLACKBOT_URL = "https://hooks.slack.com/triggers/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"

# glidepath factor
#NEO_QUERY_SPEED = 0.1  # seconds to wait between NEO API requests

# sites
SITES = {"GYR3", "IND9", "LAS1", "LAX9", "MEM1", "MQJ1", "SMF3", "TEB9", "FWA4",
         "GYR2", "IAH3", "ORF2", "RDU2", "RFD2", "RMN3", "SBD1", "SCK4", "SWF2", "VGT2", "ABE8", "AVP1", "FTW1", "CLT2", "ONT8", "LGB8", "MDW2"}


# helpers

def create_sites_dict():
    """
    Creates a dictionary of sites with their respective staffing data.
    """
    sites_dict = {}
    for site in SITES:
        sites_dict[site] = {
            "total_trailers": 0,
            "future_trailers": 0,
            "cut_pct": 0.0,
        }
    return sites_dict

def pull_qs_data(sites_dict, driver):
    """
    Downloads csv from the cut qs with compliance data about all of the trailers in current day.
    """

    driver.get("https://us-east-1.quicksight.aws.amazon.com/sn/account/amazonbi/dashboards/95cdd446-9da1-41b1-b8ed-5f31d2a7f265/sheets/95cdd446-9da1-41b1-b8ed-5f31d2a7f265_634e79c4-8894-4af4-a34b-3f5d4f2fe7b8")  # Ensure you're logged in

    time.sleep(5)

    driver.execute_script("document.body.style.zoom='50%'")

    # Wait for the element to be clickable
    filters = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id="sheet-control-panel-toggle-expand"]'))
    )

    # Click it
    filters.click()

    time.sleep(1)

    # date_picker_0
    #date_picker = driver.find_element(By.CSS_SELECTOR, '[data-automation-id="date-picker-0"]')
    date_picker = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id="date_picker_0"]'))
    )
    date_value = date_picker.get_attribute("value")
    today_str = datetime.today().strftime("%Y/%m/%d")
    if date_value == today_str:
        pass
    else:
        date_picker.click()
        time.sleep(1)

        # aria-label="Choose August 7, 2025 as your date"

        # aria-label="View next month." 
        #this is broken if the correct date is already selected
        formatted_date = datetime.now(ZoneInfo("America/Chicago")).strftime("%B %#d, %Y")
        css_selector = f'button[aria-label="Choose {formatted_date} as your date"]'
        date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        date_button.click()
        time.sleep(1)

        # close the date menu
        #date_picker = WebDriverWait(driver, 10).until(
        #    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id="date_picker_0"]'))
        #)
        #date_picker.click()
        #time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body")
        ActionChains(driver).move_to_element(body).click().perform()
        time.sleep(1)

    

    # date_picker_0 <- going to probably be the second one
    date_pickers = driver.find_elements(By.CSS_SELECTOR, '[data-automation-id="date_picker_0"]')
    date_value = date_pickers[1].get_attribute("value")
    if date_value == today_str:
        pass
    else:
        date_pickers[1].click()
        time.sleep(1)

        # follow the same pattern to select the date
        date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        date_button.click()
        time.sleep(1)

        #close the date menu

        body = driver.find_element(By.TAG_NAME, "body")
        ActionChains(driver).move_to_element(body).click().perform()
        time.sleep(1)

    # hover over the correct table
    table = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-automation-context="PIVOT_TABLE - 2.1 CUT Compliance Daily Summary"]'))
    )
    ActionChains(driver).move_to_element(table).perform()
    time.sleep(1)


    # analysis_visual_dropdown
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id="analysis_visual_dropdown_menu_button"]'))
    )
    dropdown.click()
    time.sleep(1)

    # dashboard_visual_dropdown_export
    export_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id="dashboard_visual_dropdown_export"]'))
    )
    export_button.click()
    time.sleep(5)

    

    # pull the file from the downloads folder into a pandas df
    df = pd.read_csv(glob.glob("2.1*.csv")[0])
    os.remove(glob.glob("2.1*.csv")[0])

    #df["wa"]
    df.columns = df.columns.str.strip()  # Strip whitespace from column names
    
    for site in sites_dict:
        #if the site exists in the df, grab the total trailers from "2. Total Processed" and the future trailers from "4. Future Due Trailers Processed"
        if site in df["warehouse_id"].values:
            total = int(df.loc[df["warehouse_id"] == site, "2. Total Processed"].values[0])
            future = int(df.loc[df["warehouse_id"] == site, "4. Future Due Trailers Processed"].values[0])
            sites_dict[site]["total_trailers"] = total
            sites_dict[site]["future_trailers"] = future
            sites_dict[site]["cut_pct"] = ((total-future)/total) if total > 0 else 0.0
        
        else:
            sites_dict[site]["total_trailers"] = 0
            sites_dict[site]["future_trailers"] = 0



    return sites_dict  


def format_slack_message(sites_dict):
    """
    Formats the final Slack message with a table of trailer counts and CUT %.
    CUT % = (total - future) / total
    """
    header = f"{'Site':<6} {'Total':>8} {'Future':>8} {'CUT %':>8}"
    lines = [header, "-" * len(header)]

    # Sort by cut_pct descending; tie-breaker by Total desc to surface volume
    rows = sorted(
        sites_dict.items(),
        key=lambda kv: (kv[1].get("cut_pct", 0.0), kv[1].get("total_trailers", 0)),
        reverse=True
    )

    # Build table rows
    for site, data in rows:
        total = data["total_trailers"]
        future = data["future_trailers"]

        # Handle divide by zero
        cut_pct = data.get("cut_pct",0.0)*100.0

        line = (
            f"{site:<6} "
            f"{total:>8} "
            f"{future:>8} "
            f"{cut_pct:>7.1f}%"
        )
        lines.append(line)

    message = "\n".join(lines)

    return {
        "text": message
    }


# main

def main():

    # Launch browser for manual authentication
    print("Launching Firefox for Midway auth... you have 20 seconds.")
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.getcwd())
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    driver = webdriver.Firefox(options=options)
    driver.get("https://atoz.amazon.work/")  # Or the exact URL you want to pre-auth

    #time.sleep(7200)
    time.sleep(45)  # Wait for manual login and cert push
    print("Auth window complete. Continuing...")

    sites_dict = create_sites_dict()

    #update_goals(sites_dict, driver)
    
    #hourly update
    while True:

        #if (datetime.now().hour > 9 and datetime.now().hour <14) or (datetime.now().hour > 21) or datetime.now().hour < 2:
            #update_goals(sites_dict, driver)
        #sites_dict = get_shift_goals(sites_dict)
        #sites_dict = calculate_recommended_staffing(sites_dict)
        #sites_dict = apply_glidepath(sites_dict)

        #while (datetime.now().minute < 41):
        #    time.sleep(60)
        sites_dict = pull_qs_data(sites_dict, driver)
        #sites_dict = pull_tot(sites_dict, driver)
        #sites_dict = calculate_deltas(sites_dict)
        print(sites_dict)
        #time.sleep(100000000)
        
        slack_payload = format_slack_message(sites_dict)

        #while (datetime.now().minute > 10):
        #    time.sleep(60)

        response = requests.post(SLACKBOT_URL, json=slack_payload)
        if response.status_code != 200:
            print(f"Slack post failed with status code {response.status_code}: {response.text}")
        else:
            print("Slack message sent successfully.")

        # Sleep for an hour before the next update
        #time.sleep(3600)
        time.sleep(3600)
        driver.get("https://atoz.amazon.work/")
        time.sleep(10)



if __name__ == "__main__":
    main()
