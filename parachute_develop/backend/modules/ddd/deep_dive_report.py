import os
import sys
from datetime import datetime, timedelta
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from metrics.piles_count import PilesCountMetric
from metrics.camp_metric import (
    IOL3DaysMetric, GIAMetric, PIDDPMOMetric, UISToteWranglerMetric, ATACCompletionMetric,
    FluidLoadSweepMetric, FailedShipMovesMetric, UCODPMOMetric, BusRouteMetric, GCAExpiredMetric,
    EPPAccuracyMetric, DIOTMetric
)
from metrics.ps_staffing import PsStaffingComplianceMetric, DaysPsHoursMetric, NightsPsHoursMetric
from metrics.ti_to_reconcile import TiToReconcileMetric
from metrics.iss_ticket_status import OpenTicketsMetric, SlaBufferHoursMetric
from integrations.firefox import FirefoxIntegration
from integrations.outlook import OutlookIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import TEST_EMAIL

def run_report(designation):
    # Initialize Firefox driver
    driver = FirefoxIntegration.get_authenticated_driver()

    # Initialize all metrics with the driver
    metrics = {
        'Piles Count': PilesCountMetric(driver),
        'IOL > 3 days': IOL3DaysMetric(driver),
        'GIA': GIAMetric(driver),
        'TI to Reconcile': TiToReconcileMetric(driver),
        'PID DPMO': PIDDPMOMetric(driver),
        'UIS Tote Wrangler Manual Percentage': UISToteWranglerMetric(driver),
        'ATAC Measurement Completion': ATACCompletionMetric(driver),
        'Fluid Load Sweep Compliance': FluidLoadSweepMetric(driver),
        'Failed Ship Moves': FailedShipMovesMetric(driver),
        'UCO DPMO': UCODPMOMetric(driver),
        'PS Staffing Compliance': PsStaffingComplianceMetric(driver),
        'Bus Route': BusRouteMetric(driver),
        'Days PS Hours': DaysPsHoursMetric(driver),
        'Nights PS Hours': NightsPsHoursMetric(driver),
        'GCA expired': GCAExpiredMetric(driver),
        'EPP Accuracy': EPPAccuracyMetric(driver),
        'DIOT': DIOTMetric(driver),
        'Open Tickets': OpenTicketsMetric(driver),
        'SLA Buffer Hours': SlaBufferHoursMetric(driver),
    }

    results = []
    for name, metric in metrics.items():
        if designation == 'prior-day':
            value = metric.get_prior_day()
        elif designation == 'wtd':
            value = metric.get_wtd()
        elif designation == 'prior-week':
            value = metric.get_prior_week()
        else:
            print(f"Unknown designation: {designation}")
            return
        results.append((name, value))
        print(f"{name} ({designation}): {value}")

    driver.quit()
    return results

def format_report_as_html(results):
    html_body = "<h2>Deep Dive Flash Report</h2><table border='1'><tr><th>Metric</th><th>Value</th></tr>"
    for name, value in results:
        html_body += f"<tr><td>{name}</td><td>{value}</td></tr>"

    html_body += "</table>"
    return html_body

if __name__ == "__main__":
    #print(os.getcwd())
    if len(sys.argv) != 2:
        print("Usage: python deep_dive_report.py [designation]")
        sys.exit(1)

    designation = sys.argv[1]
    results = run_report(designation)
    html_body = format_report_as_html(results)

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Send the report via Outlook
    outlook_integration = OutlookIntegration()
    outlook_integration.create_html_email(
        to_addresses=[f'{TEST_EMAIL}'],
        subject=f'Deep Dive Flash - {current_date}',
        html_body=html_body,
        send_immediately=True
    )
