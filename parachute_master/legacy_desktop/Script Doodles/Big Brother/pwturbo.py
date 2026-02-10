import json
import requests
import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from seleniumwire import webdriver as selenium_wire_webdriver
import re
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
import threading

# CONTROLS
# test mode
test_mode = False  # Set to True for testing, will slow down execution

# slackbot url
#SLACKBOT_URL = "https://hooks.slack.com/triggers/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"

# speed
NEO_QUERY_SPEED = 3 #seconds waiting for each Neo query to complete (roughly 152 queries in present state)
NEO_QUERY_SPEED_2 = 20

# sites
SITES = [["LGB8", "ONT8", "LAS1", "LAX9"], ["FTW1", "MEM1", "MQJ1", "CLT2"], ["SMF3", "TEB9", "FWA4", "IND9"],
         ["GYR2", "IAH3", "ORF2", "GYR3"], ["RDU2", "RFD2", "RMN3", "MDW2"], ["AVP1", "SWF2", "ABE8"], ["VGT2", "MCC1", "SBD1", "SCK4"]]# "ABE8", "AVP1", "FTW1", "CLT2", "ONT8", "LGB8", "MDW2"}
#SITES = {"TEB9"}

#SITES = [["RMN3"],["MDW2"],["SBD1"],["SCK4"]]
#SITES = [["FTW1", "MEM1", "MQJ1"], ["TEB9", "FWA4", "IND9"],
#         ["IAH3", "ORF2", "CLT2"], ["RDU2", "RFD2", "RMN3", "MDW2"], ["AVP1", "SWF2", "ABE8"]]# "ABE8", "AVP1", "FTW1", "CLT2", "ONT8", "LGB8", "MDW2"}


# helpers
def is_driver_healthy(driver) -> bool:
    try:
        driver.execute_script("return 1")
        return True
    except Exception:
        return False

def abort_navigation(driver):
    # Try to stop the current load so the control channel unblocks
    try:
        driver.execute_script("window.stop();")
    except Exception:
        pass

def get_with_retry(driver, url, attempts=3, sleep_base=0.3):
    for i in range(1, attempts + 1):
        # keep selenium-wire memory small and results precise
        try:
            driver.requests.clear()
        except Exception:
            pass

        try:
            driver.get(url)      # returns quickly with page_load_strategy='none'
            return True
        except TimeoutException:
            abort_navigation(driver)
        except ReadTimeoutError:
            abort_navigation(driver)
        except WebDriverException as e:
            # Any other control-channel issue: abort and maybe heal
            abort_navigation(driver)
            if not is_driver_healthy(driver):
                # Optional soft reset to clear the state
                try:
                    driver.get("about:blank")
                except Exception:
                    pass
        # backoff
        time.sleep(sleep_base * i)
    return False

def fetch_json_via_selenium_wire(driver, url, wait_timeout=30):
    if not get_with_retry(driver, url, attempts=3):
        return None

    pattern = re.escape(url)
    try:
        req = driver.wait_for_request(pattern, timeout=wait_timeout)
    except TimeoutError:
        abort_navigation(driver)
        return None

    if not req or not getattr(req, "response", None):
        return None

    try:
        return json.loads(req.response.body.decode("utf-8", "ignore"))
    except Exception:
        return None

