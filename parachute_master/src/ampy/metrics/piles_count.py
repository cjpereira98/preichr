import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.ont_base import OntBaseIntegration
from metrics.abstract_metric import AbstractMetric

class PilesCountMetric(AbstractMetric):

    def __init__(self, driver=None):
        super().__init__(driver)
        self.integration = OntBaseIntegration(self.driver)

    def _calculate_metric(self, designation):
        df = self.integration.get_piles_data(designation)
        
        # Filter for night audits with audit number 4
        filtered_df = df[(df['Audit shift'] == 'Nights') & (df['Audit number'] == 4)]

        if designation == 'prior-day':
            # Get the sum of 'Total units' for the previous day
            result = filtered_df['Total units'].sum()
        else:
            # Get the average of 'Total units' sums for the specified time frame
            grouped = filtered_df.groupby(['Audit date'])['Total units'].sum()
            result = grouped.mean()
        
        return result

    def get_prior_day(self):
        return self._calculate_metric('prior-day')

    def get_wtd(self):
        return self._calculate_metric('wtd')

    def get_prior_week(self):
        return self._calculate_metric('prior-week')
