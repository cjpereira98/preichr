import time
import sys
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

"""
!!!!YOU NEED TO USE THE NAMES OF THE PROCESSES HERE, NOT PROCESS ID!!!!
"""

class URIntegration:

    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver(True)
            self.own_driver = True

    
    def get_day(self, process, date):
        """
        Retrieve Units Rollup data for a specific day.
        """
        date = date.replace(hour=5, minute=0, second=0, microsecond=0)
        print(f"date: {date}")
        start_date_str = (date).strftime("%Y/%m/%d")
        print(f"start_date_str: {start_date_str}")
        end_date = date + timedelta(days=1)
        end_date = end_date.replace(hour=5, minute=0, second=0, microsecond=0)
        print(f"end_date: {end_date}")
        end_date_str = (end_date).strftime("%Y/%m/%d")
        print(f"end_date_str: {end_date_str}")
        filedate = date.strftime("%Y%m%d%H%M%S") + end_date.strftime("-%Y%m%d%H%M%S")
        file_name = f"unitsRollup-{FC}-{process}-{filedate}.csv"
        

        # Construct the cache folder path dynamically
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        cache_dir = os.path.join(project_root, "cache")
        os.makedirs(cache_dir, exist_ok=True)  # Ensure the cache directory exists
        file_path = os.path.join(cache_dir, file_name)

        print(f"file_path: {file_path}")

        try:
            #check if "unitsRollup-{FC}-{process}-{filedate}.csv" exists in cache
            if os.path.exists(file_path):
                print("This has already been downloaded")
            #else download it
            else: 
                url = f"https://fclm-portal.amazon.com/reports/unitsRollup?reportFormat=CSV&warehouseId={FC}&jobAction={process}&startDate={start_date_str}&startHour=0&startMinute=0&endDate={end_date_str}&endHour=0&endMinute=0"
                #self.driver.get(f"https://fclm-portal.amazon.com/reports/unitsRollup?reportFormat=CSV&warehouseId={FC}&jobAction={process}&startDate={start_date_str}&startHour=0&startMinute=0&endDate={end_date_str}&endHour=0&endMinute=0")
            #then wait until download is complete + 3 seconds
                # Execute JavaScript to download the file directly
                self.driver.execute_script(f"window.open('{url}', '_blank');")
                while not os.path.exists(file_path):
                    time.sleep(1)
                time.sleep(3)
            return
        except Exception as e:
            print(f"Error fetching day data: {e}")
            return None


# Usage example:
if __name__ == "__main__":
    print((datetime.now()-timedelta(days=1)).replace(hour=5, minute=0, second=0, microsecond=0))
    ur = URIntegration()
    ur.get_day("PalletReceived", datetime.now()-timedelta(days=1))