def create_sites_dict():
    """
    Creates a dictionary of sites with their respective staffing data.
    """
    sites_dict = {}
    for site_list in SITES:
        for site in site_list:
            sites_dict[site] = {
                "recommended_staffing": 0,
                "planned_pid": 0,
                "planned_presort": 0,
                "actual staffing": 0,
                "excluded_hours": 0,
                "legacy_only_hours": 0,
                "delta_to_recommended": 0,
                "tp_containers_planned": 0,
                "combined_cartons_planned": 0,
                "rc_sort_units_planned": 0,
                "5lb_units_planned": 0,
                "20lb_units_planned": 0,
                "ms_units_planned": 0,
                "total_diverts_planned": 0,
                "ship_sorter_diverts_planned": 0,
                "tpv_diverts_planned": 0,
                "rwc_jobs_planned": 0,
                "fl_jobs_planned": 0,
                "mp_jobs_planned": 0,
                "pallets_loaded_planned": 0,
                "pr_pallets_planned": 0,
                "online_blended_rate_planned": 0,
                "sort_total_rate_planned": 0,
                "5lb_rate_planned": 0,
                "20lb_rate_planned": 0,
                "ms_rate_planned": 0,
                "to_ex_pallet_rate_planned": 0,
                "fl_rate_planned": 0,
                "mp_rate_planned": 0,
                "to_ws_rate_planned": 0,
                "total_hours_planned": 0,
                "5lb_hours_planned": 0,
                "20lb_hours_planned": 0,
                "ms_hours_planned": 0,
                "presort_hours_planned": 0,
                "fl_hours_planned": 0,
                "mp_hours_planned": 0,
                "receive_dock_hours_planned": 0,
                "tis_hours_planned": 0,
                "rc_sort_indirect_hours_planned": 0,
                "to_indirect_hours_planned":0,
                "rob_ws_hours_planned": 0,
                "to_ws_hours_planned": 0,
                "tod_obdc_hours_planned": 0,
            }
    return sites_dict

def pull_all_site_data(sites_dict):
    threads = []

    # for each site
    for site_list in SITES:
        # create a thread
        t = threading.Thread(target=pull_site_data, args=(site_list, sites_dict))
        threads.append(t)
        t.start()
        time.sleep(40)
        
    for t in threads:
        t.join()

    print("[INFO] All site data pulled successfully.")
    return sites_dict

def pull_site_data(site_list, sites_dict):
    #print(f"[INFO] Pulling data for site: {site}")
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.getcwd())
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    driver = selenium_wire_webdriver.Firefox(options=options)
    driver.get("https://atoz.amazon.work/")  # Or the exact URL you want to pre-auth
    time.sleep(180)
    driver.set_page_load_timeout(180)

    for site in site_list:
        calculate_recommended_staffing(site, sites_dict, driver)
        pull_actuals(site, sites_dict, driver)

    driver.quit()



