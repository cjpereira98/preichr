import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric

class DecantUPH(Metric):
    def get(self, specificity: str, start: datetime = None, end: datetime = None):
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
        
        total_units = 0
        total_hours = 0
        
        for day, start_hour, end_hour in shift_times[shift]:
            # Convert times for each segment within the shift
            start_dt = local_tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour))
            if end_hour < start_hour:  # Overnight shift
                end_dt = start_dt + timedelta(hours=12)
            else:
                end_dt = datetime.combine(day, datetime.min.time()) + timedelta(hours=end_hour)
            
            # Fetch data from both sources and aggregate
            total_units += self.fetch_and_sum_data(start_dt, end_dt, process_id='1003019')
            total_units += self.fetch_and_sum_data(start_dt, end_dt, process_id='1003033')
            total_hours += self.fetch_and_sum_hours(start_dt, end_dt, process_id='1003019')
            total_hours += self.fetch_and_sum_hours(start_dt, end_dt, process_id='1003033')

        if total_hours > 0:
            return total_units / total_hours
        else:
            return 0

    def fetch_and_sum_data(self, start: datetime, end: datetime, process_id: str):
        start_date = start.strftime('%Y/%m/%d')
        end_date = end.strftime('%Y/%m/%d')
        start_hour = start.strftime('%H')
        end_hour = end.strftime('%H')
        
        url = f"https://fclm-portal.amazon.com/reports/functionRollup?reportFormat=CSV&warehouseId=SWF2&processId={process_id}&maxIntradayDays=1&spanType=Intraday&startDateIntraday={start_date}&startHourIntraday={start_hour}&startMinuteIntraday=0&endDateIntraday={end_date}&endHourIntraday={end_hour}&endMinuteIntraday=0"
        
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        
        # Generate the download filename
        process_name = "Transfer In Dock" if process_id == '1003019' else "Receive-Support"
        start_str_utc = start.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        end_str_utc = end.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        download_filename = f"functionRollupReport-SWF2-{process_name}-Intraday-{start_str_utc}-{end_str_utc}.csv"
        download_path = os.path.join(os.getcwd(), download_filename)
        
        # Wait for the file to download
        timeout = 30
        while not os.path.exists(download_path) and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if not os.path.exists(download_path):
            print(download_path)
            raise Exception("Failed to download the file within the timeout period.")
        
        # Parse the downloaded CSV file
        units = 0
        with open(download_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 15 and ((process_id == '1003019' and row[14] == 'EACH' and row[15] == 'Total') or
                                      (process_id == '1003033' and row[1] == 'Decant Non-TI' and row[14] == 'EACH' and row[15] == 'Total')):
                    try:
                        units += float(row[16])  # Column Q
                    except ValueError:
                        pass  # Skip non-numeric values

        os.remove(download_path)
        return units

    def fetch_and_sum_hours(self, start: datetime, end: datetime, process_id: str):
        start_date = start.strftime('%Y/%m/%d')
        end_date = end.strftime('%Y/%m/%d')
        start_hour = start.strftime('%H')
        end_hour = end.strftime('%H')
        
        url = f"https://fclm-portal.amazon.com/reports/functionRollup?reportFormat=CSV&warehouseId=SWF2&processId={process_id}&maxIntradayDays=1&spanType=Intraday&startDateIntraday={start_date}&startHourIntraday={start_hour}&startMinuteIntraday=0&endDateIntraday={end_date}&endHourIntraday={end_hour}&endMinuteIntraday=0"
        
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        
        # Generate the download filename
        process_name = "Transfer In Dock" if process_id == '1003019' else "Receive-Support"
        start_str_utc = start.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        end_str_utc = end.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        download_filename = f"functionRollupReport-SWF2-{process_name}-Intraday-{start_str_utc}-{end_str_utc}.csv"
        download_path = os.path.join(os.getcwd(), download_filename)
        
        # Wait for the file to download
        timeout = 30
        while not os.path.exists(download_path) and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if not os.path.exists(download_path):
            raise Exception("Failed to download the file within the timeout period.")
        
        # Parse the downloaded CSV file
        hours = 0
        with open(download_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 10 and ((process_id == '1003019' and row[14] == 'EACH' and row[15] == 'Total') or
                                      (process_id == '1003033' and row[1] == 'Decant Non-TI' and row[14] == 'EACH' and row[15] == 'Total')):
                    try:
                        hours += float(row[10])  # Column K
                    except ValueError:
                        pass  # Skip non-numeric values

        os.remove(download_path)
        return hours
