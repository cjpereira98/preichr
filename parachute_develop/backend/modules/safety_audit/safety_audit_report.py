import os
import sys
import time
from datetime import datetime
import pandas as pd

# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from integrations.outlook import OutlookIntegration
from integrations.apollo import ApolloIntegration
from integrations.time_on_task import TimeOnTaskIntegration

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import FC, OWNER

def generate_and_send_report():
    audit_id = 20188
    start_date = '2024-07-15 00:00:00'
    end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get the audit results
    results_df = pd.DataFrame(ApolloIntegration.get_audit_results(audit_id, start_date, end_date))

    # Load the employee list
    employee_list_path = os.path.join(os.path.dirname(__file__), f'employeeList-{FC}.csv')
    employee_list_df = pd.read_csv(employee_list_path)

    # Determine which employees have not been audited
    audited_logins = results_df['Associate Login'].unique()
    non_audited_df = employee_list_df[~employee_list_df['User ID'].isin(audited_logins)]

    # Save the overall compliance report
    overall_compliance_path = os.path.join(os.path.dirname(__file__), 'overall_compliance_report.csv')
    non_audited_df.to_csv(overall_compliance_path, index=False)

    # Load the time off task data
    time_off_task_path = os.path.join(os.path.dirname(__file__), 'timeOffTask.csv')
    time_off_task_df = pd.read_csv(time_off_task_path)

    # Create the on-prem report
    on_prem_report_df = time_off_task_df[time_off_task_df['Employee ID'].isin(non_audited_df['Employee ID'])]
    on_prem_report_path = os.path.join(os.path.dirname(__file__), 'on_prem_report.csv')
    on_prem_report_df.to_csv(on_prem_report_path, index=False)

    # Generate the email body
    manager_summary = non_audited_df['Manager Name'].value_counts().reset_index()
    manager_summary.columns = ['Manager Name', 'Non-Compliant Employees']

    email_body = f"""
    <html>
    <body>
    <h2>Safety Audit Report</h2>
    <p>Please find attached the reports for associates who have not yet been audited as of {end_date}. The on prem will list AAs currently on site that have not been audited.</p>
    <h3>Manager Summary</h3>
    <table border="1">
        <tr>
            <th>Manager Name</th>
            <th>Non-Compliant Employees</th>
        </tr>
    """
    for _, row in manager_summary.iterrows():
        email_body += f"""
        <tr>
            <td>{row['Manager Name']}</td>
            <td>{row['Non-Compliant Employees']}</td>
        </tr>
        """
    email_body += """
    </table>
    </body>
    </html>
    """

    current_date = datetime.now().strftime('%Y-%m-%d')

    # Send the email
    outlook = OutlookIntegration()
    outlook.create_html_email(
        to_addresses=[f'{FC}-boss@amazon.com', f'{OWNER}@amazon.com'],
        subject=f'Safety Audit Report - {current_date}',
        html_body=email_body,
        attachments=[overall_compliance_path, on_prem_report_path],
        send_immediately=True
    )
    time.sleep(100)

if __name__ == "__main__":
    generate_and_send_report()
