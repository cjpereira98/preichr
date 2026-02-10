import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric

class ManualEditHours(Metric):
    def get(self, specificity: str):
        if specificity in ['FHD', 'BHD', 'FHN', 'BHN']:
            return self.aggregate_shift(specificity)
        else:
            raise ValueError("Invalid specificity")

    def aggregate_shift(self, shift: str):
        # Calculate the previous business week based on the current day
        today = datetime.now().date()
        most_recent_sunday = today - timedelta(days=today.weekday() + 1)  # Find most recent Sunday
        print(most_recent_sunday)
        previous_sunday = most_recent_sunday - timedelta(days=7)  # Move back one full week to previous Sunday
        
        # Define local timezone and shifts
        local_tz = pytz.timezone(os.environ.get('TZ', 'America/New_York'))
        shift_days = {
            'FHD': [(previous_sunday + timedelta(days=i)) for i in range(3)],  # Sun-Tues
            'BHD': [(previous_sunday + timedelta(days=i+4)) for i in range(3)], # Thurs-Sat
            'FHN': [(previous_sunday + timedelta(days=i)) for i in range(3)],   # Sun-Tues
            'BHN': [(previous_sunday + timedelta(days=i+4)) for i in range(3)]  # Thurs-Sat
        }
        shift_hours = {'FHD': (6, 18), 'BHD': (6, 18), 'FHN': (18, 6), 'BHN': (18, 6)}
        
        total_hours = 0
        for day in shift_days[shift]:
            total_hours += self.fetch_and_sum_manual_hours(day, shift)
        
        return total_hours

    def fetch_and_sum_manual_hours(self, day: datetime, shift: str):
        # Prepare the URL and filename
        start_date = day.strftime('%Y/%m/%d')
        #end_date = (day + timedelta(days=1 if shift in ['FHN', 'BHN'] else 0)).strftime('%Y/%m/%d')
        end_date = start_date

        url = f"https://fclm-portal.amazon.com/reports/audit/timeOnTask?reportFormat=CSV&warehouseId=SWF2&startDate={start_date}&endDate={end_date}"
        print(f"Fetching data from URL: {url}")
        
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        
        # Search for the downloaded file using a wildcard for the matching pattern
        download_pattern = f"functionTimeAssignmentAuditReport-SWF2-*-null-null.csv"
        timeout = 30
        download_path = None
        
        while timeout > 0:
            files = glob.glob(download_pattern)
            if files:
                download_path = files[0]  # Take the first matching file
                break
            time.sleep(1)
            timeout -= 1

        if not download_path or not os.path.exists(download_path):
            raise Exception("Failed to download the file within the timeout period.")
        
        time.sleep(5)
        
        # Parse the downloaded CSV file
        total_hours = 0
        with open(download_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 10:
                    try:
                        # Convert task start and end times using helper function
                        task_start = self.convert_to_datetime(row[3])
                    except ValueError:
                        continue  # Skip the row if it can't be parsed as a datetime
                    
                    print("I WAS ACTUALLY PARSED AS DATETIME")
                    # Check if within shift
                    if self.is_within_shift(task_start, shift):
                        # Check the 'aftli_rw' exclusion and add time differences accordingly
                        if row[9] != 'aftli_rw':
                            try:
                                if row[4]:  # Column E is not blank
                                    end_time = self.convert_to_datetime(row[4])
                                else:
                                    end_time = self.convert_to_datetime(row[10])  # Column K
                                total_hours += (end_time - task_start).total_seconds() / 3600  # Convert to hours
                            except ValueError:
                                continue  # Skip any rows with invalid end times

        os.remove(download_path)
        return total_hours

    @staticmethod
    def convert_to_datetime(date_str: str) -> datetime:
        # Strip timezone and parse
        clean_date_str = date_str[:-4].strip()
        return datetime.strptime(clean_date_str, '%Y/%m/%d %H:%M:%S')

    def is_within_shift(self, task_start: datetime, shift: str) -> bool:
        # Define shift hours
        shift_hours = {'FHD': (6, 18), 'BHD': (6, 18), 'FHN': (18, 6), 'BHN': (18, 6)}
        start_hour, end_hour = shift_hours[shift]

        # Check for regular or overnight shift
        if end_hour > start_hour:
            return start_hour <= task_start.hour < end_hour
        else:  # Overnight shift
            return task_start.hour >= start_hour or task_start.hour < end_hour
