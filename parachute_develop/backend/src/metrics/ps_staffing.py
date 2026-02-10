import os
import sys
from datetime import datetime, timedelta


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.abstract_metric import AbstractMetric
from integrations.ppr import ProcessPathRollupIntegration

class PsStaffingComplianceMetric(AbstractMetric):
    def get_prior_day(self):
        end_date_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        start_date_time = end_date_time - timedelta(days=1)
        integration = ProcessPathRollupIntegration(self.driver)
        hours = integration.get_problem_solve_hours(start_date_time, end_date_time)
        return hours / 1500 if hours else -1

    def get_wtd(self):
        return -1

    def get_prior_week(self):
        return -1

class DaysPsHoursMetric(AbstractMetric):
    def get_prior_day(self):
        start_date_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_date_time = start_date_time.replace(hour=18, minute=0)
        integration = ProcessPathRollupIntegration(self.driver)
        hours = integration.get_problem_solve_hours(start_date_time, end_date_time)
        return hours if hours else -1

    def get_wtd(self):
        return -1

    def get_prior_week(self):
        return -1

class NightsPsHoursMetric(AbstractMetric):
    def get_prior_day(self):
        end_date_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        start_date_time = end_date_time - timedelta(hours=12)
        integration = ProcessPathRollupIntegration(self.driver)
        #print(start_date_time, end_date_time)
        hours = integration.get_problem_solve_hours(start_date_time, end_date_time)
        return hours if hours else -1

    def get_wtd(self):
        return -1

    def get_prior_week(self):
        return -1