import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.aft_transship_hub import AFTTransshipHubIntegration
from metrics.abstract_metric import AbstractMetric

class TiToReconcileMetric(AbstractMetric):
    def __init__(self, driver=None):
        super().__init__(driver)
        self.csv_filename = 'AFT Transshipment Hub.csv'

    def get_prior_day(self):
        # Check if the file exists, if not, download it
        if not os.path.exists(self.csv_filename):
            aft_integration = AFTTransshipHubIntegration(self.driver)
            aft_integration.download_csv()

        # Load the data and calculate the metric
        try:
            df = pd.read_csv(self.csv_filename)
            #print(df)
            count = df[df['YMS Arrival Time'].notna()].shape[0]
            os.remove(self.csv_filename)
            return count
        except Exception as e:
            print(f"Error reading {self.csv_filename}: {e}")
            return -1

    def get_wtd(self):
        return -1

    def get_prior_week(self):
        return -1
