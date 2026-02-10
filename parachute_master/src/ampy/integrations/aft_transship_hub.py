import os
import sys
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class AFTTransshipHubIntegration:

    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()

    def download_and_format_csv(self):
        #driver = FirefoxIntegration.get_authenticated_driver()

        download_dir = os.getcwd()
        file_path = os.path.join(download_dir, "AFT Transshipment Hub.csv")

        self.download_csv()

        df = pd.read_csv(file_path)

        shift_times = {
            "FHD": ("06:30", "18:30", ["SUN", "MON", "TUE"]),
            "WD": ("06:30", "18:30", ["WED"]),
            "BHD": ("06:30", "18:30", ["THU", "FRI", "SAT"]),
            "FHN": ("18:30", "06:30", ["SUN", "MON", "TUE"]),
            "WN": ("18:30", "06:30", ["WED"]),
            "BHN": ("18:30", "06:30", ["THU", "FRI", "SAT"]),
        }

        def get_shift(date_str):
            try:
                date_parts = date_str.split(" ")
                time_part = date_parts[1]
                day_part = date_parts[0]
                day_of_week = pd.to_datetime(day_part).strftime('%a').upper()
                for shift, (start, end, days) in shift_times.items():
                    if day_of_week[:3] in days:
                        if start <= time_part <= end or end < start and (time_part >= start or time_part <= end):
                            return shift
            except:
                return "Unknown"

        # Initialize new columns
        df['Unload Shift'] = ''
        df['Pallets for Reconcile'] = ''
        df['# TSX for Reconcile'] = ''
        df['# CSX for Reconcile'] = ''
        df['Units for Reconcile'] = ''
        df['% Remaining'] = ''
        df['Next VRID'] = ''
        df['Link'] = ''
        df['Reconcile'] = ''
        df['Flags'] = ''

        #Need to change this because I am only getting first 100 links
        #links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'stowing-in-progress')]")
        #stowing_links = [link.get_attribute('href') for link in links]

        # Construct the stowing links from the DataFrame
        stowing_links = []
        for index, row in df.iterrows():
            #if row['Details'] == "Stowing Progress":
            shipment_id = row['Shipment Reference Id']
            stowing_links.append(f"https://afttransshipmenthub-na.aka.amazon.com/{FC}/stowing-in-progress/{shipment_id}")

        for link in stowing_links:
            self.driver.get(link)
            wait = WebDriverWait(self.driver, 120)
            try:

                load_id_element = wait.until(EC.visibility_of_element_located((By.ID, 'loadId')))
                load_id = load_id_element.text

                quantity_reconcile_element = wait.until(EC.visibility_of_element_located((By.ID, 'quantityItemsReconcile')))
                quantity_reconcile = quantity_reconcile_element.text

                if (quantity_reconcile == '0'):
                    self.driver.get(link) #reload
                    quantity_reconcile_element = wait.until(EC.visibility_of_element_located((By.ID, 'quantityItemsReconcile')))
                    quantity_reconcile = quantity_reconcile_element.text

                while (load_id == "No appointment information found.") or ("Unavailable" in quantity_reconcile):
                    self.driver.get(link)
                    load_id_element = wait.until(EC.visibility_of_element_located((By.ID, 'loadId')))
                    load_id = load_id_element.text
                    quantity_reconcile_element = wait.until(EC.visibility_of_element_located((By.ID, 'quantityItemsReconcile')))
                    quantity_reconcile = quantity_reconcile_element.text

                #quantity_initial_element = wait.until(EC.visibility_of_element_located((By.ID, 'quantityItemsTotal')))
                #quantity_initial = quantity_initial_element.text

                pallet_quantity_reconcile_element = wait.until(EC.visibility_of_element_located((By.ID, 'palletQuantityReconcile')))
                pallet_quantity_reconcile = pallet_quantity_reconcile_element.text

                tote_quantity_reconcile_element = wait.until(EC.visibility_of_element_located((By.ID, 'toteQuantityReconcile')))
                tote_quantity_reconcile = tote_quantity_reconcile_element.text

                case_quantity_reconcile_element = wait.until(EC.visibility_of_element_located((By.ID, 'caseQuantityReconcile')))
                case_quantity_reconcile = case_quantity_reconcile_element.text

                try:
                    flags_element = self.driver.find_element(By.ID, 'receivedBy')
                    flags = flags_element.text
                except NoSuchElementException:
                    flags = "Unknown"

                

                matching_row = df[df['Load ID'] == load_id]
                if not matching_row.empty:
                    received_time = matching_row['Received Time'].values[0]
                    unload_shift = get_shift(received_time)

                    df.loc[df['Load ID'] == load_id, ['Unload Shift', 'Pallets for Reconcile', '# TSX for Reconcile', '# CSX for Reconcile', 'Units for Reconcile', 'Link', 'Flags']] = \
                        [unload_shift, pallet_quantity_reconcile, tote_quantity_reconcile, case_quantity_reconcile, quantity_reconcile, link, flags]
                else:
                    print(f"Load ID {load_id} not found in the DataFrame.")

            except Exception as e:
                print(f"Error processing link {link}: {e}")

        self.driver.quit()
        df.to_csv(file_path, index=False)

    def close_shipments(self, shipment_ids):
        driver = FirefoxIntegration.get_authenticated_driver()

        # Configure logging
        logging.basicConfig(filename='update_reconciles.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

        for shipment_id in shipment_ids:
            url = f"https://afttransshipmenthub-na.aka.amazon.com/{FC}/stowing-in-progress/{shipment_id}"
            driver.get(url)

            logging.info(f"Closing shipment ID: {shipment_id}")

            try:
                wait = WebDriverWait(driver, 60)
                reconcile_button = wait.until(
                    EC.visibility_of_element_located((By.ID, 'reconcileRequest')))
                reconcile_button.click()
                confirm_button = wait.until(
                    EC.visibility_of_element_located((By.ID, 'reconcile-button')))
                confirm_button.click()
                success_message = wait.until(
                    EC.visibility_of_element_located((By.ID, 'reconcile_success_alert')))
                print(f"Shipment {shipment_id} closed successfully.")
                logging.info(f"Shipment {shipment_id} closed successfully.")
                time.sleep(1)  # Wait for 1 second after clicking the button
            except Exception as e:
                print(f"Error processing shipment {shipment_id}: {e}")
                logging.error(f"Error processing shipment {shipment_id}: {e}")

        driver.quit()

    def download_csv(self):
        download_dir = os.getcwd()
        file_path = os.path.join(download_dir, "AFT Transshipment Hub.csv")

        self.driver.get(f"https://afttransshipmenthub-na.aka.amazon.com/{FC}/view-transfers/inbound/")
        time.sleep(5)  # Wait for the page to load

        if os.path.exists(file_path):
            os.remove(file_path)

        wait = WebDriverWait(self.driver, 30)

        # Set the date range to the 30-day window leading up to the current day
        end_date = datetime.now() #- timedelta(days=29)
        start_date = end_date - timedelta(days=29)
        date_format = "%Y-%m-%d"

        # Retry mechanism for clicking the CSV button
        retries = 5
        while retries > 0:
            try:

                # Click on the date picker input to open the date picker
                date_picker_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.form-control.flatpickr-input.input")))
                date_picker_input.click()
                #time.sleep(5)

                # Select the start date
                if start_date.month != end_date.month:
                    prev_month_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.flatpickr-prev-month")))
                    prev_month_button.click()
                #time.sleep(5)
                print(f"Selecting start date: {start_date.strftime('%B %d, %Y').replace(' 0', ' ')}")
                #time.sleep(1000)

                start_date_day = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[@aria-label='{start_date.strftime('%B %d, %Y').replace(' 0', ' ')}']")))
                start_date_day.click()

                if start_date.month != end_date.month:
                    next_month_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.flatpickr-next-month")))
                    next_month_button.click()

                # Select the end date
                end_date_day = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[@aria-label='{end_date.strftime('%B %d, %Y').replace(' 0', ' ')}']")))
                end_date_day.click()

                submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submitDateRangeForm")))
                submit_button.click()
                time.sleep(10)  # Wait for the form submission and the page to load the results

                dropdown = wait.until(EC.visibility_of_element_located((By.NAME, "inboundTransfersTable_length")))
                dropdown.click()
                option = self.driver.find_element(By.XPATH, "//option[@value='100']")
                option.click()
        
        
                csv_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-default.buttons-csv.buttons-html5")))
                csv_button.click()
                break
            except Exception as e:
                print(f"Attempt failed, retrying... {e}")
                retries -= 1
                time.sleep(5)
                self.driver.refresh()
                wait = WebDriverWait(self.driver, 30)  # Reinitialize wait after refresh

        while not os.path.exists(file_path):
            time.sleep(1)

        print(f"File downloaded: {file_path}")


if __name__ == "__main__":
    AFTTransshipHubIntegration.download_and_format_csv()
