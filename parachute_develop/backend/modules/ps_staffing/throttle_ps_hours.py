import os
import sys
import glob
import time
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from integrations.time_on_task import TimeOnTaskIntegration
from integrations.ppr import ProcessPathRollupIntegration
from integrations.outlook import OutlookIntegration
from integrations.firefox import FirefoxIntegration
from integrations.employee_roster import RosterIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import FC

def rename_downloaded_file(pattern, new_name):
    files = glob.glob(pattern)
    if files:
        os.rename(files[0], new_name)
        return new_name
    else:
        raise FileNotFoundError(f"No file matching pattern {pattern} found")

def clean_up_files(pattern):
    files = glob.glob(pattern)
    for file in files:
        os.remove(file)

def get_recent_15_min_window():
    now = datetime.now()
    # Subtract 15 minutes to get the valid window
    window_end = now - timedelta(minutes=30)
    # Round down to the nearest 15-minute increment
    window_start = window_end.replace(minute=(window_end.minute // 15) * 15, second=0, microsecond=0)
    window_end = window_start + timedelta(minutes=15)
    return window_start, window_end

def download_active_problem_solvers():
    # Get an authenticated driver
    firefox_integration = FirefoxIntegration()
    driver = firefox_integration.get_authenticated_driver()

    # Get the most recent 15-minute window at least 15 minutes before current time
    start_time, end_time = get_recent_15_min_window()

    start_date = start_time.strftime("%Y-%m-%dT%H:%M:%S.000")
    end_date = end_time.strftime("%Y-%m-%dT%H:%M:%S.000")

    # Get active problem solvers
    ppr = ProcessPathRollupIntegration(driver)
    url = f"https://fclm-portal.amazon.com/reports/functionRollup?warehouseId={FC}&spanType=Intraday&startDate={start_date}&endDate={end_date}&reportFormat=HTML&processId=01002980"
    ppr.get_active_problem_solvers(url)
    
    active_ps_pattern = f'functionRollupReport-{FC}-*.csv'
    active_ps_file = rename_downloaded_file(active_ps_pattern, 'throttle_ps_hours_active_problem_solvers.csv')

    driver.quit()

    # Load the CSV file
    active_ps = pd.read_csv(active_ps_file)

    # Clean up files
    clean_up_files(active_ps_pattern)
    if os.path.exists(active_ps_file):
        os.remove(active_ps_file)

    return active_ps

if __name__ == "__main__":
    active_problem_solvers = download_active_problem_solvers()

    # Get unique Employee IDs
    unique_employee_ids = active_problem_solvers['Employee Id'].unique()

    # Get the employee badge conversion dictionary
    roster_integration = RosterIntegration()
    conversion_dict = roster_integration.get_employee_badge_conversion_dict()
    roster_integration.close()

    # Convert Employee IDs to Badge Numbers
    badge_numbers = [conversion_dict[eid] for eid in unique_employee_ids if eid in conversion_dict]
    print(badge_numbers)

    print(active_problem_solvers.head())
