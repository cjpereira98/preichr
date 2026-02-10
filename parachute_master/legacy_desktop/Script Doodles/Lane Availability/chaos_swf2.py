from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv
from datetime import datetime, timedelta
import pytz
import requests

# Config variables
site_main_page = "https://prod-na.dockflow.robotics.a2z.com/SWF2/wc/MainSorter1/Sorter?tagConfig=%7B%7D"
# Slack webhook URL
webhook_url = "https://hooks.slack.com/triggers/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"
site = "SWF2"
timezone = "America/New_York"
mp_limit = 250
rwc_limit = 400
fl_limit = 300
mp_floor = 80
rwc_floor = 225
fl_floor = 200
turbo_mode = True
#top_n_utilization = 5

def extract_table_data(driver):
    data = []

    # Wait briefly to let page fully render
    #time.sleep(15)
    print("Page loaded, starting to scrape data...")
    #with open("debug_page.html", "w", encoding="utf-8") as f:
    #    f.write(driver.page_source)
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "awsui_table-layout-fixed_wih1l_wyjfv_208"))
    )


   
    applicable_tables = driver.find_elements(By.CLASS_NAME, "awsui_table-layout-fixed_wih1l_wyjfv_208")
    #print(len(outer_divs))
    if len(applicable_tables) < 2:
        print("Got Stuck Again")
        print(len(applicable_tables))
        time.sleep(100000)
        raise Exception("Could not find enough tables with the specified class name.")

    target_table = applicable_tables[1]

    tbody = target_table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 5:
            continue

        # Extract arc href (3rd td)
        try:
            arc_div = tds[2].find_element(By.TAG_NAME, "div")
            inner_div = arc_div.find_element(By.TAG_NAME, "div")
            arc_href = inner_div.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            arc_href = None

        # Extract workcell hrefs (4th td)
        try:
            wc_div = tds[3].find_element(By.TAG_NAME, "div")
            wc_inner_div = wc_div.find_element(By.TAG_NAME, "div")
            links = wc_inner_div.find_elements(By.TAG_NAME, "a")
            workcell_hrefs = [link.get_attribute("href") for link in links]
        except:
            workcell_hrefs = []

        # Extract utilization integer (5th td)
        try:
            util_div = tds[4].find_element(By.TAG_NAME, "div")
            util_inner_div = util_div.find_element(By.TAG_NAME, "div")
            utilization = int(util_inner_div.text.strip())
        except:
            utilization = 0

        data.append({
            "arc_href": arc_href,
            "workcell_hrefs": workcell_hrefs,
            "utilization": utilization
        })

    return data

def check_last_hour(driver, ob_arcs_list):
    for arc in ob_arcs_list:
        if not arc["arc_href"]:
            arc["last_hour_vol"] = None
            continue

        driver.get(arc["arc_href"])
        print(f"Scraping last hour volume for: {arc['arc_href']}")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "awsui_table_wih1l_wyjfv_202"))
            )
            time.sleep(3)

            tables = driver.find_elements(By.CLASS_NAME, "awsui_table_wih1l_wyjfv_202")
            if len(tables) < 3:
                print(f"Not enough tables found at {arc['arc_href']}")
                arc["last_hour_vol"] = None
                continue

            target_table = tables[1]
            tbody = target_table.find_element(By.TAG_NAME, "tbody")
            row = tbody.find_element(By.TAG_NAME, "tr")
            tds = row.find_elements(By.TAG_NAME, "td")

            if len(tds) >= 3:
                if turbo_mode:
                    volume_div = tds[0].find_element(By.TAG_NAME, "div")
                    volume_text = str(4*int(volume_div.text.strip()))
                else:
                    volume_div = tds[2].find_element(By.TAG_NAME, "div")
                    volume_text = volume_div.text.strip()
                arc["last_hour_vol"] = int(volume_text.replace(",", ""))
            else:
                arc["last_hour_vol"] = None

        except Exception as e:
            print(f"Error scraping volume for {arc['arc_href']}: {e}")
            arc["last_hour_vol"] = None

def check_ob_lane_utilization(driver, ob_arcs_list):
    ob_lanes_list = {}

    for arc in ob_arcs_list:
        vol = arc.get("last_hour_vol", 0)
        targets = [wc for wc in arc["workcell_hrefs"] if wc and (
            wc.endswith("RWC4") or wc.endswith("DirectedPalletize") or wc.endswith("OBDockDoor")
        )]

        if not targets or vol is None:
            continue

        distributed_vol = vol / len(targets)

        for wc in targets:
            if wc not in ob_lanes_list:
                ob_lanes_list[wc] = 0
            ob_lanes_list[wc] += distributed_vol

    # Convert to list of dicts if needed later
    ob_lanes_list = [{"workcell_href": k, "hourly_vol": round(v)} for k, v in ob_lanes_list.items()]
    return ob_lanes_list

