import os
import sys
import time
import glob
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

class RosterIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()

    def fetch_employee_roster(self):        
        # Navigate to the employee roster page
        self.driver.get(f"https://fclm-portal.amazon.com/employee/employeeRoster?&warehouseId={FC}")

        # Wait for the CSV download link to be visible and click it
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "a.cp-submit[data-click-metric='CSV']"))
        ).click()

        # Wait for the file to be downloaded
        download_dir = os.getcwd()
        file_pattern = os.path.join(download_dir, f"employeeList-{FC}*.csv")
        file_path = None

        for _ in range(30):  # Wait up to 30 seconds
            matching_files = glob.glob(file_pattern)
            if matching_files:
                file_path = matching_files[0]
                break
            time.sleep(1)

        if not file_path:
            self.driver.quit()
            raise FileNotFoundError("CSV file not found after waiting for 30 seconds")

        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Clean up the downloaded file
        os.remove(file_path)
        return df

    def get_employee_badge_conversion_dict(self):
        df = self.fetch_employee_roster()
        # Create the conversion dictionary
        conversion_dict = pd.Series(df['Badge Barcode ID'].values, index=df['Employee ID']).to_dict()

        return conversion_dict

    def close(self):
        self.driver.quit()

# Example usage
if __name__ == "__main__":
    ri = RosterIntegration()
    conversion_dict = ri.get_employee_badge_conversion_dict()
    print(conversion_dict)
    ri.close()
