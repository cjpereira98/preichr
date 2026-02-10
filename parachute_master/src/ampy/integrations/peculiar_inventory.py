import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class PeculiarInventoryIntegration:
    def __init__(self, fc=f'{FC}', driver=None):
        self.fc = fc
        self.driver = driver or FirefoxIntegration().get_authenticated_driver(True)
        self.created_driver = driver is None

    def __del__(self):
        if self.created_driver and self.driver:
            self.driver.quit()

    def navigate_to_inventory(self):
        base_url = f"http://peculiar-inventory-na.aka.corp.amazon.com/{self.fc}/overview"
        self.driver.get(base_url)

    def get_scrub_buckets_data(self):
        self.navigate_to_inventory()
        
        try:
            # Select "All" from the dropdown for time bucket
            time_dropdown = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#a-autoid-1 .a-dropdown-prompt"))
            )
            time_dropdown.click()

            time.sleep(1)

            all_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#timeBucketDropDown_5"))
            )
            all_option.click()
            time.sleep(1)

            # List of buckets to scrub
            buckets = [
                "Inbound", "Outbound", "Transshipment",
                "PendingResearch", "PendingRepair", "ProblemSolve"
            ]
            
            for bucket in buckets:
                # Select the bucket
                
                bucket_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#a-autoid-0 .a-dropdown-prompt"))
                )
                bucket_dropdown.click()
                time.sleep(1)
                
                bucket_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[data-value='{{\"stringVal\":\"{bucket}\"}}']"))
                )
                bucket_option.click()
                time.sleep(3)

                # Click the submit button to download the file
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "a-autoid-2"))
                )
                submit_button.click()
                time.sleep(20)# Ensure the download completes

        except TimeoutException as e:
            print(f"An error occurred: {e}")

