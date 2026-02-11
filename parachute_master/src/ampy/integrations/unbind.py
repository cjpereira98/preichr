import time
import os
import sys
import logging
from collections import deque
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration
from integrations.dj import DirectedJackpotIntegration

class UnbindIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()
            self.own_driver = True
        self.buffer = deque()

    def add_to_buffer(self, container_id):
        """
        Add container ID to the buffer.
        """
        self.buffer.append(container_id)

    def inf_unbind(self, dj_integration, interval=5):
        """
        Continuously process containers from the buffer by simulating the scanning of each container
        into the unbinding tool. After processing, add the container to dj_integration's buffer.
        """
        try:
            self.navigate_to_tool()
            logging.info("Unbind navigate_to_tool completed successfully")
        except Exception as e:
            logging.error(f"Unbind navigate_to_tool FAILED — thread cannot proceed: {e}")
            return

        while True:
            try:
                if self.buffer:
                    container_id = self.buffer.popleft()
                    logging.info(f"Unbind processing: {container_id} (buffer remaining: {len(self.buffer)})")
                    success = self.process_container(container_id)
                    if success:
                        dj_integration.add_containers_to_buffer([container_id])
                        logging.info(f"Unbind -> DJ: {container_id} (re-queued)")
                time.sleep(interval)  # Avoid busy waiting
            except Exception as e:
                logging.error(f"Unbind error processing iteration: {e}", exc_info=True)

    def navigate_to_tool(self):
        """
        Navigate to the Unbind Hierarchy tool.
        """
        self.driver.get("http://tx-b-hierarchy-iad.iad.proxy.amazon.com/unbindHierarchy")
        logging.info("Navigated to Unbind Hierarchy tool.")
        # Wait for the page to load and be ready for interaction
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "text-entry"))
        )

    def process_container(self, container_id):
        """
        Simulate scanning the container into the tool and process it.
        Returns True if the container is successfully processed, False otherwise.
        """
        try:
            # Locate the text input for scanning containers
            #scan_input = WebDriverWait(self.driver, 10).until(
            #    EC.visibility_of_element_located((By.XPATH, "//div[@id='text-entry']//input[@type='text']"))
            #)
            #scan_input.clear()
            #scan_input.send_keys(container_id + Keys.RETURN)
            #logging.info(f"Scanned container: {container_id}")
            # Inject JavaScript to simulate the scan
            script = f"aft.scan('{container_id}', '', '', '', '');"
            self.driver.execute_script(script)
            logging.info(f"Simulated scan for container: {container_id}")

            # Click the "Continue" button
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "continue-btn"))
            )
            continue_button.click()

            # Wait for success message (or handle errors)
            #WebDriverWait(self.driver, 10).until(
                #EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Successfully unbound')]"))
            #)
            time.sleep(3)
            logging.info(f"Successfully unbound container: {container_id}")
            return True
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Failed to unbind container {container_id}: {e}")
            return False

    def close(self):
        if self.own_driver:
            self.driver.quit()

    # Testing the integration
if __name__ == "__main__":
    # Set up logging to print to console
    logging.basicConfig(level=logging.INFO)

    # Create drivers for both integrations
    unbind_driver = FirefoxIntegration.get_authenticated_driver(True)
    dj_driver = FirefoxIntegration.get_authenticated_driver(True)

    # Initialize integrations
    unbind_integration = UnbindIntegration(unbind_driver)
    dj_integration = DirectedJackpotIntegration(dj_driver)

    # Add test container IDs to the buffer
    test_containers = ['tsX2iwct6r1', 'tsX07vhxpz9', 'tsX0ctgnadh']
    for container_id in test_containers:
        unbind_integration.add_to_buffer(container_id)

    # Run the unbind integration to process the buffer
    unbind_integration.inf_unbind(dj_integration)

    # Close the drivers after testing
    unbind_integration.close()
    dj_integration.close()
