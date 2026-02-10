import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metrics.abstract_metric import AbstractMetric
from integrations.iss_ticket_prioritizer import IssTicketPrioritizerIntegration

class OpenTicketsMetric(AbstractMetric):
    def get_prior_day(self):
        integration = IssTicketPrioritizerIntegration(self.driver)
        integration.navigate_to_ticket_page()
        open_tickets = integration.get_open_tickets()
        return open_tickets if open_tickets is not None else -1

    def get_wtd(self):
        return -1

    def get_prior_week(self):
        return -1

class SlaBufferHoursMetric(AbstractMetric):
    def get_prior_day(self):
        integration = IssTicketPrioritizerIntegration(self.driver)
        integration.navigate_to_ticket_page()
        sla_buffer = integration.get_sla_buffer_hours()
        return sla_buffer if sla_buffer is not None else -1

    def get_wtd(self):
        return -1

    def get_prior_week(self):
        return -1
