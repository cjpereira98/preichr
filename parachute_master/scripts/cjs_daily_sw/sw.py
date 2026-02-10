import os
import sys
import glob
import time
import schedule
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Add necessary directories to system path for importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from ampy.integrations.ppr import ProcessPathRollupIntegration
from ampy.integrations.firefox import FirefoxIntegration
from ampy.integrations.slack import SlackIntegration

from config.config import FC

# Constants
CHECK_FREQUENCY = 180  # in minutes

# File handling functions
def rename_downloaded_file(pattern, new_name):
    """
    Rename the first file matching the given pattern.
    """
    files = glob.glob(pattern)
    if files:
        os.rename(files[0], new_name)
        return new_name
    else:
        raise FileNotFoundError(f"No file matching pattern {pattern} found")

def clean_up_files(pattern):
    """
    Remove all files matching the given pattern.
    """
    files = glob.glob(pattern)
    for file in files:
        os.remove(file)

# Date and time utilities
def get_recent_min_window(min_delta):
    """
    Calculate a time window ending 30 minutes ago and round down to the nearest
    `min_delta` minute increment.
    """
    now = datetime.now()
    window_end = now - timedelta(minutes=30)
    window_start = window_end.replace(minute=(window_end.minute // min_delta) * min_delta, second=0, microsecond=0)
    window_end = window_start + timedelta(minutes=min_delta)
    return window_start, window_end

# Web scraping function
def download_flex_on_prem():
    """
    Download and return the flex on-prem employee data.
    """
    firefox_integration = FirefoxIntegration()
    driver = firefox_integration.get_authenticated_driver()

    # Get the time window for the request
    start_time, end_time = get_recent_min_window(CHECK_FREQUENCY)
    start_date_day = start_time.strftime("%Y%%2F%m%%2F%d")
    end_date_day = end_time.strftime("%Y%%2F%m%%2F%d")
    start_hour = start_time.strftime("%H")
    start_minute = start_time.strftime("%M")
    end_hour = end_time.strftime("%H")
    end_minute = end_time.strftime("%M")

    # Request URL for flex associates on premise
    ppr = ProcessPathRollupIntegration(driver)
    url = f"https://fclm-portal.amazon.com/reports/employeeAttendance?warehouseId={FC}&spanType=Intraday&reportFormat=HTML&maxIntradayDays=30&startDateDay={start_date_day}&startDateIntraday={start_date_day}&startHourIntraday={start_hour}&startMinuteIntraday={start_minute}&endDateIntraday={end_date_day}&endHourIntraday={end_hour}&endMinuteIntraday={end_minute}"
    ppr.get_flex_on_prem(url)

    # Rename and load the file
    flex_on_prem_pattern = f'employeeAttendance-{FC}-*.csv'
    flex_on_prem_file = rename_downloaded_file(flex_on_prem_pattern, 'flex_on_prem.csv')

    driver.quit()

    # Load the CSV data into a DataFrame
    flex_on_prem = pd.read_csv(flex_on_prem_file)

    # Clean up temporary files
    clean_up_files(flex_on_prem_pattern)
    if os.path.exists(flex_on_prem_file):
        os.remove(flex_on_prem_file)

    return flex_on_prem

# Slack communication function
def send_to_slack(payload_content):
    """
    Send the formatted content to Slack via a webhook.
    """
    slack_integration = SlackIntegration()
    slack_url = "https://hooks.slack.com/workflows/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"
    payload = {"flex_on_prem_chart": payload_content} 
    slack_integration.send_message(slack_url, payload)

# Helper function to reformat names from "Last,First" to "First Last"
def reformat_name(name):
    """
    Reformat names from "Last,First" to "First Last".
    """
    last, first = name.split(",", 1)
    return f"{first.strip()} {last.strip()}"

# Parse the Flex On Prem CSV DataFrame
def parse_flex_on_prem(flex_on_prem):
    """
    Filter and format the flex on-prem data, preparing it for Slack message.
    """
    global CHECK_FREQUENCY

    # Filter the DataFrame for FLEX shifts
    filtered_flex_on_prem = flex_on_prem[flex_on_prem["Shift"].str.contains("FLEX", na=False)]

    # Drop unnecessary columns
    filtered_flex_on_prem = filtered_flex_on_prem.drop(columns=["Shift", "Punch Type", "Punch Time"])

    # Sort by Managers and move 'Manager' column to the front
    filtered_flex_on_prem = filtered_flex_on_prem.sort_values(by="Manager", ascending=False)
    column_to_move = filtered_flex_on_prem.pop("Manager")
    filtered_flex_on_prem.insert(0, "Manager", column_to_move)

    # Format the output string
    if(filtered_flex_on_prem.size == 0):
        payload_content = f"\n\n0 Flex Employees On Premise in the Last {CHECK_FREQUENCY} Minutes.\n"
    else:
        payload_content = f"\n\nFlex Employees On Premise in the Last {CHECK_FREQUENCY} Minutes\n================================================\n"
        for manager, group in filtered_flex_on_prem.groupby('Manager'):
            payload_content += f"Manager: {reformat_name(manager)}\n"
            associates = ", ".join(
                f"{reformat_name(row['Employee Name'])} ({row['Employee ID']})" for _, row in group.iterrows()
            )
            payload_content += f"Associates: {associates}\n---------------------------------------------------\n"

    return payload_content

# Main function to process flex on premise data and send to Slack
def flex_on_prem_process():
    """
    Main processing function that downloads the flex on-prem data, formats it, and sends it to Slack.
    """
    flex_on_prem = download_flex_on_prem()
    slack_payload_content = parse_flex_on_prem(flex_on_prem)

    # Only send to Slack if there is data
    if flex_on_prem.size > 1:
        send_to_slack(slack_payload_content.strip())

# Scheduler function to periodically run flex on prem processing
def scheduler():
    """
    Schedules the flex on-prem process to run at specified times.
    """
    times = [
        "00:00", "01:00", "07:00", "08:00", "12:00", "13:00", "19:00", "20:00", 
    ]
    
    for t in times:
        schedule.every().day.at(t).do(flex_on_prem_process)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def load_sp_bucket_dump(driver):
    """
    Loads the shift plan bucket dump from the specified URL.
    """
    url = "https://us-east-1.quicksight.aws.amazon.com/sn/account/amazonbi/dashboards/b38dbec9-6514-423e-ac23-aee0e70a1aa6/sheets/b38dbec9-6514-423e-ac23-aee0e70a1aa6_23dab159-7824-4adf-af88-30784de2891f"
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    scenario_close = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id="dashboard-scenarios-blunt-modal-close"]')))
    scenario_close.click()
    target = wait.until(EC.presence_of_element_located(
        (By.ID, "block-b38dbec9-6514-423e-ac23-aee0e70a1aa6_636335bc-b4bd-4be8-b82b-1230a319cfbc")
    ))

    # Hover over it
    actions = ActionChains(driver)
    actions.move_to_element(target).perform()



    button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '[aria-label="Menu options, Throughput CPLH excl. Support (SP vs Actual), Pivot table"]')
    ))

    button.click()

    # Wait until the li with the visible text "Export to CSV" is clickable
    export_option = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//li[normalize-space(text())="Export to CSV"]')
    ))

    export_option.click()

    time.sleep(5)




def spe_audit(driver):
    """
    Checks every quicksight required to load the shift plan adherence file, inserts the data into the file, and then refreshes the tables in the file.
    """
    #load shift plan bucket dump
    load_sp_bucket_dump(driver)


    pass

# Main entry point
if __name__ == "__main__":
    firefox_integration = FirefoxIntegration()
    driver = firefox_integration.get_authenticated_driver()

    #shift planning and execution audit
    spe_audit(driver)

    driver.quit()
    #scheduler()
