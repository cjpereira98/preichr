import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class OntBaseIntegration:

    def __init__(self, driver=None):
        self.driver = driver

    def get_piles_data(self, designation):
        if not self.driver:
            self.driver = FirefoxIntegration.get_authenticated_driver()
            own_driver = True
        else:
            own_driver = False

        self.driver.get(f"https://ont-base.corp.amazon.com/{FC}/icqa/piles/export?locale=en")

        wait = WebDriverWait(self.driver, 30)
        date_range_input = wait.until(EC.element_to_be_clickable((By.ID, "dateRange")))
        date_range_input.click()

        if designation == 'prior-day':
            date_range_key = "Yesterday"
        elif designation == 'wtd':
            date_range_key = "Week To Date"
        elif designation == 'prior-week':
            date_range_key = "Last Week"
        else:
            raise ValueError("Invalid designation. Choose from 'prior-day', 'wtd', or 'prior-week'.")

        date_range_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[@data-range-key='{date_range_key}']")))
        date_range_option.click()

        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
        submit_button.click()

        csv_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-secondary.buttons-csv.buttons-html5")))
        csv_button.click()

        file_path = os.path.join(os.getcwd(), "ONT Base.csv")
        while not os.path.exists(file_path):
            time.sleep(1)

        time.sleep(5)

        df = pd.read_csv(file_path)
        os.remove(file_path)  # Clean up the file after reading
        
        if own_driver:
            self.driver.quit()

        return df
