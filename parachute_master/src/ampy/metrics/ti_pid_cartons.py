import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric

class TIPIDCartons(Metric):
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
        #target_tz = pytz.timezone('Etc/GMT-3')  # UTC+3 Timezone
        shift_times = {
            'FHD': [(previous_sunday + timedelta(days=i), 6, 18) for i in range(3)],  # Sun-Tues, 6AM-6PM
            'BHD': [(previous_sunday + timedelta(days=i+4), 6, 18) for i in range(3)], # Thurs-Sat, 6AM-6PM
            'FHN': [(previous_sunday + timedelta(days=i), 18, 6) for i in range(3)],   # Sun-Tues, 6PM-6AM (overnight)
            'BHN': [(previous_sunday + timedelta(days=i+4), 18, 6) for i in range(3)]  # Thurs-Sat, 6PM-6AM (overnight)
        }
        
        total_sum = 0
        for day, start_hour, end_hour in shift_times[shift]:
            start_dt = local_tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour))
            
            # Calculate end_dt as exactly 12 hours after start_dt for overnight shifts
            if end_hour < start_hour:  # Overnight shift (e.g., 6PM - 6AM)
                end_dt = start_dt + timedelta(hours=12)
            else:
                end_dt = datetime.combine(day, datetime.min.time()) + timedelta(hours=end_hour)
            
            # Convert times to UTC+3
            #start_dt_utc3 = start_dt.astimezone(target_tz)
            #end_dt_utc3 = end_dt.astimezone(target_tz)
            
            # Fetch data and aggregate
            total_sum += self.fetch_and_sum_data(start_dt, end_dt)

        return total_sum

    def fetch_and_sum_data(self, start: datetime, end: datetime):
        # Prepare URL with the specified time range and format with '%3A'
        #start_str = start.strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ')
        #end_str = end.strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ')

        start_date_str = start.strftime('%Y%%2F%m%%2F%d')
        start_hour = start.strftime('%H')
        start_minute = start.strftime('%M')

        end_date_str = end.strftime('%Y%%2F%m%%2F%d')
        end_hour = end.strftime('%H')
        end_minute = end.strftime('%M')


        #print(start_date_str)
        #print(start_hour)
        #print(start_minute)
        #print(end_date_str)
        #print(end_hour)
        #print(end_minute)
        
        url = f"https://fclm-portal.amazon.com/reports/functionRollup?reportFormat=CSV&warehouseId=SWF2&processId=1003035&maxIntradayDays=1&spanType=Intraday&startDateIntraday={start_date_str}&startHourIntraday={start_hour}&startMinuteIntraday={start_minute}&endDateIntraday={end_date_str}&endHourIntraday={end_hour}&endMinuteIntraday={end_minute}"

        # Execute JavaScript to download the file directly
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        #print("I made it!")

        #modified_start = start + timedelta(hours=5)
        #modified_end = end + timedelta(hours=5)
        modified_start = start.astimezone(pytz.UTC)
        modified_end = end.astimezone(pytz.UTC)

        file_name_start = modified_start.strftime("functionRollupReport-SWF2-Case Transfer In-Intraday-%Y%m%d%H%M00-")
        file_name_end = modified_end.strftime("%Y%m%d%H%M00.csv")

        file_name = file_name_start + file_name_end
        
        print(file_name)
        # Wait for the file to download
        download_path = os.path.join(os.getcwd(), file_name)
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
            for i, row in enumerate(reader):
                if i >= 2 and len(row) > 14:  # Check row length to avoid out-of-range errors
                    try:
                        if row[14].strip() == 'Case':  # Check if column O is 'Case'
                            total_value += float(row[12])  # Sum the value in column M
                    except ValueError:
                        pass  # Skip non-numeric values

        # Clean up by deleting the downloaded file
        os.remove(download_path)

        return total_value
    
def main():
    pid_cartons = TIPIDCartons()
    start = datetime.strptime("06:00 10/27/24", "%H:%M %m/%d/%y")
    end = datetime.strptime("05:59 11/03/24", "%H:%M %m/%d/%y")
    specificities = ['FHD', 'BHD', 'FHN', 'BHN']

    for specificity in specificities:
        print(f"Running get() for specificity: {specificity}")
        result = pid_cartons.get(specificity=specificity, start=start, end=end)
        print(f"Result for {specificity}: {result}")

if __name__ == "__main__":
    main()