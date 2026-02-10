import time
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class IssTicketPrioritizerIntegration:
    def __init__(self, driver=None):
        self.driver = driver

    def navigate_to_ticket_page(self):
        self.driver.get("https://iss.corp.amazon.com/ticket_prioritizer")
        # Wait for the site list to load
        wait = WebDriverWait(self.driver, 30)
        site_select = wait.until(EC.visibility_of_element_located((By.ID, "sites_list_sites")))
        site_select.send_keys(f"{FC}")

        time.sleep(5)

        # Wait for and click the 'Get Data' button
        get_data_button = wait.until(EC.element_to_be_clickable((By.ID, "submit_button")))
        get_data_button.click()

    def get_open_tickets(self):
        wait = WebDriverWait(self.driver, 30)
        # Wait for the first table to load and extract the number of open tickets
        table_1 = wait.until(EC.visibility_of_element_located((By.XPATH, "(//table[@class='table summary-table table-bordered table-condensed table-hover table-striped'])[1]")))
        open_tickets = table_1.find_element(By.XPATH, ".//tbody/tr[1]/td[2]").text
        return int(open_tickets)

    def get_sla_buffer_hours(self):
        wait = WebDriverWait(self.driver, 30)
        # Wait for the second table to load and extract the SLA buffer
        table_2 = wait.until(EC.visibility_of_element_located((By.XPATH, "(//table[@class='table summary-table table-bordered table-condensed table-hover table-striped'])[2]")))
        sla_buffer = table_2.find_element(By.XPATH, ".//tbody/tr[1]/td[2]").text
        return float(sla_buffer.replace(" hours", ""))
