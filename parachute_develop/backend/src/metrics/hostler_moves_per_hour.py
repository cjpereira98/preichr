from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric

class HostlerMovesPerHour(Metric):
    door_codes = {'DD151','DD152','DD153','DD201','DD202','DD203','DD204','DD205','DD206',
                  'DD207','DD208','DD209','DD210','DD211','DD212','DD213','DD214','DD215',
                  'DD216','DD217','DD218','DD219','DD220','DD221','DD222','DD223','DD224',
                  'DD225','DD226','DD227','DD228','DD229','DD230','DD231','DD232','DD301',
                  'DD302','DD303','DD304','DD305','DD306','DD307'}

    def get(self, specificity: str):
        if specificity in ['FHD', 'BHD', 'FHN', 'BHN']:
            return self.aggregate_shift(specificity)
        else:
            raise ValueError("Invalid specificity")

    def aggregate_shift(self, shift: str):
        # Calculate the previous business week based on the current day
        today = datetime.now().date()
        most_recent_sunday = today - timedelta(days=today.weekday() + 1)  # Find most recent Sunday
        previous_sunday = most_recent_sunday - timedelta(days=7)  # Move back one full week to previous Sunday

        # Define local timezone and shifts
        local_tz = pytz.timezone(os.environ.get('TZ', 'America/New_York'))
        shift_times = {
            'FHD': [(previous_sunday + timedelta(days=i), 6, 18) for i in range(3)],  # Sun-Tues, 6AM-6PM
            'BHD': [(previous_sunday + timedelta(days=i+4), 6, 18) for i in range(3)], # Thurs-Sat, 6AM-6PM
            'FHN': [(previous_sunday + timedelta(days=i), 18, 6) for i in range(3)],   # Sun-Tues, 6PM-6AM (overnight)
            'BHN': [(previous_sunday + timedelta(days=i+4), 18, 6) for i in range(3)]  # Thurs-Sat, 6PM-6AM (overnight)
        }

        total_moves = 0
        for day, start_hour, end_hour in shift_times[shift]:
            # Convert local start and end times to Unix timestamp in milliseconds
            start_dt = local_tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour))
            end_dt = start_dt + timedelta(hours=12) if end_hour < start_hour else datetime.combine(day, datetime.min.time()) + timedelta(hours=end_hour)
            
            from_timestamp = int(start_dt.timestamp() * 1000)
            to_timestamp = int(end_dt.timestamp() * 1000)

            # Prepare the URL and navigate to it
            url = f"https://trans-logistics.amazon.com/yms/eventHistory#/eventReport?yard=SWF2&fromDate={from_timestamp}&toDate={to_timestamp}&eventType=HOSTLER_CREATE"
            print(f"Fetching data from URL: {url}")
            self.driver.get(url)
            
            time.sleep(5)
            # Wait for the page to load and then fetch the CSV data
            try:
                # Instead of clicking the button, execute the fetchData() function
                self.driver.execute_script("angular.element(document.querySelector('.yms-button-primary-alt')).scope().fetchData()")
            except Exception as e:
                print(f"Error: {e}")
                raise Exception("Failed to execute fetchData() within the timeout period.")
            
            # Define file path for the downloaded report
            download_path = os.path.join(os.getcwd(), 'eventReport.csv')
            timeout = 30
            while not os.path.exists(download_path) and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            if not os.path.exists(download_path):
                raise Exception("Failed to download the file within the timeout period.")
            
            # Count the moves for the specified doors in the downloaded file
            with open(download_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and row[1] in self.door_codes:
                        total_moves += 1
            
            # Remove the file to avoid overwriting
            os.remove(download_path)

        # Calculate moves per hour and return
        return total_moves / 30  # Divide by 30 to get average per hour for the shift
