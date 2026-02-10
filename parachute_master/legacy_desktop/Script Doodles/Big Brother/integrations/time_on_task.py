import time
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.firefox import FirefoxIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import FC

class TimeOnTaskIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.firefox = FirefoxIntegration()
            self.driver = self.firefox.get_authenticated_driver()

    def get_on_prem_logins(self, url):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 30)
        download_link = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@data-click-metric="CSV" and contains(@href, "reportFormat=CSV")]')))
        download_link.click()
        time.sleep(5)  # Ensure the download completes

# Usage example:
if __name__ == "__main__":
    tit = TimeOnTaskIntegration()
    tit.get_on_prem_logins(f"https://fclm-portal.amazon.com/reports/timeOnTask?reportFormat=HTML&warehouseId={FC}&startDateDay=2024%2F07%2F23&maxIntradayDays=30&spanType=Intraday&startDateIntraday=2024%2F07%2F23&startHourIntraday=9&startMinuteIntraday=0&endDateIntraday=2024%2F07%2F23&endHourIntraday=9&endMinuteIntraday=15")
