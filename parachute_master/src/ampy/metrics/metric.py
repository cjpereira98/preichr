from abc import ABC, abstractmethod
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration

class Metric(ABC):
    def __init__(self, driver=None):
        # Use the provided driver or create an authenticated driver if none is provided
        self.driver = driver or FirefoxIntegration.get_authenticated_driver()

    @abstractmethod
    def get(self, specificity: str, start: datetime = None, end: datetime = None):
        pass

    def close_driver(self):
        if self.driver:
            self.driver.quit()