def add_projected_missed_diverts(ob_lanes_list):
    for entry in ob_lanes_list:
        href = entry["workcell_href"]
        vol = entry["hourly_vol"]
        threshold = 0

        if href.endswith("DirectedPalletize"):
            threshold = mp_limit
        elif href.endswith("RWC4"):
            threshold = rwc_limit
        elif href.endswith("OBDockDoor"):
            threshold = fl_limit
        else:
            entry["projected_missed_diverts"] = None
            continue

        projected_missed = vol - threshold
        entry["projected_missed_diverts"] = projected_missed if projected_missed > 0 else 0

    ob_lanes_list.sort(key=lambda x: x["projected_missed_diverts"] or 0, reverse=True)

    return ob_lanes_list

def reduce_workcell_links(ob_lanes_list):
    ob_lanes_no_links = []

    for entry in ob_lanes_list:
        full_href = entry["workcell_href"]
        parts = full_href.strip("/").split("/")

        if len(parts) >= 2:
            workcell_name = parts[-2]
        else:
            workcell_name = "UNKNOWN"

        ob_lanes_no_links.append({
            "workcell_name": workcell_name,
            "hourly_vol": entry["hourly_vol"],
            "projected_missed_diverts": entry["projected_missed_diverts"]
        })

    return ob_lanes_no_links


def format_and_send_update(ob_lanes_list, fl_rate, fl_hours):
    # Format into table string
    table_lines = ["Workcell HREF     " + "Hourly Volume     " + "Projected Missed Diverts"]
    table_lines.append("-" * 80)
    
    ob_lanes_no_links = reduce_workcell_links(ob_lanes_list)

    for entry in ob_lanes_no_links:
        if entry["workcell_name"].startswith("DD"):
            wc = entry["workcell_name"].ljust(24) #three less
        elif entry["workcell_name"].startswith("RT"):
            wc = entry["workcell_name"].ljust(21)
        else:
            wc = entry["workcell_name"].ljust(20)
        #wc = entry["workcell_name"]
        vol = entry["hourly_vol"]
        if entry["projected_missed_diverts"] > 50:
            table_lines.append(wc + str(vol).ljust(26) + str(entry["projected_missed_diverts"]))

    table_lines.append("FL Rate: " + str(fl_rate))
    table_lines.append("FL HC: " + str(fl_hours*4))

    table_text = "\n".join(table_lines)

    # Prepare JSON payload
    payload = {
        "Table": table_text
    }

    

    # Send POST request
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Slack message sent.")
        else:
            print(f"❌ Slack error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Slack message: {e}")

def get_ur_jobs(driver, func, start: datetime, end: datetime):
    # Prepare URL with the specified time range using local time in 'YYYY/MM/DD' format
    start_date = start.strftime('%Y/%m/%d')
    end_date = end.strftime('%Y/%m/%d')
    start_hour = start.strftime('%H')
    start_minute = start.strftime('%M')
    end_hour = end.strftime('%H')
    end_minute = end.strftime('%M')
    
    # Generate URL
    url = f"https://fclm-portal.amazon.com/reports/unitsRollup?reportFormat=CSV&warehouseId={site}&jobAction={func}&startDate={start_date}&startHour={start_hour}&startMinute={start_minute}&endDate={end_date}&endHour={end_hour}&endMinute={end_minute}"
    print(f"Fetching data from URL: {url}")
    
    # Execute JavaScript to download the file directly
    driver.execute_script(f"window.open('{url}', '_blank');")
    
    # Generate expected filename for the downloaded CSV
    start_str_utc = start.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
    end_str_utc = end.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
    download_filename = f"unitsRollup-{site}-{func}-{start_str_utc}-{end_str_utc}.csv"
    download_path = os.path.join(os.getcwd(), download_filename)

    print(download_path)
    
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

