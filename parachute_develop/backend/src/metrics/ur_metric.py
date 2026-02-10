from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from integrations.firefox import FirefoxIntegration
from integrations.ppr import URIntegration
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric2

class URMetric(Metric2):
    
    def __init__(self, driver=None):
        # Call the parent class constructor to initialize the driver
        super().__init__(driver)
        self.ur = URIntegration(self.driver)

    def get_day(self, process, date: datetime):
        """
        Retrieve PPR data for a specific day.
        """
        try:
            return self.ur.get_day(process, date)
        except Exception as e:
            print(f"Error fetching day data: {e}")
            return None

    def get_week(self, process, date: datetime):
        """
        Retrieve PPR data for the week containing the given date.
        """
        return None

    def get_month(self, process, date: datetime):
        """
        Retrieve PPR data for the month containing the given date.
        """
        return None

    def get_intraday(self, process, start_date: datetime, end_date: datetime):
        """
        Retrieve PPR data for a specific intraday range.
        """
        try:
            return self.ur.get_intraday(process, start_date, end_date)
        except Exception as e:
            print(f"Error fetching intraday data: {e}")
            return None
        
    def get_shift(self, process, start_date: datetime, end_date: datetime):
        """
        Retrieve PPR data for a specific intraday range.
        
        try:
            return self.ppr.get_intraday(process, start_date, end_date)
        except Exception as e:
            print(f"Error fetching intraday data: {e}")
            return None
        """
        pass
    """
    def _parse_data(self, raw_data):
        
        
        try:
            # Example parsing logic
            return [line.split(",") for line in raw_data.split("\n") if line]
        except Exception as e:
            print(f"Error parsing data: {e}")
            return None
    """

