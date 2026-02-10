import os
import sys
import time
import logging
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class ContainerResearchIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()
            self.own_driver = True

    def get_recent_containers(self, elapsed_minutes=10, max_retries=40, retry_delay=60):
        url = f'https://flow-sortation-na.amazon.com/{FC}/#/container-research?maxResults=5000&orderOldestFirst=false&searchIncludeStrings=r1&serializedTimeRange=relative_time:{elapsed_minutes}:minutes_ago:0:minutes_ago&searchExcludeStrings=DECANT&searchExcludeStrings=SORT&searchExcludeStrings=TRANS&searchExcludeStrings=PREP&searchExcludeStrings=PRIME&searchExcludeStrings=SIZE'
        
        self.driver.get(url)
        temp_duration = 10
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.driver.refresh()
                # Click the search button
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//button[@type='button' and @class='btn btn-success btn-sm time-search-button success' and @data-ng-click='performSearch()' and not(@disabled)]"))
                ).click()

                # Click the export to CSV button
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//span[@translate='container_research_export_to_csv_button' and @class='ng-scope']"))
                ).click()

                # If both operations succeed, break out of the loop
                break
            except (NoSuchElementException, TimeoutException) as e:
                temp_duration += 10

                retry_count += 1
                if retry_count < max_retries:
                    print(f"Attempt {retry_count} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed after {max_retries} attempts: {e}.")
                    if self.own_driver:
                        self.driver.quit()
                    raise

        # Wait for the download to complete
        download_dir = os.getcwd()
        file_path = None
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            file_pattern = os.path.join(download_dir, "download.csv")
            if os.path.exists(file_pattern):
                file_path = file_pattern
                break

        if not file_path:
            if self.own_driver:
                self.driver.quit()
            raise FileNotFoundError("CSV file not found after waiting for 30 seconds")

        # Process the CSV file with pandas
        df = pd.read_csv(file_path)
        os.remove(file_path)  # Clean up the downloaded file

        # Split the 'messages' column into 7 columns
        split_cols = df['Message'].str.split(',', expand=True)
        df['container_id'] = split_cols[2]
        df['routing'] = split_cols[4]

        # Filter the DataFrame based on the criteria
        #filtered_df = df[
        #    ((df['container_id'].str.startswith('tsX')) | (df['container_id'].str.startswith('csX'))) &
        #    ((df['routing'] == 'KICKOUT') | (df['routing'] == 'dz-P-PSOLVE') | (df['routing'] == ''))
        #]

        # Filter the DataFrame based on the criteria
        filtered_df = df[
            ((df['container_id'].str.startswith('tsX')) | (df['container_id'].str.startswith('csX'))) &
            ((df['routing'] == 'KICKOUT') | (df['routing'] == 'dz-P-PSOLVE'))
        ]

        # Print the filtered DataFrame for verification
        print(filtered_df)

        # Return the applicable container values
        container_values = filtered_df['container_id'].tolist()

        if self.own_driver:
            self.driver.quit()

        return container_values
    
    def watch_ps(self, dj_integration, interval=5):
        """
        Continuously fetch recent containers and pass them to DirectedJackpotIntegration.
        """
        while True:
            try:
                logging.info("Running ContainerResearchIntegration to fetch recent containers.")
                recent_containers = self.get_recent_containers(elapsed_minutes=1.5)
                dj_integration.add_containers_to_buffer(recent_containers)
                logging.info(f"Fetched and passed containers: {recent_containers}")
            except Exception as e:
                logging.error(f"Error in watch_ps: {e}")
            time.sleep(interval)  # Avoid busy waiting

    def close(self):
        if self.own_driver:
            self.driver.quit()
