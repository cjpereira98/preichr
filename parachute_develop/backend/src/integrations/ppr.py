import time
import sys
import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class ProcessPathRollupIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.firefox = FirefoxIntegration()
            self.driver = self.firefox.get_authenticated_driver()

    def get_flex_on_prem(self, url):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 30)
        download_link = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@data-click-metric="CSV" and contains(@href, "reportFormat=CSV")]')))
        download_link.click()
        time.sleep(5)  # Ensure the download completes


    def get_active_problem_solvers(self, url):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 30)
        download_link = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@data-click-metric="CSV" and contains(@href, "reportFormat=CSV")]')))
        download_link.click()
        time.sleep(5)  # Ensure the download completes

    def get_problem_solve_hours(self, start_date_time, end_date_time):
        downloaded_file = self.download_ppr_dump(start_date_time, end_date_time)

        # Read the CSV file and find the row with 'LineItem Name' = 'IB Problem Solve'
        df = pd.read_csv(downloaded_file)
        row = df[df['LineItem Name'] == 'IB Problem Solve']
        if not row.empty:
            actual_hours = row['Actual Hours'].values[0]
        else:
            actual_hours = None

        os.remove(downloaded_file)
        # Return the 'Actual Hours' value
        return actual_hours
    
    def get_case_ti(self, start_date_time, end_date_time):
        downloaded_file = self.download_ppr_dump(start_date_time, end_date_time)

        # Read the CSV file and find the row with 'LineItem Name' = 'Case TI'
        df = pd.read_csv(downloaded_file)
        row = df[df['LineItem Name'] == 'Case Transfer In']
        if not row.empty:
            actual_volume = row['Actual Volume'].values[0]
        else:
            actual_volume = None

        os.remove(downloaded_file)
        # Return the 'Actual Hours' value
        return actual_volume
    
    def download_ppr_dump(self, start_date_time, end_date_time):
        # Define the URL with the appropriate query parameters
        url = f"https://fclm-portal.amazon.com/reports/processPathRollup?reportFormat=HTML&warehouseId={FC}&startDateDay={start_date_time.strftime('%Y/%m/%d')}&maxIntradayDays=1&spanType=Intraday&startDateIntraday={start_date_time.strftime('%Y/%m/%d')}&startHourIntraday={start_date_time.hour}&startMinuteIntraday={start_date_time.minute}&endDateIntraday={end_date_time.strftime('%Y/%m/%d')}&endHourIntraday={end_date_time.hour}&endMinuteIntraday={end_date_time.minute}&_adjustPlanHours=on&_hideEmptyLineItems=on&employmentType=AllEmployees"
        
        # Navigate to the URL
        self.driver.get(url)

        # Wait until the CSV link is clickable and click it
        wait = WebDriverWait(self.driver, 30)
        csv_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.cp-submit[data-click-metric='CSV']")))
        csv_button.click()

        time.sleep(5)  # Wait for the download to complete

        # Define the download directory and filename pattern
        filename_pattern = "processPathReport"
        #print(os.getcwd())
        # Busy wait for the file to download
        downloaded_file = None
        for _ in range(30):  # Check for the file every second for 30 seconds
            for filename in os.listdir(os.getcwd()):
                #print(f"Found file: {filename}")
                #print(os.getcwd())
                #print(filename)
                if filename.startswith(filename_pattern) and filename.endswith(".csv"):
                    downloaded_file = os.path.join(os.getcwd(), filename)
                    break
            if downloaded_file:
                break
            time.sleep(1)

        if not downloaded_file:
            raise FileNotFoundError("CSV file download failed.")
        
        return downloaded_file 
    
    def get_day(self, process, date):
        """
        Retrieve PPR data for a specific day.
        """
        try:
            return self.get_problem_solve_hours(date, date)
        except Exception as e:
            print(f"Error fetching day data: {e}")
            return None


# Usage example:
if __name__ == "__main__":
    ppr = ProcessPathRollupIntegration()
    ppr.get_active_problem_solvers(f"https://fclm-portal.amazon.com/reports/functionRollup?warehouseId={FC}&spanType=Day&startDate=2024-07-23T00:00:00.000&endDate=2024-07-24T00:00:00.000&reportFormat=HTML&processId=01002980")