def calculate_recommended_staffing(site, sites_dict, driver):
    # Step 1: Generate prior Sunday–Saturday week
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday() + 2)  # Saturday → index 5; need Sunday before last
    start_of_week = start_of_week - timedelta(days=start_of_week.weekday() + 1)  # Sunday
    date_list = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    # Step 2: Iterate through sites, shifts, and all dates from the prior week
    #for site in SITES:
    for shift in ["day", "night"]:
        for date in date_list:
            # SHIFT ID
            shift_id_url = f"https://neo.meta.amazon.dev/api/v2/shift?site_id={site}&shift={shift}&date={date}&department=One%20Flow"
            shift_id = None
            for attempt in range(3):
                driver.requests.clear()  # Clear previous requests
                driver.get(shift_id_url)
                #req = driver.wait_for_request(shift_id_url, timeout=60)
                time.sleep(NEO_QUERY_SPEED)
                for request in driver.requests:
                    if request.response and shift_id_url in request.url:
                        try:
                            response_json = request.response.body.decode('utf-8')
                            shift_data = json.loads(response_json)
                            shift_id = shift_data.get("shift_id")
                            print(f"[INFO] Shift ID for {site} {shift} on {date}: {shift_id}")
                            break
                        except Exception as e:
                            print(f"[ERROR] Failed to parse shift ID for {site} on {date}: {e}")
                if shift_id:
                    break
            print(f"Result of shift ID request({shift_id_url}): {shift_id}")

            # STAFFING PROFILE ID
            sp_id_url = f"https://neo.meta.amazon.dev/api/v2/rules/staffing_profile?site_id={site}"
            sp_id = None
            for attempt in range(3):
                driver.requests.clear()
                driver.get(sp_id_url)
                time.sleep(NEO_QUERY_SPEED)
                #request = driver.wait_for_request(sp_id_url, timeout=60)
                for request in driver.requests:
                    if request.response and sp_id_url in request.url:
                        try:
                            response_json = request.response.body.decode('utf-8')
                            sp_data = json.loads(response_json)
                            sp_id = sp_data[0].get("staffing_profile_id")
                            print(f"[INFO] Staffing Profile ID for {site}: {sp_id}")
                            break
                        except Exception as e:
                            print(f"[ERROR] Failed to parse staffing profile ID for {site}: {e}")
                if sp_id:
                    break
            print(f"Result of staffing profile ID request({sp_id_url}): {sp_id}")

            # PLAN ID
            plan_id_url = f"https://neo.meta.amazon.dev/api/v2/planning/plan?staffing_profile_id={sp_id}&shift={shift_id}"
            plan_id = None
            plan_type = None
            for attempt in range(3):
                driver.requests.clear()
                driver.get(plan_id_url)
                time.sleep(NEO_QUERY_SPEED)
                #req = driver.wait_for_request(plan_id_url, timeout=60)
                for request in driver.requests:
                    if request.response and plan_id_url in request.url:
                        try:
                            response_json = request.response.body.decode('utf-8')
                            plan_data = json.loads(response_json)
                            priority_order = {"sos": 1, "psp": 2, "pdp": 3}

                            locked_plans = [
                                plan for plan in plan_data
                                if plan.get("locked") and plan.get("plan_type") in priority_order
                            ]

                            if not locked_plans:
                                print(f"[WARN] No locked plans of valid types found for {site} {shift} on {date} in url: {plan_id_url}")
                                if attempt == 2:
                                    plan_id = -1
                                    plan_type = None
                                continue
                            
                            best_plan = sorted(
                                locked_plans,
                                key=lambda p: priority_order[p["plan_type"]]
                            )[0]

                            plan_id = best_plan.get("plan_id")
                            plan_type = best_plan.get("plan_type")

                            print(f"[INFO] Plan ID for {site} {shift} on {date}: {plan_id}")
                            break
                        except Exception as e:
                            print(f"[ERROR] Failed to parse plan ID for {site} on {date}: {e}")
                if plan_id:
                    break

            if plan_id == -1:
                print(f"[INFO] No valid plan selected for {site} {shift} on {date}. Proceeding with plan_id = -1.")

            print(f"Result of plan ID request({plan_id_url}): {plan_id}")

            # PLAN PR & PID
            plan_url = f"https://neo.meta.amazon.dev/api/v2/planning/generate_plan?site_id={site}&shift={shift}&date={date}&plan_id={plan_id}&department=One%20Flow&staffing_profile_id={sp_id}&plan_name={plan_type}"
            plan_pr = None
            plan_pid = None

            if plan_id == -1:
                plan_pid = -1
                plan_pr = -1
                plan_presort = -1
                print(f"[INFO] Skipping plan fetch for {site} {shift} on {date} because plan_id is -1")
            else:
                for attempt in range(3):
                    print("Attempt ", attempt + 1, "to fetch plan data")
                    driver.requests.clear()
                    driver.get(plan_url)
                    time.sleep(NEO_QUERY_SPEED_2)
                    #req = driver.wait_for_request(plan_url, timeout=60)
                    for request in driver.requests:
                        if request.response and plan_url in request.url:
                            try:
                                response_json = request.response.body.decode('utf-8')
                                plan_data = json.loads(response_json)
                                plan_pr = plan_data[0]['data'][1]['subfunctions'][1].get("plan")
                                plan_pid = plan_data[0]['data'][1]['subfunctions'][7].get("plan")
                                plan_presort = plan_data[0]['data'][4]['subfunctions'][0].get("plan")

                                combined_cartons_planned = plan_data[0]['data'][1]['subfunctions'][0].get("plan")
                                total_diverts_planned = plan_data[0]['data'][5]['subfunctions'][3].get("plan")
                                tp_containers_planned = combined_cartons_planned + total_diverts_planned
                                rc_sort_units_planned = plan_data[0]['data'][4]['subfunctions'][1].get("plan")
                                five_lb_units_planned = plan_data[2]['data'][6]['subfunctions'][26].get("plan")
                                twenty_lb_units_planned = plan_data[2]['data'][6]['subfunctions'][31].get("plan")
                                ms_units_planned = plan_data[2]['data'][6]['subfunctions'][36].get("plan")
                                ship_sorter_diverts_planned = plan_data[0]['data'][5]['subfunctions'][1].get("plan")
                                tpv_diverts_planned = plan_data[0]['data'][5]['subfunctions'][2].get("plan")
                                rwc_jobs_planned = plan_data[2]['data'][8]['subfunctions'][8].get("plan")
                                fl_jobs_planned = plan_data[2]['data'][8]['subfunctions'][0].get("plan")
                                mp_jobs_planned = plan_data[2]['data'][8]['subfunctions'][3].get("plan")
                                pallets_loaded_planned = plan_data[2]['data'][9]['subfunctions'][0].get("plan")
                                pr_pallets_planned = plan_pr
                                total_hours_planned = plan_data[1]['data'][3]['subfunctions'][6].get("plan") + plan_data[1]['data'][4]['subfunctions'][3].get("plan")
                                five_lb_hours_planned = plan_data[2]['data'][6]['subfunctions'][28].get("plan")
                                twenty_lb_hours_planned = plan_data[2]['data'][6]['subfunctions'][33].get("plan")
                                ms_hours_planned = plan_data[2]['data'][6]['subfunctions'][38].get("plan")
                                presort_hours_planned = plan_data[2]['data'][7]['subfunctions'][2].get("plan")
                                fl_hours_planned = plan_data[2]['data'][8]['subfunctions'][17].get("plan")
                                mp_hours_planned = plan_data[2]['data'][8]['subfunctions'][12].get("plan")
                                receive_dock_hours_planned = plan_data[3]['data'][0]['subfunctions'][2].get("plan")
                                tis_hours_planned = plan_data[3]['data'][2]['subfunctions'][2].get("plan")
                                rc_sort_indirect_hours_planned = plan_data[3]['data'][6]['subfunctions'][4].get("plan")
                                to_indirect_hours_planned = plan_data[3]['data'][7]['subfunctions'][4].get("plan")
                                rob_ws_hours_planned = plan_data[3]['data'][7]['subfunctions'][6].get("plan")
                                to_ws_hours_planned = plan_data[3]['data'][7]['subfunctions'][10].get("plan")
                                tod_obdc_hours_planned = plan_data[3]['data'][8]['subfunctions'][8].get("plan")

                                #increment everything you just pulled in
                                sites_dict[site]["combined_cartons_planned"] += combined_cartons_planned
                                sites_dict[site]["total_diverts_planned"] += total_diverts_planned
                                sites_dict[site]["tp_containers_planned"] += tp_containers_planned
                                sites_dict[site]["rc_sort_units_planned"] += rc_sort_units_planned
                                sites_dict[site]["5lb_units_planned"] += five_lb_units_planned
                                sites_dict[site]["20lb_units_planned"] += twenty_lb_units_planned
                                sites_dict[site]["ms_units_planned"] += ms_units_planned
                                sites_dict[site]["ship_sorter_diverts_planned"] += ship_sorter_diverts_planned
                                sites_dict[site]["tpv_diverts_planned"] += tpv_diverts_planned
                                sites_dict[site]["rwc_jobs_planned"] += rwc_jobs_planned
                                sites_dict[site]["fl_jobs_planned"] += fl_jobs_planned
                                sites_dict[site]["mp_jobs_planned"] += mp_jobs_planned
                                sites_dict[site]["pallets_loaded_planned"] += pallets_loaded_planned
                                sites_dict[site]["pr_pallets_planned"] += pr_pallets_planned
                                sites_dict[site]["total_hours_planned"] += total_hours_planned
                                sites_dict[site]["5lb_hours_planned"] += five_lb_hours_planned
                                sites_dict[site]["20lb_hours_planned"] += twenty_lb_hours_planned
                                sites_dict[site]["ms_hours_planned"] += ms_hours_planned
                                sites_dict[site]["presort_hours_planned"] += presort_hours_planned
                                sites_dict[site]["fl_hours_planned"] += fl_hours_planned
                                sites_dict[site]["mp_hours_planned"] += mp_hours_planned
                                sites_dict[site]["receive_dock_hours_planned"] += receive_dock_hours_planned
                                sites_dict[site]["tis_hours_planned"] += tis_hours_planned
                                sites_dict[site]["rc_sort_indirect_hours_planned"] += rc_sort_indirect_hours_planned
                                sites_dict[site]["to_indirect_hours_planned"] += to_indirect_hours_planned
                                sites_dict[site]["rob_ws_hours_planned"] += rob_ws_hours_planned
                                sites_dict[site]["to_ws_hours_planned"] += to_ws_hours_planned
                                sites_dict[site]["tod_obdc_hours_planned"] += tod_obdc_hours_planned



                                print(f"[INFO] Plan PR for {site} {shift} on {date}: {plan_pr}")
                                print(f"[INFO] Plan PID for {site} {shift} on {date}: {plan_pid}")
                                if plan_pr is not None and plan_pid is not None and plan_presort is not None:
                                    break
                            except Exception as e:
                                print(f"[ERROR] Failed to parse plan data for {site} on {date}: {e}")
                    if plan_pr is not None and plan_pid is not None and plan_presort is not None:
                        break
            print(f"Result of plan request({plan_url}): PR={plan_pr}, PID={plan_pid}, Presort={plan_presort}")

            calculate_recommended_hours(sites_dict, site, plan_pid, plan_pr, plan_presort)
    return



