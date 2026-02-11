import os
import sys
import logging
import time
import traceback
from collections import deque
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Assuming FirefoxIntegration and FC config are available from the respective modules
# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from config.config import FC

class FCResearchIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver(True)
            self.own_driver = True
        self.buffer = deque()
        #self.log_file = 'fc_research_log.txt'
        #logging.basicConfig(filename=self.log_file, level=logging.INFO)

    def add_containers_to_buffer(self, containers):
        for container in containers:
            if container not in self.buffer:
                self.buffer.append(container)

    def _check_element(self, by, value):
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

    def process_container(self, container, sideline_integration):
        try:
            fc = FC  # Use FC from the config file
            self.driver.get(f"http://fcresearch-na.aka.amazon.com/{fc}/results?s={container}")
            logging.info(f"Processing container {container}")

            time.sleep(5)  # Potentially speed this up

            # Check for Full Container Shortage, Transshipment Completed Shortage
            try:
                asins_list = []

                problem_element = self.driver.find_element(By.XPATH, "//td[contains(text(),'Full Container Shortage,Transshipment Completed Shortage')]")

                try:
                    expiration_date = self.driver.find_element(By.CSS_SELECTOR, 'div[data-section-type="carton-general-info"]').find_element(By.XPATH, "//th[contains(text(),'Expiration Date')]/following-sibling::td").text

                except NoSuchElementException:
                    expiration_date=None
                #print(problem_element)
                #if problem_element:
                print(f"Full Container Shortage found for container {container}. Attempting to rehydrate inventory.")
                time.sleep(3)

                # Locate the Inventory History section
                inventory_history_table = self.driver.find_element(By.ID, "table-inventory-history")
                print("Inventory History section located: ", inventory_history_table)
                time.sleep(3)
                inventory_history_table_body = inventory_history_table.find_element(By.TAG_NAME, "tbody")
                inventory_history_rows = inventory_history_table_body.find_elements(By.TAG_NAME, "tr")
                print("Inventory History rows located: ", inventory_history_rows)
                time.sleep(3)
                for row in inventory_history_rows:
                    try:
                        elements = row.find_elements(By.TAG_NAME, "td")
                        for e in elements:
                            print(e.text)

                        new_bin = row.find_elements(By.TAG_NAME, "td")[10].text
                        print("New Bin: ", new_bin)
                        time.sleep(3)
                        if new_bin.startswith("vtcs"):
                            asin = row.find_elements(By.TAG_NAME, "td")[3].text  # Assuming FCSku is the third link
                            
                            quantity = row.find_elements(By.TAG_NAME, "td")[7].text  # Assuming quantity is in the first span with this class
                            print(f"Rehydrating inventory for FCSku: {asin}, Quantity: {quantity}")
                            asins_list.append([asin, quantity])
                            sideline_integration.add_container_to_buffer(new_bin, 'overage', asins_list)
                    except NoSuchElementException:
                        continue
                    print("ASINs list: ", asins_list)

            except NoSuchElementException:
                logging.info(f"No Full Container Shortage issue found for container {container}")

            # Check for carton-general-info section
            if not self._check_element(By.CSS_SELECTOR, 'div[data-section-type="carton-general-info"]'):
                logging.error(f"Carton General Info section not found for container {container}")
                return

            time.sleep(5)  # Potentially speed this up

            # Locate Failure Reason
            failure_reason_xpath = "//th[contains(text(), 'Failure Reason')]/following-sibling::td"
            try:
                failure_reason = self.driver.find_elements(By.XPATH, failure_reason_xpath)[0].text
                if "NO_PURCHASE_ORDERS" not in failure_reason:
                    logging.info(f"Failure reason for container {container} does not contain 'NO_PURCHASE_ORDERS'. Found: {failure_reason}")
                    return
            except Exception as e:
                logging.error(f"Exception occurred while locating Failure Reason for container {container}: {e}")
                logging.error(traceback.format_exc())
                return

            # Locate GTIN14
            gtin14_xpath = "//th[contains(text(),'GTIN14')]/following-sibling::td"
            try:
                gtin14 = self.driver.find_element(By.XPATH, gtin14_xpath).text.strip()
                logging.info(f"GTIN14 found for container {container}: {gtin14}")
            except Exception as e:
                logging.error(f"Exception occurred while locating GTIN14 for container {container}: {e}")
                logging.error(traceback.format_exc())
                return

            # Locate SKU
            try:
                # Locate the SKU
                sku_element = self.driver.find_element(By.XPATH, '//table[@id="table-carton-contents"]//td[2]/a')
                sku = sku_element.text if sku_element else None
                if sku:
                    logging.info(f"SKU located: {sku}")
                else:
                    logging.error("SKU not found.")
            except Exception as e:
                logging.error(f"Error locating SKU: {str(e)}")

        except Exception as e:
            logging.error(f"An error occurred while processing container {container}: {e}")
            logging.error(traceback.format_exc())

    def inf_research(self, sideline_integration, interval=1):
        """
        Continuously monitors the queue and processes containers.
        The function checks for new containers in the buffer and calls process_container() on each.
        """
        logging.info("FCResearch thread started")
        while True:
            try:
                if self.buffer:
                    container = self.buffer.popleft()
                    logging.info(f"FCResearch processing: {container} (buffer remaining: {len(self.buffer)})")
                    self.process_container(container, sideline_integration)
                else:
                    time.sleep(interval)  # Wait for a bit before checking the queue again
            except Exception as e:
                logging.error(f"FCResearch error processing iteration: {e}", exc_info=True)

    def close(self):
        if self.own_driver:
            self.driver.quit()

    def add_test_containers(self):
        """
        Add test container values to the buffer for independent testing.
        """
        test_containers = ['csXNP4vWytM', 'csXNQ4qPzZT']
        self.add_containers_to_buffer(test_containers)
        logging.info("Test containers added to buffer for testing.")


if __name__ == "__main__":
    try:
        # Initialize FCResearchIntegration and add test containers
        fc_research_integration = FCResearchIntegration()
        fc_research_integration.add_test_containers()

        # Start the research process
        fc_research_integration.inf_research()

    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
    except Exception as e:
        logging.error(f"An error occurred in the main process: {e}")
        logging.error(traceback.format_exc())
    finally:
        # Ensure the driver is properly closed
        fc_research_integration.close()
        logging.info("FCResearchIntegration process finished.")


