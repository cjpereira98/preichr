import os
import sys
import time
import logging
from collections import deque
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration
from integrations.slack import SlackIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class DirectedJackpotIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
            self.own_driver = False
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()
            self.own_driver = True
        self.buffer = deque()
        self.repeat_buster = deque(maxlen=100)

    def _click_if_visible(self, by, value):
        if self._check_element(by, value):
            try:
                self.driver.find_element(by, value).click()
                print(f"Clicked on element with {by}='{value}'")
            except Exception as e:
                print(f"Error clicking element with {by}='{value}': {e}")

    def add_containers_to_buffer(self, containers):
        for container in containers:
            if container not in self.buffer:
                self.buffer.append(container)
        #self.buffer.extend(containers)

    #def parse_containers(self, containers):
    #    invalid_routing = []
    #    invalid_container = []
    #    virtually_empty = []

        # Navigate directly to the specific process
        #self.driver.get('https://web.iad.prod.taskui.aft.amazon.dev/?listingID=eb105a2a-bcba-4aa9-9b56-5ea2d9e22b5b#initialized')
        #print("Navigated directly to the process 1208.")

        # Navigate to the FC menu with the building passed in from config
    #    fc = FC  # Replace with the actual FC value from your config
    #    self.driver.get(f'https://fcmenu-iad-regionalized.corp.amazon.com/{fc}')
    #    print(f"Navigated to the FC menu for {fc}.")

        # Simulate sending keys "1208" and pressing Enter
    #    try:
    #        body = WebDriverWait(self.driver, 20).until(
    #            EC.presence_of_element_located((By.TAG_NAME, "body"))
    #        )
    #        body.send_keys("1208" + Keys.RETURN)
    #        print("Entered '1208' and pressed Enter.")
    #    except Exception as e:
    #        print(f"Error sending keys to input: {e}")
        
    #    try:
    #        WebDriverWait(self.driver, 20).until(
    #            EC.visibility_of_element_located((By.XPATH, "//div[@class='list-item-text__primary']//span[@class='text' and text()='Directed Jackpot']"))
    #        ).click()
        
    #    except Exception as e:
    #        print(f"Error: {e}")

    #    for container in containers:
    #        try:
    #            # Execute JavaScript to simulate the scanner input
    #            self.driver.execute_script(f"wavelinkScannerProcessed('{container}', '', '', '', '');")
    #            time.sleep(1)  # Wait for 1 second to allow the page to process the input

                # Check for invalid routing
    #            if self._check_element(By.XPATH, "//div[@class='alert__content alert__content--density-dense']//span[text()='Container has invalid routing.']"):
    #                invalid_routing.append(container)
    #                print(f"Invalid routing for container {container}")

                # Check for invalid container
    #            elif self._check_element(By.XPATH, "//div[@class='alert alert--variant-error theme--variant-error alert--density-dense']//span[text()='Container is not valid.']"):
    #                invalid_container.append(container)
    #                print(f"Invalid container {container}")

                # Check for virtually empty
    #            elif self._check_element(By.XPATH, "//div[@class='alert__content alert__content--density-dense']//span[text()='Container is virtually empty.']"):
    #                virtually_empty.append(container)
    #                print(f"Container is virtually empty {container}")

    #            print(f"Processed container {container}")
    #        except Exception as e:
    #            print(f"Error processing container {container}: {e}")

        # Save results to txt files
    #    self._save_to_file("invalid_routing.txt", invalid_routing)
    #    self._save_to_file("invalid_container.txt", invalid_container)
    #    self._save_to_file("virtually_empty.txt", virtually_empty)

    #    if self.own_driver:
    #        self.driver.quit()

    #    return invalid_routing, invalid_container, virtually_empty

    def _check_element(self, by, value):
        try:
            self.driver.find_element(by, value)
            #print(f"Element with {by}='{value}' found.")
            return True
        except NoSuchElementException:
            #print(f"Element with {by}='{value}' not found.")
            return False

    #def _save_to_file(self, filename, data):
    #    with open(filename, 'w') as f:
    #        for item in data:
    #            f.write(f"{item}\n")

    def inf_parse(self, sideline_integration, unbind_integration, fc_research_integration, interval=1):
        """
        Continuously process containers from the buffer and pass overages to SidelineIntegration.
        """
        try:
            self.navigate_to_tool()
            logging.info("DJ navigate_to_tool completed successfully")
        except Exception as e:
            logging.error(f"DJ navigate_to_tool FAILED — thread cannot proceed: {e}")
            return

        while True:
            try:
                if self.buffer:
                    container = self.buffer.popleft()
                    logging.info(f"DJ processing container: {container} (buffer remaining: {len(self.buffer)})")
                    result = self.process_container(container)
                    logging.info(f"DJ result for {container}: {result}")
                    if result is None:
                        logging.warning(f"DJ got None result for {container} — container dropped")
                    elif result == 'invalid_container':
                        if not container in self.repeat_buster:
                            self.repeat_buster.append(container)
                            si = SlackIntegration()
                            si.send_message('https://hooks.slack.com/workflows/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', {"csx": container})
                        sideline_integration.add_container_to_buffer(container, 'overage')
                        logging.info(f"DJ -> Sideline: {container} (overage)")
                    elif result == 'invalid_routing':
                        unbind_integration.add_to_buffer(container)
                        logging.info(f"DJ -> Unbind: {container}")
                    #elif result == 'virtually_empty':
                        #fc_research_integration.add_containers_to_buffer([container])

                time.sleep(interval)  # Avoid busy waiting
            except Exception as e:
                logging.error(f"DJ error processing iteration: {e}", exc_info=True)

    def navigate_to_tool(self):
        # Logic to navigate to the tool (e.g., the code before the loop in parse_containers)
        # Navigate directly to the specific process
        #self.driver.get('https://web.iad.prod.taskui.aft.amazon.dev/?listingID=eb105a2a-bcba-4aa9-9b56-5ea2d9e22b5b#initialized')
        #print("Navigated directly to the process 1208.")

        # Navigate to the FC menu with the building passed in from config
        fc = FC  # Replace with the actual FC value from your config
        self.driver.get(f'https://fcmenu-iad-regionalized.corp.amazon.com/{fc}')
        print(f"Navigated to the FC menu for {fc}.")

        # Simulate sending keys "1208" and pressing Enter
        try:
            body = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            body.send_keys("1208" + Keys.RETURN)
            print("Entered '1208' and pressed Enter.")
        except Exception as e:
            print(f"Error sending keys to input: {e}")
        
        try:
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='list-item-text__primary']//span[@class='text' and text()='Directed Jackpot']"))
            ).click()
        
        except Exception as e:
            print(f"Error: {e}")

    def process_container(self, container):
        """
        Logic to process a container and return the result category (invalid_container, etc.).
        """
        # Similar to the logic inside the parse_containers method but without the loop.
        try:
            # Check if the current URL is the undesired one
            fc = FC  # Get the FC from your config
            undesired_url = f'https://fcmenu-iad-regionalized.corp.amazon.com/{fc}'
            if self.driver.current_url == undesired_url:
                logging.info(f"Detected undesired URL: {undesired_url}. Navigating back to the tool.")
                self.navigate_to_tool()

            # Look for Application Error
            application_error_xpath = "//div[@class='alert__title alert__title--density-normal alert__title--with-icon-ltr']//span[@class='text' and text()='Application Error']"
            if self._check_element(By.XPATH, application_error_xpath):
                logging.error("Application Error detected. Navigating back to the tool.")
                self.navigate_to_tool()
                #return

            # Execute JavaScript to simulate the scanner input
            self.driver.execute_script(f"wavelinkScannerProcessed('{container}', '', '', '', '');")
            time.sleep(1)  # Wait for 1 second to allow the page to process the input

            # Check for invalid routing
            if self._check_element(By.XPATH, "//div[@class='alert__content alert__content--density-dense']//span[text()='Container has invalid routing.']"):
                 # Look for the routing profile
                try:
                    # Wait for up to 3 seconds for the element to be present
                    routing_profile_elements = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "text font-weight-bold"))
                    )
                    routing_profile = routing_profile_elements[0].text.strip()
                    if routing_profile in ['DAMAGED', 'QUARANTINE']:
                        return 'good_work'
                    else:
                        logging.info(f"Invalid Routing Profile: {routing_profile}")
                        return 'invalid_routing'
                except Exception as e:
                    logging.error("Routing profile element not found.")
                    print("Didnt find routing info, still invalid")
                    return 'invalid_routing'

            # Check for invalid container
            elif self._check_element(By.XPATH, "//div[@class='alert alert--variant-error theme--variant-error alert--density-dense']//span[text()='Container is not valid.']"):
                return 'invalid_container'

            # Check for virtually empty
            elif self._check_element(By.XPATH, "//div[@class='alert__content alert__content--density-dense']//span[text()='Container is virtually empty.']"):
                return 'virtually_empty'

            else:
                return 'good_work'
        except Exception as e:
            print(f"Error processing container {container}: {e}")

    def close(self):
        if self.own_driver:
            self.driver.quit()