def calculate_recommended_hours(sites_dict, site, pid, pr, presort):
    """
    Calculates recommended staffing by looking up the matrix.csv based on PID and PR values.
    """

    if pid == -1 or presort == -1 or pr == -1:
        print(f"[INFO] Skipping recommended hours for {site} due to invalid plan inputs (pid={pid}, pr={pr})")
        return sites_dict

    # Step 1: Load matrix
    matrix = {}
    try:
        with open("matrix.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                pid_key = int(row["PID Cartons"])
                pr_key = int(row["PR Cartons"])
                hc = int(row["Headcount"])
                matrix[(pid_key, pr_key)] = hc
    except FileNotFoundError:
        print("matrix.csv not found. Aborting headcount calculation.")
        return sites_dict

    # Bin PID goal
    if pid + presort <= 30000:
        pid_bin = 30000
    elif pid + presort <= 35000:
        pid_bin = 35000
    elif pid + presort <= 40000:
        pid_bin = 40000
    elif pid + presort <= 45000:
        pid_bin = 45000
    elif pid + presort <= 50000:
        pid_bin = 50000
    elif pid + presort <= 55000:
        pid_bin = 55000
    elif pid + presort <= 60000:
        pid_bin = 60000
    elif pid + presort <= 65000:
        pid_bin = 65000
    elif pid + presort <= 70000:
        pid_bin = 70000
    elif pid + presort <= 75000:
        pid_bin = 75000
    elif pid + presort <= 80000:
        pid_bin = 80000
    elif pid + presort <= 85000:
        pid_bin = 85000
    elif pid + presort <= 90000:
        pid_bin = 90000
    elif pid + presort <= 95000:
        pid_bin = 95000
    else:
        pid_bin = 100000

    # Bin PR goal
    if pr <= 200:
        pr_bin = 200
    elif pr <= 300:
        pr_bin = 300
    elif pr <= 400:
        pr_bin = 400
    elif pr <= 500:
        pr_bin = 500
    elif pr <= 600:
        pr_bin = 600
    else:
        pr_bin = 700

    # Lookup from matrix
    key = (pid_bin, pr_bin)
    sites_dict[site]["recommended_staffing"] += (matrix.get(key, 0))  # Default to 0 if missing
    sites_dict[site]["planned_pid"] += pid
    sites_dict[site]["planned_presort"] += presort

    return


def pull_actuals(site, sites_dict, driver):
    processes = {
        "Receive Dock": 1003010,
        "Pallet-Receive": 1003032,
        "LP-Receive": 1003031,
        "Transfer In Support": 1003020
    }

    tz_df = pd.read_csv("timezones.csv")
    tz_lookup = dict(zip(tz_df["Site"], tz_df["Delta to EST"]))

    today = datetime.now()
    start_of_last_week = today - timedelta(days=today.weekday() + 8)  # Prior Sunday
    start_of_this_week = start_of_last_week + timedelta(days=7)


    #for site in sites_dict:
    # Get site-local start of week and end of week
    site_delta = tz_lookup.get(site, 0)

    start_dt_local = datetime.combine(start_of_last_week.date(), datetime.min.time()) + timedelta(hours=0)
    end_dt_local = datetime.combine(start_of_this_week.date(), datetime.min.time()) + timedelta(hours=0)

    # Convert to UTC using EST anchor, site_delta shift
    start_dt_utc = (start_dt_local - timedelta(hours=site_delta)).replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")
    end_dt_utc = (end_dt_local - timedelta(hours=site_delta)).replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")

    # These will be used for the filename match
    start_date_str = start_of_last_week.strftime("%Y/%m/%d")
    end_date_str = start_of_this_week.strftime("%Y/%m/%d")


    total_hours = 0
    excluded_hours = 0
    legacy_only_hours = 0

    for process_name, process_id in processes.items():
        success = False
        for attempt in range(3):
            url = (
                f"https://fclm-portal.amazon.com/reports/functionRollup?"
                f"reportFormat=CSV&warehouseId={site}&processId={process_id}"
                f"&spanType=Week&startDateWeek={start_date_str}&maxIntradayDays=1&startHourIntraday=0"
                f"&startMinuteIntraday=0&endHourIntraday=0"
                f"&endMinuteIntraday=0"
            )

            driver.execute_script(f"window.open('{url}', '_blank');")

            filename = f"functionRollupReport-{site}-{process_name}-Week-{start_dt_utc}-{end_dt_utc}.csv"
            filepath = os.path.join(os.getcwd(), filename)

            if test_mode:
                print(f"[INFO] Attempt {attempt + 1}: Downloading {filename} from {url}")

            for _ in range(15):
                if os.path.exists(filepath):
                    print(f"[INFO] Downloaded {filename}")
                    if test_mode:
                        time.sleep(5)
                    break
                time.sleep(1)

            if not os.path.exists(filepath):
                print(f"[WARN] Attempt {attempt + 1}: File did not download: {filename}")
                continue

            try:
                time.sleep(3)  # Allow time for file to be fully written
                df = pd.read_csv(filepath)
                if df.empty or "Employee Id" not in df.columns or "Function Name" not in df.columns:
                    print(f"[WARN] Missing required data in {filename}")
                    continue


                dedup_df = df.drop_duplicates(subset=["Employee Id", "Function Name"])
                
                if "Paid Hours-Total(function,employee)" in dedup_df.columns:
                    # Identify excluded hours before filtering
                    excluded_df = dedup_df[dedup_df["Function Name"].isin([
                        "Bin Scout Trans", "Cart Runner Trans", "Tote Stacking", 
                        "Transfer In Ambssdr", "Transfer In Training", "PrEditor Receive"
                    ])]
                    excluded_hours += excluded_df["Paid Hours-Total(function,employee)"].sum()

                    legacy_only_df = dedup_df[dedup_df["Function Name"].isin([
                        "PID Manual Divert", "Vendor Cutter"
                    ])]
                    legacy_only_hours += legacy_only_df["Paid Hours-Total(function,employee)"].sum()

                    # Now filter them out
                    dedup_df = dedup_df[~dedup_df["Function Name"].isin([
                        "Bin Scout Trans", "Cart Runner Trans", "Tote Stacking", 
                        "Transfer In Ambssdr", "Transfer In Training", "PrEditor Receive", "PID Manual Divert", "Vendor Cutter"
                    ])]

                    hours = dedup_df["Paid Hours-Total(function,employee)"].sum()
                    total_hours += hours
                    success = True
                    print(f"[INFO] Processed {filename}")
                else:
                    print(f"[WARN] 'Paid Hours' column not found in {filename}")

            except Exception as e:
                print(f"[ERROR] Could not process {filename}: {e}")

            finally:
                if os.path.exists(filepath):
                    print(f"[INFO] Deleting {filename}")
                    os.remove(filepath)

            if success:
                break

        if not success:
            print(f"[FAIL] All attempts failed for {site} - {process_name}")

    sites_dict[site]["actual staffing"] = round(total_hours)
    sites_dict[site]["excluded_hours"] = round(excluded_hours)
    sites_dict[site]["legacy_only_hours"] = round(legacy_only_hours)
    print(f"[INFO] {site} - Actual Staffing: {sites_dict[site]['actual staffing']} hours, Excluded: {sites_dict[site]['excluded_hours']} hours")

    return sites_dict



def calculate_deltas(sites_dict):
    """
    Calculates deltas to recommended and glidepath.
    """
    for site in sites_dict:
        actual = sites_dict[site]["actual staffing"]
        rec = sites_dict[site]["recommended_staffing"]
        sites_dict[site]["delta_to_recommended"] = actual - rec

        
        sites_dict[site]["online_blended_rate_planned"] = (sites_dict[site]["planned_pid"] + sites_dict[site]["planned_presort"]) / (sites_dict[site]["receive_dock_hours_planned"]+sites_dict[site]["tis_hours_planned"]+sites_dict[site]["presort_hours_planned"]) if ((sites_dict[site]["receive_dock_hours_planned"]+sites_dict[site]["tis_hours_planned"]+sites_dict[site]["presort_hours_planned"]) != 0) else 0 
        sites_dict[site]["sort_total_rate_planned"] = sites_dict[site]["rc_sort_units_planned"] / (sites_dict[site]["5lb_hours_planned"] + sites_dict[site]["20lb_hours_planned"] + sites_dict[site]["ms_hours_planned"] + sites_dict[site]["rc_sort_indirect_hours_planned"]) if ((sites_dict[site]["5lb_hours_planned"] + sites_dict[site]["20lb_hours_planned"] + sites_dict[site]["ms_hours_planned"] + sites_dict[site]["rc_sort_indirect_hours_planned"]) != 0) else 0
        sites_dict[site]["5lb_rate_planned"] = sites_dict[site]["5lb_units_planned"] / sites_dict[site]["5lb_hours_planned"] if (sites_dict[site]["5lb_hours_planned"]) != 0 else 0
        sites_dict[site]["20lb_rate_planned"] = sites_dict[site]["20lb_units_planned"] / sites_dict[site]["20lb_hours_planned"] if (sites_dict[site]["20lb_hours_planned"]) != 0 else 0
        sites_dict[site]["ms_rate_planned"] = sites_dict[site]["ms_units_planned"] / sites_dict[site]["ms_hours_planned"] if (sites_dict[site]["ms_hours_planned"]) != 0 else 0
        sites_dict[site]["to_ex_pallet_rate_planned"] = sites_dict[site]["ship_sorter_diverts_planned"] / (sites_dict[site]["fl_hours_planned"]+sites_dict[site]["mp_hours_planned"]+sites_dict[site]["to_indirect_hours_planned"]) if (sites_dict[site]["fl_hours_planned"]+sites_dict[site]["mp_hours_planned"]+sites_dict[site]["to_indirect_hours_planned"]) != 0 else 0
        sites_dict[site]["fl_rate_planned"] = sites_dict[site]["fl_jobs_planned"] / sites_dict[site]["fl_hours_planned"] if (sites_dict[site]["fl_hours_planned"]) != 0 else 0
        sites_dict[site]["mp_rate_planned"] = sites_dict[site]["mp_jobs_planned"] / sites_dict[site]["mp_hours_planned"] if (sites_dict[site]["mp_hours_planned"]) != 0 else 0
        sites_dict[site]["to_ws_rate_planned"] = sites_dict[site]["pallets_loaded_planned"] / (sites_dict[site]["rob_ws_hours_planned"] + sites_dict[site]["to_ws_hours_planned"] + sites_dict[site]["tod_obdc_hours_planned"]) if (sites_dict[site]["rob_ws_hours_planned"] + sites_dict[site]["to_ws_hours_planned"] + sites_dict[site]["tod_obdc_hours_planned"]) != 0 else 0



    return sites_dict


def output_to_csv(sites_dict):
    #output the results of sites dict to a CSV file
    output_file = "weekly_staffing_results_turbo.csv"
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Site", "Planned PID", "Planned Presort", "Recommended Staffing", "Actual Staffing", "Excluded Hours", "Legacy Only Hours","Delta to Recommended", "TP Containers Planned", "Combined Cartons Planned", "RC Sort Units Planned", "5lb Units Planned", "20lb Units Planned", "MS Units Planned", "Total Diverts Planned", "Ship Sorter Diverts Planned", "Transship Pallet Verified Planned", "RWC Jobs Planned", "FL Jobs Planned", "MP Jobs Planned", "Pallets Loaded Planned", "PR Pallets Planned", "Online Blended Rate Planned", "Sort Total Rate Planned", "5lb Rate Planned", "20lb Rate Planned", "MS Rate Planned", "TO Ex Pallet Rate Planned", "FL Rate Planned", "MP Rate Planned", "TO WS Rate Planned", "Total Hours Planned", "5lb Hours Planned", "20lb Hours Planned", "MS Hours Planned", "Presort Hours Planned", "FL Hours Planned", "MP Hours Planned", "Receive Dock Hours Planned", "TIS Hours Planned", "RC Sort Indirect Hours Planned", "TO Indirect Hours Planned", "Robotic WS Hours Planned", "TO WS Hours Planned", "TOD OBDC Hours Planned"])
        for site, data in sites_dict.items():
            writer.writerow([site,data["planned_pid"], data["planned_presort"], data["recommended_staffing"], data["actual staffing"], data["excluded_hours"], data["legacy_only_hours"], data["delta_to_recommended"], data["tp_containers_planned"], data["combined_cartons_planned"], data["rc_sort_units_planned"], data["5lb_units_planned"], data["20lb_units_planned"], data["ms_units_planned"], data["total_diverts_planned"], data["ship_sorter_diverts_planned"], data["tpv_diverts_planned"], data["rwc_jobs_planned"], data["fl_jobs_planned"], data["mp_jobs_planned"], data["pallets_loaded_planned"], data["pr_pallets_planned"], data["online_blended_rate_planned"], data["sort_total_rate_planned"], data["5lb_rate_planned"], data["20lb_rate_planned"], data["ms_rate_planned"], data["to_ex_pallet_rate_planned"], data["fl_rate_planned"], data["mp_rate_planned"], data["to_ws_rate_planned"], data["total_hours_planned"], data["5lb_hours_planned"], data["20lb_hours_planned"], data["ms_hours_planned"], data["presort_hours_planned"], data["fl_hours_planned"], data["mp_hours_planned"], data["receive_dock_hours_planned"], data["tis_hours_planned"], data["rc_sort_indirect_hours_planned"], data["to_indirect_hours_planned"], data["rob_ws_hours_planned"], data["to_ws_hours_planned"], data["tod_obdc_hours_planned"]])
    return

# main

def main():

    # Launch browser for manual authentication
    #print("Launching Firefox for Midway auth... you have 20 seconds.")
    #options = Options()
    #options.set_preference("browser.download.folderList", 2)
    #options.set_preference("browser.download.dir", os.getcwd())
    #options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    #options.page_load_strategy = 'none'
    #options.add_argument("--auto-open-devtools-for-tabs")
    #driver = selenium_wire_webdriver.Firefox(options=options)
    #driver.execute_cdp_cmd("Network.enable",{})
    #driver.set_page_load_timeout(60)
    #driver.get("https://atoz.amazon.work/")  # Or the exact URL you want to pre-auth

    #time.sleep(7200)
    #time.sleep(30)  # Wait for manual login and cert push
    #print("Auth window complete. Continuing...")

    sites_dict = create_sites_dict()
    sites_dict = pull_all_site_data(sites_dict)
    #sites_dict = calculate_recommended_staffing(sites_dict, driver)
    #sites_dict = pull_actuals(sites_dict, driver)
    sites_dict = calculate_deltas(sites_dict)
    
    output_to_csv(sites_dict)



if __name__ == "__main__":
    main()