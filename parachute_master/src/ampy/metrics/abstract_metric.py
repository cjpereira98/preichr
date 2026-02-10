from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class AbstractMetric(ABC):
    
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.driver = self.get_default_driver()
    
    @staticmethod
    def get_default_driver():
        options = Options()
        # Add your Firefox profile and options here
        driver = webdriver.Firefox(options=options)
        return driver

    @abstractmethod
    def get_prior_day(self):
        pass

    @abstractmethod
    def get_wtd(self):
        pass

    @abstractmethod
    def get_prior_week(self):
        pass
