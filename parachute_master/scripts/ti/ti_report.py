
import sys
import os

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ampy.integrations.aft_transship_hub import AFTTransshipHubIntegration

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.config import FC

if __name__ == "__main__":


    aft_integration = AFTTransshipHubIntegration()
    aft_integration.download_and_format_csv()

    # Run update_percent.py after downloading the csv file
    os.system('python update_percent.py')


    # Run update_reconciles.py after generating the data file
    os.system('python update_reconciles.py')

    if FC == 'SWF2':
        # Run auto_reconcile.py after updating the reconciles
        os.system('python auto_reconcile.py')


    # Run calculate_next_vrid.py after reconciling the freight
    os.system('python calculate_next_vrid.py')

    # Run send_ti_report.py after calculating the next vrid
    os.system('python send_ti_report.py')


