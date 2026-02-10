from selenium import webdriver
import os
import csv
import pandas
import time
from datetime import datetime, timedelta
import pytz
import sys
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from metrics.combined_cartons import CombinedCartons

class RCSortVol:
    def __init__(self):
        # Initialize the WebDriver (assuming you have a WebDriver instance)
        # self.driver = webdriver.Chrome()  # or any other driver you are using
        options = webdriver.FirefoxOptions()
        options.add_argument('--start-maximized')
        # Set up Firefox options for downloading files (if needed)
        download_dir = os.getcwd()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.driver = webdriver.Firefox(options=options)
        time.sleep(3)  # Wait for the browser to open
        self.driver.get("https://fclm-portal.amazon.com/")  # Open the login page
        time.sleep(20)  # Wait for authentication (adjust as needed)
        pass


    def get(self, site: str, last_n_days: int):
        end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=(last_n_days-1))  # Last N days

        while start_date <= end_date:
            start_date_str = start_date.strftime('%Y/%m/%d')
            
            url = f"https://fclm-portal.amazon.com/reports/processPathRollup?reportFormat=CSV&warehouseId={site}&spanType=Day&startDateDay={start_date_str}&maxIntradayDays=1&startHourIntraday=0&startMinuteIntraday=0&endHourIntraday=0&endMinuteIntraday=0&_adjustPlanHours=on&_hideEmptyLineItems=on&_rememberViewForWarehouse=on&employmentType=AllEmployees"
            
            # Execute JavaScript to download the file directly
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            
            start_str = start_date.strftime('%Y%m%d')
            end_str = (start_date + timedelta(days=1)).strftime('%Y%m%d')

            # Pattern to match: e.g., processPathReport-NYC1-Day-20240501040000-20240502040000.csv
            # But now we allow any digit before 0000
            pattern = f"processPathReport-{site}-Day-{start_str}0[0-9]0000-{end_str}0[0-9]0000.csv"
            download_path_pattern = os.path.join(os.getcwd(), pattern)

            # Wait for the file matching the pattern to appear
            timeout = 30
            download_path = None
            while timeout > 0:
                matches = glob.glob(download_path_pattern)
                if matches:
                    download_path = matches[0]
                    break
                time.sleep(1)
                timeout -= 1

            # Now download_path will be the first matched file path

            if not os.path.exists(download_path):
                raise Exception("Failed to download the file within the timeout period.")
            
            time.sleep(5)

            # Parse the downloaded CSV file
            each_units = 0
            ib_total_units = 0
            prep_units = 0
            with open(download_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) > 8 and row[3] == 'Each Receive - Total': 
                        try:
                            each_units = float(row[7])  # Column H contains the units
                        except ValueError:
                            pass  # Skip non-numeric values
                    elif len(row) > 8 and row[3] == 'IB Total': 
                        try:
                            ib_total_units = float(row[7])  # Column H contains the units
                        except ValueError:
                            pass
                    elif len(row) > 8 and row[3] == 'Prep Recorder - Total':  
                        try:
                            prep_units = float(row[7])  # Column H contains the units
                        except ValueError:
                            pass

            # Clean up by deleting the downloaded file
            os.remove(download_path)

            er_fpp = (each_units) / ib_total_units if ib_total_units > 0 else 0
            prep_fpp = (prep_units) / ib_total_units if ib_total_units > 0 else 0
            filename = 'master.csv'

            #write the data to the master file
            if not os.path.isfile(filename):
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Site', 'ER Units', 'Prep_Units', 'Total IB Units', 'ER_FPP', 'Prep_FPP'])

            # Append the row
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([start_date, site, each_units, prep_units, ib_total_units, er_fpp, prep_fpp])
            
            #iterate to the next day
            start_date += timedelta(days=1)
            
    
def main():


    rcsv = RCSortVol()
    sites_list = ['ABE8', 'ABQ2', 'AVP1', 'CLT2', 'GEU2', 'GEU5', 'FTW1', 'LGB8', 'MDW2', 'ONT8', 'GYR3', 'IND9', 'LAS1', 'LAX9', 'MEM1', 'MQJ1', 'SMF3', 'TEB9', 'FWA4', 'GYR2', 'IAH3', 'ORF2', 'RDU2', 'RFD2', 'RMN3', 'SBD1', 'SCK4', 'SWF2', 'VGT2', 'HGR6', 'HIA1', 'LBE1', 'RDU4', 'WBW2', 'BNA6', 'LAN2', 'PBI3', 'PPO4', 'RYY2', 'TMB8', 'HLI2', 'MIT2', 'POC1', 'POC2', 'POC3', 'TCY1', 'PSC2', 'TCY2']
    last_n_days = 6
    

    sites_list = ['ABE8', 'ABQ2']
    
    #last_n_days = 5S

    for site in sites_list:
        rcsv.get(site, last_n_days)

    rcsv.driver.quit()

if __name__ == "__main__":
    main()