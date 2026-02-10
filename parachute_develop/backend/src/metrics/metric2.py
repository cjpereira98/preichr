from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration

class Metric2(ABC):
    
    def __init__(self, driver=None):
        # Use the provided driver or create an authenticated driver if none is provided
        self.driver = driver or FirefoxIntegration.get_authenticated_driver()

    @abstractmethod
    def get_day(self, process ,date: datetime):
        pass

    @abstractmethod
    def get_week(self, process, date: datetime):
        pass

    @abstractmethod
    def get_month(self, process, date: datetime):
        pass

    @abstractmethod
    def get_intraday(self, process, start_date: datetime, end_date: datetime):
        pass

    @abstractmethod
    def get_shift(self, process, date: datetime, shift):
        pass

    def close_driver(self):
        if self.driver:
            self.driver.quit()
