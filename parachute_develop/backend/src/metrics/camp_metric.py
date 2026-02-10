import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.camp import CampIntegration
from metrics.abstract_metric import AbstractMetric

class CampMetricBase(AbstractMetric):

    def __init__(self, metric, driver=None):
        super().__init__(driver)
        self.metric = metric
        self.integration = CampIntegration(self.driver)

    def _calculate_metric(self, designation):
        return self.integration.get_metric_value(self.metric, designation)

    def get_prior_day(self):
        return self._calculate_metric('prior-day')

    def get_wtd(self):
        return self._calculate_metric('wtd')

    def get_prior_week(self):
        return self._calculate_metric('prior-week')

class IOL3DaysMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('iol_3_days', driver)

class GIAMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('gross_inventory_adjustments_dpmo', driver)

class PIDDPMOMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('aqat_pid_dpmo', driver)

class UISToteWranglerMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('uis_tote_wrangler_man_sort', driver)

class ATACCompletionMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('cat_cubiscan_compliance', driver)

class FluidLoadSweepMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('ixd_fl_sweeps', driver)

class FailedShipMovesMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('ship_failed_moves_deliver_coaching_compliance', driver)

class UCODPMOMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('total_fc_controllable_uco_dpmo', driver)

class BusRouteMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('ixd_uis_bus_route_audit_compliance', driver)

class GCAExpiredMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('receive_deliver_coaching_compliance', driver)

class EPPAccuracyMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('epp_accuracy', driver)

class DIOTMetric(CampMetricBase):
    def __init__(self, driver=None):
        super().__init__('dwelling_inventory_over_threshold', driver)
