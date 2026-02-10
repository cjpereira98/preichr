import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric
from metrics.nvf_pid_cartons import PIDCartons
from metrics.pr_cartons import PRCartons



class CombinedCartons(Metric):
    def get(self, specificity: str, start: datetime = None, end: datetime = None, pid_value=None, pr_value=None):
        # Calculate PIDCartons and PRCartons only if not provided
        if pid_value is None:
            pid_cartons = PIDCartons(self.driver)
            pid_value = pid_cartons.get(specificity)
        
        if pr_value is None:
            pr_cartons = PRCartons(self.driver)
            pr_value = pr_cartons.get(specificity)
        
        # Return the sum of both metrics
        return pid_value + pr_value
