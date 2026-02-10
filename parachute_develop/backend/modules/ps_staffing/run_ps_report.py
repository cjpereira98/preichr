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
    # Subtract 30 minutes to get the valid window
    window_start = now - timedelta(minutes=30)
    # Round down to the nearest 15-minute increment
    window_start = window_start.replace(minute=(window_start.minute // 15) * 15, second=0, microsecond=0)
    window_end = window_start + timedelta(minutes=15)
    return window_start, window_end

def generate_report():
    # Load trainings.csv
    trainings = pd.read_csv('trainings.csv')
    
    # List of relevant roles
    relevant_roles = [
        "IB Dock Problem Solve", "Freight Identification & Problem Solve", 
        "Transfer Out Problem Solve", "ISS PS", "Receive/Prep Problem Solve",
        "Non-Con Problem Solve", "Decant Problem Solve", "Sort Problem Solve", 
        "Decant/Sort/UIS Problem Solve"
    ]

    # Filter trainings for relevant roles
    filtered_trainings = trainings[trainings['Role'].isin(relevant_roles)]

    # Get an authenticated driver
    firefox_integration = FirefoxIntegration()
    driver = firefox_integration.get_authenticated_driver()

    # Get current date for URL parameters
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_intraday = datetime.now().strftime("%Y/%m/%d")

    # Get the most recent 15-minute window at least 30 minutes before current time
    start_time, end_time = get_recent_15_min_window()
    start_hour_intraday = start_time.hour
    start_minute_intraday = start_time.minute
    end_hour_intraday = end_time.hour
    end_minute_intraday = end_time.minute

    # Get on-prem logins
    tit = TimeOnTaskIntegration(driver)
    tit.get_on_prem_logins(f"https://fclm-portal.amazon.com/reports/timeOnTask?reportFormat=HTML&warehouseId={FC}&startDateDay={current_date_intraday}&maxIntradayDays=30&spanType=Intraday&startDateIntraday={current_date_intraday}&startHourIntraday={start_hour_intraday}&startMinuteIntraday={start_minute_intraday}&endDateIntraday={current_date_intraday}&endHourIntraday={end_hour_intraday}&endMinuteIntraday={end_minute_intraday}")
    
    on_prem_pattern = f'timeOffTask-ppr-{FC}-*.csv'
    on_prem_file = rename_downloaded_file(on_prem_pattern, 'run_ps_report_on_prem.csv')
    

    # Get active problem solvers
    start_date_ps = start_time.strftime("%Y-%m-%dT%H:%M:%S.000")
    end_date_ps = end_time.strftime("%Y-%m-%dT%H:%M:%S.000")
    ppr = ProcessPathRollupIntegration(driver)
    ppr.get_active_problem_solvers(f"https://fclm-portal.amazon.com/reports/functionRollup?warehouseId={FC}&spanType=Intraday&startDate={start_date_ps}&endDate={end_date_ps}&reportFormat=HTML&processId=01002980")

    # Get active problem solvers
    #ppr = ProcessPathRollupIntegration(driver)
    #ppr.get_active_problem_solvers("https://fclm-portal.amazon.com/reports/functionRollup?warehouseId={FC}&spanType=Day&startDate=2024-07-23T00:00:00.000&endDate=2024-07-24T00:00:00.000&reportFormat=HTML&processId=01002980")

    active_ps_pattern = f'functionRollupReport-{FC}-*.csv'
    active_ps_file = rename_downloaded_file(active_ps_pattern, 'run_ps_report_active_problem_solvers.csv')
    
    # Load the CSV files
    on_prem = pd.read_csv(on_prem_file)
    active_ps = pd.read_csv(active_ps_file)

    driver.quit()

    # Merge data and filter for relevant roles and active status
    merged = pd.merge(on_prem, filtered_trainings, left_on='Employee ID', right_on='Emp ID')
    merged = merged[merged['STATUS'] == 'ACTIVE']
    available_associates = merged[~merged['Employee ID'].isin(active_ps['Employee Id'])]

    # Create a summary table and separate Excel files for each role
    summary = []
    attachments = []

    for role in relevant_roles:
        role_df = available_associates[available_associates['Role'] == role]
        role_count = role_df['Employee ID'].nunique()
        summary.append([role, role_count])
        
        file_name = f"{role.replace('/', '_').replace(' ', '_')}_available.xlsx"
        role_df_filtered = role_df[['Employee ID', 'Employee Name', 'Login', 'Manager', 'Role', 'Shift Pattern']]
        role_df_filtered.to_excel(file_name, index=False)
        full_path = os.path.abspath(file_name)
        print(f"Generated file for attachment: {full_path}")
        attachments.append(full_path)

    summary_df = pd.DataFrame(summary, columns=['Role', 'Available Associates'])
    total_unique_available = available_associates['Employee ID'].nunique()
    summary_df.loc[len(summary_df.index)] = ['Unique Available Problem Solvers', total_unique_available]

        # Create email body with the summary table
    email_body = """
    <html>
    <body>
    <h2>Good Morning!</h2>
    <p>Below, you will find a summary of the number of problem solvers not in path. Attached will be drilldowns for each process path.</p>
    <h3>Summary</h3>
    <table border="1">
        <tr>
            <th>Role</th>
            <th>Available Associates</th>
        </tr>
    """
    for _, row in summary_df.iterrows():
        email_body += f"""
        <tr>
            <td>{row['Role']}</td>
            <td>{row['Available Associates']}</td>
        </tr>
        """
    email_body += """
    </table>
    </body>
    </html>
    """

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    time.sleep(5)

    # Send email with attachments
    oi = OutlookIntegration()
    oi.create_html_email(
        to_addresses=[f'{FC}-boss@amazon.com'],
        subject=f'PS Staffing Report - {current_date}',
        html_body=email_body,
        attachments=attachments,
        send_immediately=True
    )

    # Clean up files
    clean_up_files(on_prem_pattern)
    clean_up_files(active_ps_pattern)
    if os.path.exists(on_prem_file):
        os.remove(on_prem_file)
    if os.path.exists(active_ps_file):
        os.remove(active_ps_file)
    for attachment in attachments:
        if os.path.exists(attachment):
            os.remove(attachment)

if __name__ == "__main__":
    generate_report()
