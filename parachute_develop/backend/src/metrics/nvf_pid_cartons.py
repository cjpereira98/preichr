import os
import csv
import time
from datetime import datetime, timedelta
import pytz
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metrics.metric import Metric

class NVFPIDCartons(Metric):
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
        target_tz = pytz.timezone('Etc/GMT-3')  # UTC+3 Timezone
        shift_times = {
            'FHD': [(previous_sunday + timedelta(days=i), 3, 15) for i in range(3)],  # Sun-Tues, 6AM-6PM
            'BHD': [(previous_sunday + timedelta(days=i+4), 3, 15) for i in range(3)], # Thurs-Sat, 6AM-6PM
            'FHN': [(previous_sunday + timedelta(days=i), 15, 3) for i in range(3)],   # Sun-Tues, 6PM-6AM (overnight)
            'BHN': [(previous_sunday + timedelta(days=i+4), 15, 3) for i in range(3)]  # Thurs-Sat, 6PM-6AM (overnight)
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
            
            # Convert times to UTC+3
            start_dt_utc3 = start_dt.astimezone(target_tz)
            end_dt_utc3 = end_dt.astimezone(target_tz)
            
            # Fetch data and aggregate
            total_sum += self.fetch_and_sum_data(start_dt_utc3, end_dt_utc3)

        return total_sum

    def fetch_and_sum_data(self, start: datetime, end: datetime):
        # Prepare URL with the specified time range and format with '%3A'
        start_str = start.strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ')
        end_str = end.strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ')

        #print(start_str)
        #print(end_str)
        
        url = f"https://monitorportal.amazon.com/mws?Action=GetGraph&Version=2007-07-07&SchemaName1=Service&DataSet1=Prod&Marketplace1=SWF2&HostGroup1=ALL&Host1=ALL&ServiceName1=AFTCartonDataService&MethodName1=CreateCartonFromFreightLabel&Client1=ALL&MetricClass1=NONE&Instance1=NONE&Metric1=CartonEventPublish.Created&Period1=OneMinute&Stat1=sum&LiveData1=true&Label1=Manual%20Cartons&UserLabel1=Manual%20Cartons&SchemaName2=Service&ServiceName2=AFTInboundDirectorService&MethodName2=PendingCartonLockSQSConsumer&MetricClass2=HANDSCANNER&Instance2=ALL&Metric2=FirstPerformanceForCarton&Label2=cPrEditor%20NVF%20A&UserLabel2=cPrEditor%20NVF%20A&SchemaName3=Service&MetricClass3=UNKNOWN&Label3=cPrEditor%20NVF%20B&UserLabel3=cPrEditor%20NVF%20B&SchemaName4=Service&MetricClass4=PID&Label4=PID%20NVF&UserLabel4=PID%20NVF&SchemaName5=Service&MetricClass5=AROS&Label5=AROS%20NVF&UserLabel5=AROS%20NVF&SchemaName6=Service&MetricClass6=MARS&Label6=MARS%20NVF&UserLabel6=MARS%20NVF&HeightInPixels=250&WidthInPixels=600&GraphTitle=SWF2%20NVF%20Only%20%22PID%22%20Cartons%20Created&DecoratePoints=true&GraphType=zoomer&StartTime1={start_str}&EndTime1={end_str}&FunctionExpression1=M1&FunctionLabel1=Manual%20Cartons&FunctionYAxisPreference1=left&FunctionExpression2=SUM%28M2%2C%20M3%29&FunctionLabel2=cPrEditor%20Cartons&FunctionYAxisPreference2=left&FunctionExpression3=SUM%28M4%29&FunctionLabel3=PID%20Cartons&FunctionYAxisPreference3=left&FunctionExpression4=SUM%28M5%29&FunctionLabel4=AROS%20Cartons&FunctionYAxisPreference4=right&FunctionExpression5=SUM%28M6%29&FunctionLabel5=MARS%20Cartons&FunctionYAxisPreference5=left&FunctionExpression6=SUM%28M1%2CM2%2CM3%2CM4%2CM5%2CM6%29&FunctionLabel6=Total%20%22PID%22%20Cartons%20%28sum%20of%20sums%3A%20%7Bsum%7D%29&FunctionYAxisPreference6=left&FunctionColor6=default&OutputFormat=CSV_TRANSPOSE"

        # Execute JavaScript to download the file directly
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        #print("I made it!")
        
        # Wait for the file to download
        download_path = os.path.join(os.getcwd(), 'data.csv')
        timeout = 30
        while not os.path.exists(download_path) and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if not os.path.exists(download_path):
            raise Exception("Failed to download the file within the timeout period.")
        
        # Parse the downloaded CSV file
        total_value = 0
        with open(download_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i >= 6 and len(row) > 5:
                    try:
                        total_value += float(row[6])
                    except ValueError:
                        pass  # Skip non-numeric values

        # Clean up by deleting the downloaded file
        os.remove(download_path)

        return total_value
    
def main():
    pid_cartons = NVFPIDCartons()
    start = datetime.strptime("06:00 10/27/24", "%H:%M %m/%d/%y")
    end = datetime.strptime("05:59 11/03/24", "%H:%M %m/%d/%y")
    specificities = ['FHD', 'BHD', 'FHN', 'BHN']

    for specificity in specificities:
        print(f"Running get() for specificity: {specificity}")
        result = pid_cartons.get(specificity=specificity, start=start, end=end)
        print(f"Result for {specificity}: {result}")

if __name__ == "__main__":
    main()
