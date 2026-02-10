import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric

class PalletCartonsLoaded(Metric):
    def get(self, specificity: str, start: datetime = None, end: datetime = None):
        # Check specificity for shift-based logic or a custom time range
        if specificity in ['FHD', 'BHD', 'FHN', 'BHN']:
            return self.aggregate_shift(specificity)
        elif specificity == 'time-range' and start and end:
            return self.fetch_and_sum_data(start, end)
        else:
            raise ValueError("Invalid specificity or missing start/end dates")

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
        
        total_sum = 0
        for day, start_hour, end_hour in shift_times[shift]:
            # Convert local start and end times to UTC+3
            start_dt = local_tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour))
            
            # Calculate end_dt as exactly 12 hours after start_dt for overnight shifts
            if end_hour < start_hour:  # Overnight shift (e.g., 6PM - 6AM)
                end_dt = start_dt + timedelta(hours=12)
            else:
                end_dt = datetime.combine(day, datetime.min.time()) + timedelta(hours=end_hour)
            
            # Fetch data and aggregate
            total_sum += self.fetch_and_sum_data(start_dt, end_dt)

        return total_sum

    def fetch_and_sum_data(self, start: datetime, end: datetime):
        # Prepare URL with the specified time range using local time in 'YYYY/MM/DD' format
        start_date = start.strftime('%Y/%m/%d')
        end_date = end.strftime('%Y/%m/%d')
        start_hour = start.strftime('%H')
        end_hour = end.strftime('%H')
        
        # Generate URL
        url = f"https://fclm-portal.amazon.com/reports/unitsRollup?reportFormat=CSV&warehouseId=SWF2&jobAction=PalletLoaded&startDate={start_date}&startHour={start_hour}&startMinute=0&endDate={end_date}&endHour={end_hour}&endMinute=0"
        #print(f"Fetching data from URL: {url}")
        
        # Execute JavaScript to download the file directly
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        
        # Generate expected filename for the downloaded CSV
        start_str_utc = start.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        end_str_utc = end.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        download_filename = f"unitsRollup-SWF2-PalletLoaded-{start_str_utc}-{end_str_utc}.csv"
        download_path = os.path.join(os.getcwd(), download_filename)
        
        # Wait for the file to download
        timeout = 30
        while not os.path.exists(download_path) and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if not os.path.exists(download_path):
            raise Exception("Failed to download the file within the timeout period.")
        
        time.sleep(5)

        # Parse the downloaded CSV file
        total_value = 0
        with open(download_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 8 and row[6] == 'Case':  # Checking if the value in column G is 'Case'
                    try:
                        total_value += float(row[8])  # Adding values in column I
                    except ValueError:
                        pass  # Skip non-numeric values

        # Clean up by deleting the downloaded file
        os.remove(download_path)

        return total_value

def main():
    pcl = PalletCartonsLoaded()
    start = datetime.strptime("06:00 10/27/24", "%H:%M %m/%d/%y")
    end = datetime.strptime("05:59 11/03/24", "%H:%M %m/%d/%y")
    specificities = ['FHD', 'BHD', 'FHN', 'BHN']

    for specificity in specificities:
        print(f"Running get() for specificity: {specificity}")
        result = pcl.get(specificity=specificity, start=start, end=end)
        print(f"Result for {specificity}: {result}")

if __name__ == "__main__":
    main()