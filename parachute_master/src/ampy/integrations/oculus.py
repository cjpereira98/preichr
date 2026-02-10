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

class OculusIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()
            self.own_driver = True

    def get_vendor_freight_data(self):
        # Navigate to the Oculus vendor freight page
        self.driver.get(f"https://oculus.qubit.amazon.dev/vendorfreight/{FC}")

        # Wait for the export button to be visible and click it
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )  # Ensure the page is loaded

            export_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Export data')]]"))
            )
            time.sleep(1)
            export_button.click()
        except Exception as e:
            print("Failed to locate and click the export button:", e)
            print("Page source for debugging:")
            print(self.driver.page_source)  # Print the page source for debugging
            if self.own_driver:
                self.driver.quit()
            raise

        # Wait for the file to be downloaded
        download_dir = os.getcwd()
        file_pattern = os.path.join(download_dir, f"_vendorfreight_{FC}*.csv")
        file_path = None

        for _ in range(30):  # Wait up to 30 seconds
            matching_files = glob.glob(file_pattern)
            if matching_files:
                file_path = matching_files[0]
                break
            time.sleep(1)

        if not file_path:
            if self.own_driver:
                self.driver.quit()
            raise FileNotFoundError("CSV file not found after waiting for 30 seconds")

        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Clean up the downloaded file
        os.remove(file_path)

        # Print the DataFrame
        print(df)

        return df

    def close(self):
        if self.own_driver:
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    oi = OculusIntegration()
    vendor_freight_df = oi.get_vendor_freight_data()
    oi.close()
