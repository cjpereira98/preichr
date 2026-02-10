from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# Config variables
site_main_page = "https://prod-na.dockflow.robotics.a2z.com/SWF2/wc/MainSorter1/Sorter?tagConfig=%7B%7D"
webhook_url = "https://hooks.slack.com/triggers/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"
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


def format_and_send_update(ob_lanes_list):
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

def main():
    # Setup the Firefox driver
    options = webdriver.FirefoxOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Firefox(options=options)
    # Navigate to the initial authentication page
    driver.get('https://atoz.amazon.work/')
    # Wait for 20 seconds to allow for manual authentication
    time.sleep(40)

    try:
        while True:
        
        

            driver.get(site_main_page)

            time.sleep(5)

            #Scrape all of the arcs, related workcells, and utilizations from the page
            # Scrape table data
            all_data = extract_table_data(driver)
            #print("Full scrape results:")
            #for item in all_data:
            #    print(item)


            #insert new code here
            ob_arcs_list = [
                arc for arc in all_data
                if arc["arc_href"] and (arc["arc_href"].endswith("_TOTE") or arc["arc_href"].endswith("_CASE"))
            ]

            

            check_last_hour(driver, ob_arcs_list)

            #print("\nFiltered OB arcs:")
            #for arc in ob_arcs_list:
            #    print(arc) 
            ob_lanes_list = check_ob_lane_utilization(driver, ob_arcs_list)

            ob_lanes_list = add_projected_missed_diverts(ob_lanes_list)
            print("\nOB Lane Volumes:")
            for lane in ob_lanes_list:
                print(lane)

            format_and_send_update(ob_lanes_list)
            time.sleep(900)

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()
