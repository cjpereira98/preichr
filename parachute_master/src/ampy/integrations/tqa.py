import os
import sys
import logging
from collections import deque
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from config.config import DUMMY_CONTAINER

class TQAIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver(True)
            self.own_driver = True
        self.overage_buffer = deque()
        self.adjustment_buffer = deque()
    
    def add_container_to_buffer(self, container_id, container_type, asins=None):
        if container_type == 'overage':
            self.overage_buffer.append(container_id)
        if container_type == 'adjustment':
            self.adjustment_buffer.append([container_id, asins])

    def tqa_containers(self, container_ids):
        self.driver.get('http://qa-tool-iad.iad.proxy.amazon.com/transshipQATool')
        wait = WebDriverWait(self.driver, 30)

        for container_id in container_ids:
            try:
                #search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.field-input.field-input--m')))
                #search_input.clear()
                #search_input.send_keys(container_id + Keys.RETURN)
                #print(container_id)

                script = f"aft.scan('{container_id}', '', '', '', '');"
                self.driver.execute_script(script)
                
                change_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[@class="btn-secondary btn--fit" and @type="button"]//span[contains(text(), "Change Container")]')))
                change_button.click()
                
                yes_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[@class="btn-primary btn--xs" and @type="button"]/div[@class="text-layout text-layout--flex text-layout--h-align-center text-layout--v-align-middle"]/span[@class="text"]')))
                yes_button.click()
                
                print(f'Container {container_id} has been shorted.')

            except NoSuchElementException as e:
                print(f"Element not found for container {container_id}: {e}")
                try:
                    # Click "Change Container" button
                    change_button = self.driver.find_element(By.XPATH, '//button[@class="btn-secondary btn--fit" and @type="button"]//span[contains(text(), "Change Container")]')
                    change_button.click()

                    # Click "Yes" button
                    yes_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[@class="btn-primary btn--xs" and @type="button"]/div[@class="text-layout text-layout--flex text-layout--h-align-center text-layout--v-align-middle"]/span[@class="text"]')))
                    yes_button.click()

                    print(f'No action taken for container {container_id}.')
                except NoSuchElementException as nested_e:
                    print(f"Nested element not found for container {container_id}: {nested_e}")
            except Exception as e:
                print(f"Error processing container {container_id}: {e}")
                print(f"Element not found for container {container_id}: {e}")
                try:
                    # Click "Change Container" button
                    change_button = self.driver.find_element(By.XPATH, '//button[@class="btn-secondary btn--fit" and @type="button"]//span[contains(text(), "Change Container")]')
                    change_button.click()

                    # Click "Yes" button
                    yes_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[@class="btn-primary btn--xs" and @type="button"]/div[@class="text-layout text-layout--flex text-layout--h-align-center text-layout--v-align-middle"]/span[@class="text"]')))
                    yes_button.click()

                    print(f'No action taken for container {container_id}.')
                except NoSuchElementException as nested_e:
                    print(f"Nested element not found for container {container_id}: {nested_e}")

        print('All containers have been shorted.')
        if self.own_driver:
            self.driver.quit()

    def overage_containers(self, container_ids):
        self.driver.get('https://aft-poirot-website-iad.iad.proxy.amazon.com/')
        #time.sleep(20)  # Wait for manual authentication

        for container_id in container_ids:
            try:
                search_input = self.driver.find_element(By.CSS_SELECTOR, 'input.field-input.field-input--m')
                search_input.clear()
                search_input.send_keys(container_id + Keys.RETURN)
                time.sleep(1)  # Wait for input to be processed

                # Click "Container Overage" button
                overage_button = self.driver.find_element(By.XPATH, '//button[@class="btn-secondary btn--fit" and @type="button"]//span[contains(text(), "Container Overage")]')
                overage_button.click()
                time.sleep(1)  # Wait for action to be processed

                print(f'Container {container_id} marked as overage.')
            except NoSuchElementException as e:
                print(f"Element not found for container {container_id}: {e}")
                try:
                    # Click "Change Container" button
                    change_button = self.driver.find_element(By.XPATH, '//button[@class="btn-secondary btn--fit" and @type="button"]//span[contains(text(), "Change Container")]')
                    change_button.click()

                    # Click "No" button
                    no_button = self.driver.find_element(By.XPATH, '//button[@class="btn-secondary btn--xs" and @type="button"]//span[contains(text(), "No")]')
                    no_button.click()

                    print(f'No action taken for container {container_id}.')
                except NoSuchElementException as nested_e:
                    print(f"Nested element not found for container {container_id}: {nested_e}")
            except Exception as e:
                print(f"Error processing container {container_id}: {e}")

        print('All containers have been processed for overage.')
        if self.own_driver:
            self.driver.quit()

    def navigate_to_tool(self):
        # Logic to navigate to the Sideline tool (e.g., similar to overage_containers)
        self.driver.get('https://aft-poirot-website-iad.iad.proxy.amazon.com/')
        time.sleep(10)  # Wait for manual authentication

    def close(self):
        if self.own_driver:
            self.driver.quit()