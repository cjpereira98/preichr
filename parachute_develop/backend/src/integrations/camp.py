import os
import sys
import time
import glob
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class CampIntegration:
    BASE_URL = "https://camp.corp.amazon.com/metrics/{metric}?endDate={end_date}%2023:59:59&granularity=Daily&startDate={start_date}%2000:00:00&showSummary=true&configFilterGroups=Region,Super%20Regional,Ops%20Regional&configRollupGroup=FC%20Type&Region=NA&rollupGroup=IXD&target={FC}"

    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()

    def navigate_to_page(self, metric, start_date, end_date):
        url = self.BASE_URL.format(metric=metric, start_date=start_date, end_date=end_date, FC=FC)
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button.css-sdqoxf[role='tab'][mdn-tab-value='advancedInfo']"))
        ).click()
        #WebDriverWait(self.driver, 30).until(
        #    EC.visibility_of_element_located((By.CSS_SELECTOR, "span.css-atcydw.conversation-value.fail-state"))
        #)

    def get_csv_value(self, metric, designation):
        download_button = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button.btn-success.position-relative.metric-csv-toggle.css-n0loux"))
        )
        download_button.click()
        time.sleep(5)  # Wait for the CSV to download

        download_dir = os.getcwd()
        file_path_pattern = os.path.join(download_dir, "camp*.csv")
        file_path = None

        for _ in range(10):
            matching_files = glob.glob(file_path_pattern)
            if matching_files:
                file_path = matching_files[0]
                break
            time.sleep(1)

        if not file_path:
            self.driver.quit()
            raise FileNotFoundError("CSV file not found after waiting for 10 seconds")
        
        time.sleep(5)  # Wait for the download to complete

        df = pd.read_csv(file_path)
        time.sleep(1)
        #print(df)
        os.remove(file_path)  # Clean up the file after reading

        if designation == 'prior-day':
            target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
            #print(target_date)
            #print("Metric:", metric)
            target_value = df[df['date'] == target_date][metric]
            return target_value.iloc[0] if not target_value.empty else None
        elif designation == 'wtd':
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            target_dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d 00:00:00') for i in range(today.weekday() + 1)]
            target_values = df[df['date'].isin(target_dates)][metric].tolist()
            return sum(target_values) / len(target_values) if target_values else None
        elif designation == 'prior-week':
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_prior_week = start_of_week - timedelta(days=1)
            start_of_prior_week = end_of_prior_week - timedelta(days=6)
            target_dates = [(start_of_prior_week + timedelta(days=i)).strftime('%Y-%m-%d 00:00:00') for i in range(7)]
            target_values = df[df['date'].isin(target_dates)][metric].tolist()
            return sum(target_values) / len(target_values) if target_values else None
        else:
            raise ValueError("Invalid designation. Choose from 'prior-day', 'wtd', or 'prior-week'.")

    def get_metric_value(self, metric, designation):
        if designation == 'prior-day':
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = start_date
        elif designation == 'wtd':
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
        elif designation == 'prior-week':
            end_date = (datetime.now() - timedelta(days=datetime.now().weekday() + 1)).strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=datetime.now().weekday() + 7)).strftime('%Y-%m-%d')
        else:
            raise ValueError("Invalid designation. Choose from 'prior-day', 'wtd', or 'prior-week'.")

        self.navigate_to_page(metric, start_date, end_date)
        return self.get_csv_value(metric, designation)

if __name__ == "__main__":
    camp_integration = CampIntegration()
    metric_name = "aqat_pid_dpmo"
    print("Prior Day Value:", camp_integration.get_metric_value(metric_name, 'prior-day'))
    print("WTD Value:", camp_integration.get_metric_value(metric_name, 'wtd'))
    print("Prior Week Value:", camp_integration.get_metric_value(metric_name, 'prior-week'))
