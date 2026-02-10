import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric
#from metrics.combined_cartons import CombinedCartons

class ReceiveDockHours(Metric):
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
        
        #total_cartons = 0
        total_hours = 0
        #combined_cartons = CombinedCartons(self.driver)

        #total_cartons = combined_cartons.get(shift)
        
        for day, start_hour, end_hour in shift_times[shift]:
            # Local start and end times to pass into CombinedCartons
            start_dt = local_tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour))
            
            if end_hour < start_hour:  # Overnight shift
                end_dt = start_dt + timedelta(hours=12)
            else:
                end_dt = datetime.combine(day, datetime.min.time()) + timedelta(hours=end_hour)
            
            # Get CombinedCartons for the shift
            #total_cartons += combined_cartons.get(shift)
            
            # Fetch IB Hours and aggregate
            total_hours += self.fetch_and_sum_hours(start_dt, end_dt)
        
        # Calculate IBCPLH as total cartons divided by total hours
        if total_hours > 0:
            return total_hours
        else:
            return 0

    def fetch_and_sum_hours(self, start: datetime, end: datetime):
        # Prepare URL with specified time range
        start_date = start.strftime('%Y/%m/%d')
        end_date = end.strftime('%Y/%m/%d')
        start_hour = start.strftime('%H')
        end_hour = end.strftime('%H')
        
        url = f"https://fclm-portal.amazon.com/reports/processPathRollup?reportFormat=CSV&warehouseId=SWF2&startDateDay={end_date}&maxIntradayDays=1&spanType=Intraday&startDateIntraday={start_date}&startHourIntraday={start_hour}&startMinuteIntraday=0&endDateIntraday={end_date}&endHourIntraday={end_hour}&endMinuteIntraday=0&_adjustPlanHours=on&_hideEmptyLineItems=on&employmentType=AllEmployees"
        #print(f"Fetching data from URL: {url}")
        
        # Execute JavaScript to download the file directly
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        
        # Define download file name based on the given pattern
        start_str_utc = start.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        end_str_utc = end.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        download_filename = f"processPathReport-SWF2-Intraday-{start_str_utc}-{end_str_utc}.csv"
        download_path = os.path.join(os.getcwd(), download_filename)
        
        # Wait for the file to download
        timeout = 30
        while not os.path.exists(download_path) and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if not os.path.exists(download_path):
            raise Exception("Failed to download the file within the timeout period.")
        
        # Parse the downloaded CSV file
        total_hours = 0
        with open(download_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 8 and row[3] == 'Receive Dock':  # Column D = 'Receive Dock'
                    try:
                        total_hours += float(row[8])  # Column I contains the hours
                    except ValueError:
                        pass  # Skip non-numeric values

        # Clean up by deleting the downloaded file
        os.remove(download_path)

        return total_hours
    
def main():
    rd_hours = ReceiveDockHours()
    start = datetime.strptime("06:00 10/27/24", "%H:%M %m/%d/%y")
    end = datetime.strptime("05:59 11/03/24", "%H:%M %m/%d/%y")
    specificities = ['FHD', 'BHD', 'FHN', 'BHN']

    for specificity in specificities:
        print(f"Running get() for specificity: {specificity}")
        result = rd_hours.get(specificity=specificity, start=start, end=end)
        print(f"Result for {specificity}: {result}")

if __name__ == "__main__":
    main()