def get_fr_hours(driver, process_id, process_name, func, start:datetime, end:datetime):
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
    
    url = f"https://fclm-portal.amazon.com/reports/functionRollup?reportFormat=CSV&warehouseId={site}&processId={process_id}&maxIntradayDays=1&spanType=Intraday&startDateIntraday={start_date_str}&startHourIntraday={start_hour}&startMinuteIntraday={start_minute}&endDateIntraday={end_date_str}&endHourIntraday={end_hour}&endMinuteIntraday={end_minute}"

    # Execute JavaScript to download the file directly
    driver.execute_script(f"window.open('{url}', '_blank');")
    #print("I made it!")

    modified_start = start.astimezone(pytz.UTC)
    modified_end = end.astimezone(pytz.UTC)

    file_name_start = modified_start.strftime(f"functionRollupReport-{site}-{process_name}-Intraday-%Y%m%d%H%M00-")
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
    # Initialize total_value for the new sum calculation
    total_value = 0
    with open(download_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i >= 2 and len(row) > 16:  # Ensure the row has enough columns to avoid out-of-range errors
                try:
                    if func == "Wall Builder":
                        if row[1].strip() == func:
                            total_value += float(row[10])
                    else:
                        # Check if column B is 'Decant Non-TI', column O is 'EACH', and column P is 'Total'
                        if row[1].strip() == func and row[14].strip() == 'EACH' and row[15].strip()== 'Total':
                            total_value += float(row[10])  # Add the value in column Q
                except ValueError:
                    pass  # Skip non-numeric values

    # Clean up by deleting the downloaded file
    os.remove(download_path)

    return total_value

def get_last_segment_times():
    # Define your local timezone

    # Get current local time
    now = datetime.now(pytz.timezone(timezone))

    # Apply the 10-minute delay
    delayed_now = now - timedelta(minutes=25)

    # Floor to the nearest 15-minute segment
    floored_minute = (delayed_now.minute // 15) * 15
    start = delayed_now.replace(minute=floored_minute, second=0, microsecond=0)
    end = start + timedelta(minutes=15)

    return start, end

def get_last_fl_segment(driver):
    start, end = get_last_segment_times()
    print(f"Start: {start}, End: {end}")

    case_jobs = get_ur_jobs(driver, "FluidLoadCase", start, end)
    tote_jobs = get_ur_jobs(driver, "FluidLoadTote", start, end)
    fl_jobs = case_jobs + tote_jobs

    fl_hours = get_fr_hours(driver, "1003021","Transfer Out", "Fluid Load - Case", start, end)
    fl_hours += get_fr_hours(driver, "1003021","Transfer Out", "Fluid Load - Tote", start, end)
    fl_hours += get_fr_hours(driver, "1003021","Transfer Out", "Wall Builder", start, end)
    return fl_jobs, fl_hours


def main():
    # Setup the Firefox driver
    options = webdriver.FirefoxOptions()
    options.add_argument('--start-maximized')
    # Set up Firefox options for downloading files (if needed)
    download_dir = os.getcwd()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    driver = webdriver.Firefox(options=options)
    # Navigate to the initial authentication page
    driver.get('https://atoz.amazon.work/')
    # Wait for 20 seconds to allow for manual authentication
    time.sleep(40)

    try:
        while True:
        
        
            
            #driver.get(site_main_page)

            #time.sleep(5)

            #Scrape all of the arcs, related workcells, and utilizations from the page
            # Scrape table data
            #all_data = extract_table_data(driver)
            #print("Full scrape results:")
            #for item in all_data:
            #    print(item)


            #insert new code here
            #ob_arcs_list = [
            #    arc for arc in all_data
            #    if arc["arc_href"] and (arc["arc_href"].endswith("_TOTE") or arc["arc_href"].endswith("_CASE"))
            #]

            

            #check_last_hour(driver, ob_arcs_list)

            #print("\nFiltered OB arcs:")
            #for arc in ob_arcs_list:
            #    print(arc) 
            #ob_lanes_list = check_ob_lane_utilization(driver, ob_arcs_list)

            #ob_lanes_list = add_projected_missed_diverts(ob_lanes_list)
            #print("\nOB Lane Volumes:")
            #for lane in ob_lanes_list:
            #    print(lane)

            ob_lanes_list = None

            fl_jobs, fl_hours = get_last_fl_segment(driver)
            fl_rate = fl_jobs / fl_hours if fl_hours > 0 else 0
            
            #test_time = pytz.timezone(timezone).localize(datetime(2025,4,8,8,0,0))
            #fl_rate = get_ur_jobs(driver, "FluidLoadCase", test_time - timedelta(hours=1), test_time)
            #fl_hours = 0
            

            format_and_send_update(ob_lanes_list, fl_rate, fl_hours)
            time.sleep(900)

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()
