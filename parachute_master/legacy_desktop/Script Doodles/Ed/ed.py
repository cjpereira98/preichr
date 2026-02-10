from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from datetime import datetime, timedelta

# Function to initialize the web driver
def initialize_driver():
    options = FirefoxOptions()
    #options.add_argument('--ignore-certificate-errors')
    #options.add_argument('--ignore-ssl-errors')
    return webdriver.Firefox(options=options)

# Function to wait for element to be clickable
def wait_for_clickable(driver, locator):
    return WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))

# Function to extract total pid cartons and total combined cartons
def extract_carton_totals(driver):
    # Find all elements with the specified class name
    elements = driver.find_elements(By.CLASS_NAME("label"))
    
    # Loop through the elements to find the one with the correct title and rel attribute
    pid_cartons = None
    combined_cartons = None
    for element in elements:
        title = element.get_attribute("title")
        rel = element.get_attribute("rel")
        if title and rel:
            if "PID Cartons" in title and rel == "4":
                pid_cartons = title.split(':')[-1].strip().replace(',', '')
            elif "Total Combined Cartons" in title and rel == "3":
                combined_cartons = title.split(':')[-1].strip().replace(',', '')
    
    return pid_cartons, combined_cartons

# Function to write data to CSV
def write_to_csv(data):
    with open('cartons.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

# Function to format date
def format_date(date):
    return date.strftime("%Y/%m/%d")

# Initialize web driver
driver = initialize_driver()

# Open the webpage
driver.get("https://monitorportal.amazon.com/igraph?SchemaName1=Service&DataSet1=Prod&Marketplace1=SWF2&HostGroup1=ALL&Host1=ALL&ServiceName1=AFTCartonDataService&MethodName1=CreateCartonFromFreightLabel&Client1=ALL&MetricClass1=NONE&Instance1=NONE&Metric1=CartonEventPublish.Created&Period1=FiveMinute&Stat1=sum&LiveData1=true&Label1=Manual%20Cartons&UserLabel1=Manual%20Cartons&SchemaName2=Service&ServiceName2=AFTInboundDirectorService&MethodName2=PendingCartonLockSQSConsumer&MetricClass2=HANDSCANNER&Instance2=ALL&Metric2=FirstPerformanceForCarton&Label2=cPrEditor%20NVF%20A&UserLabel2=cPrEditor%20NVF%20A&SchemaName3=Service&MetricClass3=UNKNOWN&Label3=cPrEditor%20NVF%20B&UserLabel3=cPrEditor%20NVF%20B&SchemaName4=Service&MetricClass4=PID&Label4=PID%20NVF&UserLabel4=PID%20NVF&SchemaName5=Service&MetricClass5=AROS&Label5=AROS%20NVF&UserLabel5=AROS%20NVF&SchemaName6=Service&MetricClass6=MARS&Label6=MARS%20NVF&UserLabel6=MARS%20NVF&SchemaName7=Service&MetricClass7=HANDSCANNER&Metric7=FirstPerformanceForTransInCarton&Label7=cPrEditor%20TransIn%20A&UserLabel7=cPrEditor%20TransIn%20A&SchemaName8=Service&MetricClass8=UNKNOWN&Label8=cPrEditor%20TransIn%20B&UserLabel8=cPrEditor%20TransIn%20B&SchemaName9=Service&MetricClass9=PID&Label9=PID%20TransIn&UserLabel9=PID%20TransIn&SchemaName10=Service&MetricClass10=AROS&Label10=AROS%20TransIn&UserLabel10=AROS%20TransIn&SchemaName11=Service&MetricClass11=MARS&Label11=MARS%20TransIn&UserLabel11=MARS%20TransIn&SchemaName12=Service&Marketplace12=NAFulfillment&ServiceName12=InventoryTransferService&MethodName12=ALL&MetricClass12=Client&Instance12=FCInboundRoutingService&Metric12=PalletBreakAssignmentDeltaCalculator.PALLETS_INCOMING_IN_NUM_CASES.SWF2-PalletBreak&YAxisPreference12=right&Label12=PR%20Cartons%20A&UserLabel12=PR%20Cartons%20A&SchemaName13=Service&Marketplace13=SWF2&ServiceName13=FCReceiveWebUIWebsite&MetricClass13=NONE&Instance13=NONE&Metric13=numCases&YAxisPreference13=left&Label13=PR%20Cartons%20B&UserLabel13=PR%20Cartons%20B&HeightInPixels=250&WidthInPixels=600&GraphTitle=SWF2%20Combined%20Cartons%20Created&DecoratePoints=true&GraphType=zoomer&StartTime1=2024-03-18T10%3A00%3A00Z&EndTime1=2024-03-18T22%3A00%3A00Z&FunctionExpression1=M1&FunctionLabel1=Manual%20Cartons&FunctionYAxisPreference1=left&FunctionExpression2=SUM%28M2%2C%20M3%2C%20M7%2C%20M8%29&FunctionLabel2=cPrEditor%20Cartons&FunctionYAxisPreference2=left&FunctionExpression3=SUM%28M4%2C%20M9%29&FunctionLabel3=PID%20Cartons&FunctionYAxisPreference3=left&FunctionExpression4=SUM%28M5%2C%20M10%29&FunctionLabel4=AROS%20Cartons&FunctionYAxisPreference4=right&FunctionExpression5=SUM%28M6%2C%20M11%29&FunctionLabel5=MARS%20Cartons&FunctionYAxisPreference5=left&FunctionExpression6=SUM%28M12%2C%20M13%29&FunctionLabel6=PR%20Cartons&FunctionYAxisPreference6=left&FunctionExpression7=SUM%28M1%2CM2%2CM3%2CM4%2CM5%2CM6%2CM7%2CM8%2CM9%2CM10%2CM11%2CM12%2CM13%29&FunctionLabel7=Total%20Combined%20Cartons%20%28sum%20of%20sums%3A%20%7Bsum%7D%29&FunctionYAxisPreference7=left&FunctionColor7=default")

time.sleep(10)

# Locate and set start date
start_date_input = wait_for_clickable(driver, (By.ID, "startDate"))
start_date_input.clear()
start_date = format_date(datetime.now() - timedelta(days=30))
start_date_input.send_keys(start_date)

# Locate and set end date
end_date_input = wait_for_clickable(driver, (By.ID, "endDate"))
end_date_input.clear()
end_date = format_date(datetime.now() - timedelta(days=30))
end_date_input.send_keys(end_date)

time.sleep(5)

# Click submit
submit_button = wait_for_clickable(driver, (By.ID, "graphMetricsButton"))
submit_button.click()
print("Clicking submit")

# Wait for the page to reload with the updated data
time.sleep(5)

# Extract carton totals
pid_cartons, combined_cartons = extract_carton_totals(driver)

# Write data to CSV
write_to_csv([start_date, combined_cartons, pid_cartons])

# Repeat the process for each date up to the current date
while end_date != format_date(datetime.now()):
    # Increment date by one day
    start_date = format_date(datetime.strptime(start_date, "%Y/%m/%d") + timedelta(days=1))
    end_date = format_date(datetime.strptime(end_date, "%Y/%m/%d") + timedelta(days=1))
    
    # Set new dates
    start_date_input.clear()
    start_date_input.send_keys(start_date)
    end_date_input.clear()
    end_date_input.send_keys(end_date)
    
    # Click submit
    submit_button.click()
    
    # Wait for the page to reload with the updated data
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
    
    # Extract carton totals
    pid_cartons, combined_cartons = extract_carton_totals(driver)
    
    # Write data to CSV
    write_to_csv([start_date, combined_cartons, pid_cartons])

# Close the browser
driver.quit()

