import time
import sys
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration

class IDRTIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver(True)
            self.own_driver = True

    def simulate_scan(self, data):
        """
        Simulate a scan with the provided data.
        """
        try:
            # Inject JavaScript to simulate the scan
            script = f"handleScan('{data}', '', '', '', '');"
            self.driver.execute_script(script)
        except Exception as e:
            print(f"Error in simulate_scan: {e}")

    def process_pallets(self, pallet_ids, destination_id):
        """
        For each pallet ID, simulate a scan, wait, then scan the destination ID, and wait.
        """
        try:
            self.driver.get("https://fc-spaceman-idrt-iad.aka.amazon.com/")
            for pallet_id in pallet_ids:
                # Scan the pallet ID
                self.simulate_scan(pallet_id)
                time.sleep(10)  # Wait for 5 seconds

                # Scan the destination ID
                self.simulate_scan(destination_id)
                time.sleep(10)  # Wait for 5 seconds
        except Exception as e:
            print(f"Error in process_pallets: {e}")

    def close(self):
        if self.own_driver:
            self.driver.quit()

# Testing the integration
if __name__ == "__main__":
    # Initialize and test the IDRT integration
    idrt_integration = IDRTIntegration()
    
    # Test pallet IDs and destination ID
    pallet_ids = ["paXTk22r8wx", "paXT802at33", "paXTr0qy7hf"]
    destination_id = "dz-P-StopLosingPallets"
    
    # Process the pallets
    idrt_integration.process_pallets(pallet_ids, destination_id)
    
    # Close the driver after testing
    idrt_integration.close()
