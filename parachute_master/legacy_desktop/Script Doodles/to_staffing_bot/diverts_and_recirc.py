import json
import requests
import csv
import time
import os
from selenium import webdriver
from seleniumwire import webdriver as selenium_wire_webdriver
from selenium.webdriver.firefox.options import Options
import pandas as pd
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# CONTROLS
# test mode
test_mode = False  # Set to True for testing, will slow down execution

# slackbot url
SLACKBOT_URL = "https://hooks.slack.com/triggers/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"

# glidepath factor
GLIDEPATH_FACTOR = 0.0

NEO_QUERY_SPEED = 0.1  # seconds to wait between NEO API requests

# sites
SITES = {"GYR3", "IND9", "LAS1", "LAX9", "MEM1", "MQJ1", "SMF3", "TEB9", "FWA4",
         "GYR2", "IAH3", "ORF2", "RDU2", "RFD2", "RMN3", "SBD1", "SCK4", "SWF2", "VGT2", "ABE8", "AVP1", "FTW1", "CLT2", "ONT8", "LGB8", "MDW2"}


# helpers

def create_sites_dict():
    """
    Creates a dictionary of sites with their respective staffing data.
    """
    sites_dict = {}
    for site in SITES:
        sites_dict[site] = {
            "diverts": 0,
            "staffing": 0,
            "missed diverts": 0.0,
            "diverts_per_hour": 0.0
        }
    return sites_dict

def update_goals(sites_dict, driver):
    from zoneinfo import ZoneInfo

    # Load timezones
    tz_df = pd.read_csv("timezones.csv")
    tz_lookup = dict(zip(tz_df["Site"], tz_df["Delta to EST"]))

    # Current UTC time
    now_utc = datetime.now(timezone.utc)

    rows = []

    for site in sites_dict:
        site_delta = tz_lookup.get(site, 0)
        local_now = now_utc + timedelta(hours=site_delta)
        local_hour = local_now.hour

        # Determine shift type
        if 6 <= local_hour < 18:
            shift = "day"
        else:
            shift = "night"

        # Fix date if we're after midnight but still night shift
        date_adjust = timedelta(days=1) if local_hour < 6 else timedelta(days=0)
        date = (local_now - date_adjust).strftime("%Y-%m-%d")

        # Get shift ID
        shift_id_url = f"https://neo.meta.amazon.dev/api/v2/shift?site_id={site}&shift={shift}&date={date}&department=One%20Flow"
        shift_id = None
        for attempt in range(3):
            driver.get(shift_id_url)
            time.sleep(NEO_QUERY_SPEED)
            for request in driver.requests:
                if request.response and shift_id_url in request.url:
                    try:
                        response_json = request.response.body.decode('utf-8')
                        shift_data = json.loads(response_json)
                        shift_id = shift_data.get("shift_id")
                        break
                    except Exception:
                        continue
            if shift_id:
                break

        # Get staffing profile ID
        sp_id_url = f"https://neo.meta.amazon.dev/api/v2/rules/staffing_profile?site_id={site}"
        sp_id = None
        for attempt in range(3):
            driver.get(sp_id_url)
            time.sleep(NEO_QUERY_SPEED)
            for request in driver.requests:
                if request.response and sp_id_url in request.url:
                    try:
                        response_json = request.response.body.decode('utf-8')
                        sp_data = json.loads(response_json)
                        sp_id = sp_data[0].get("staffing_profile_id")
                        break
                    except Exception:
                        continue
            if sp_id:
                break

        # Get plan ID (sos/psp/pdp only)
        plan_id_url = f"https://neo.meta.amazon.dev/api/v2/planning/plan?staffing_profile_id={sp_id}&shift={shift_id}"
        plan_id = None
        plan_type = None
        priority_order = {"sos": 1, "psp": 2, "pdp": 3}
        for attempt in range(3):
            driver.get(plan_id_url)
            time.sleep(NEO_QUERY_SPEED)
            for request in driver.requests:
                if request.response and plan_id_url in request.url:
                    try:
                        response_json = request.response.body.decode('utf-8')
                        plan_data = json.loads(response_json)
                        locked_plans = [p for p in plan_data if p.get("locked") and p.get("plan_type") in priority_order]
                        if locked_plans:
                            best_plan = sorted(locked_plans, key=lambda p: priority_order[p["plan_type"]])[0]
                            plan_id = best_plan.get("plan_id")
                            plan_type = best_plan.get("plan_type")
                            break
                    except Exception:
                        continue
            if plan_id:
                break

        # Get PR/PID data
        plan_url = f"https://neo.meta.amazon.dev/api/v2/planning/generate_plan?site_id={site}&shift={shift}&date={date}&plan_id={plan_id}&department=One%20Flow&staffing_profile_id={sp_id}&plan_name={plan_type}"
        plan_to_jobs = -1
        for attempt in range(3):
            driver.get(plan_url)
            time.sleep(NEO_QUERY_SPEED)
            for request in driver.requests:
                if request.response and plan_url in request.url:
                    try:
                        response_json = request.response.body.decode('utf-8')
                        plan_data = json.loads(response_json)
                        plan_to_jobs = plan_data[0]['data'][4]['subfunctions'][3].get("plan")
                        break
                    except Exception:
                        continue
            if plan_to_jobs != -1:
                break

        rows.append({"site": site, "TO Jobs Goal": plan_to_jobs})

    # Write out to goals.csv
    with open("goals.csv", mode="w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["site", "TO Jobs Goal"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def get_shift_goals(sites_dict):
    """
    Loads TO Jobs goal from goals.csv into the sites_dict.
    """
    try:
        with open("goals.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                site = row["site"]
                if site in sites_dict:
                    sites_dict[site]["to_jobs"] = int(float(row["TO Jobs Goal"]))
    except FileNotFoundError:
        print("goals.csv not found. Using placeholder goals instead.")
        for site in sites_dict:
            sites_dict[site]["to_jobs"] = 50000
    return sites_dict



def calculate_recommended_staffing(sites_dict):
    """
    Calculates recommended staffing by looking up the matrix.csv based on PID and PR values.
    """
    # Step 1: Load matrix
    matrix = {}
    try:
        with open("cplh.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                site_key = row["Site"]
                cplh = row["CPLH"]
                matrix[(site_key)] = cplh
    except FileNotFoundError:
        print("cplh.csv not found. Aborting headcount calculation.")
        return sites_dict

    # Step 2: Calculate per-site recommended staffing using binned logic
    for site in sites_dict:
        # Lookup from matrix
        key = (site)
        sites_dict[site]["recommended_staffing"] = int(sites_dict[site]["to_jobs"]/float(matrix.get(key, 0))/10)  # Default to 0 if missing

    return sites_dict


def pull_actuals(sites_dict, driver):
    """
    Downloads FCLM reports for each site and process, aggregates unique function-employee pairs,
    and sums Paid Hours to determine actual staffing.
    """
    # Process info
    processes = {
        "Transfer Out": 1003021,
    }

    # Load timezone deltas
    tz_df = pd.read_csv("timezones.csv")
    tz_lookup = dict(zip(tz_df["Site"], tz_df["Delta to EST"]))

    # Prep timestamp
    now = datetime.now()

    for site in sites_dict:
        site_delta = tz_lookup.get(site, 0)
        local_now = now + timedelta(hours=site_delta)

        start_minute = 0
        end_minute = 0

        current_minute = local_now.minute

        if current_minute < 10:
            start_hour = local_now.hour - 1
            start_minute = 30
            end_hour = start_hour
            end_minute = 45
        elif current_minute < 25:
            start_hour = local_now.hour - 1
            start_minute = 45
            end_hour = local_now.hour
            end_minute = 0
        elif current_minute < 40:
            start_hour = local_now.hour
            start_minute = 0
            end_hour = local_now.hour
            end_minute = 15
        elif current_minute < 55:
            start_hour = local_now.hour
            start_minute = 15
            end_hour = local_now.hour
            end_minute = 30
        else:
            start_hour = local_now.hour
            start_minute = 30
            end_hour = local_now.hour
            end_minute = 45

        #if current_minute > 15:
        #    start_hour = local_now.hour - 1
        #else:
        #    start_hour = local_now.hour - 2

        if start_hour < 0:
            # edge case: crosses midnight
            start_hour += 24
            local_now -= timedelta(days=1)

        #end_hour = (start_hour + 1) % 24
        if start_hour == 23 and end_hour == 0:
            start_date = local_now - timedelta(days=1)
            end_date = local_now
        else:
            start_date = local_now
            end_date = local_now
        #end_date = local_now if start_hour < 23 else local_now + timedelta(days=1)

        # Format time
        start_date_str = start_date.strftime("%Y/%m/%d")
        end_date_str = end_date.strftime("%Y/%m/%d")
        start_dt_local = datetime.combine(start_date.date(), datetime.min.time()) + timedelta(hours=start_hour) + timedelta(minutes=start_minute)
        end_dt_local = datetime.combine(end_date.date(), datetime.min.time()) + timedelta(hours=end_hour) + timedelta(minutes=end_minute)
        start_dt_utc = (start_dt_local - timedelta(hours=site_delta)).replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")
        end_dt_utc = (end_dt_local - timedelta(hours=site_delta)).replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")

        total_hours = 0

        for process_name, process_id in processes.items():
            url = (
                f"https://fclm-portal.amazon.com/reports/functionRollup?"
                f"reportFormat=CSV&warehouseId={site}&processId={process_id}&maxIntradayDays=1"
                f"&spanType=Intraday&startDateIntraday={start_date_str}&startHourIntraday={start_hour}"
                f"&startMinuteIntraday={start_minute}&endDateIntraday={end_date_str}&endHourIntraday={end_hour}"
                f"&endMinuteIntraday={end_minute}"
            )

            driver.execute_script(f"window.open('{url}', '_blank');")

            filename = f"functionRollupReport-{site}-{process_name}-Intraday-{start_dt_utc}-{end_dt_utc}.csv"
            filepath = os.path.join(os.getcwd(), filename)

            if test_mode:
                print(f"[INFO] Downloading {filename} from {url}")
            # Wait for download (max 30s)
            for _ in range(15):
                if os.path.exists(filepath):
                    print(f"[INFO] Downloaded {filename}")
                    if test_mode:
                        time.sleep(5) #test mode
                    break
                time.sleep(1)
            if not os.path.exists(filepath):
                driver.execute_script(f"window.open('{url}', '_blank');")
                for _ in range(15):
                    if os.path.exists(filepath):
                        break
                    time.sleep(1)
                if not os.path.exists(filepath):
                    print(f"[WARN] File did not download: {filename}")
                    continue

            try:
                df = pd.read_csv(filepath)
                if df.empty or "Employee Id" not in df.columns or "Function Name" not in df.columns:
                    print(f"[WARN] Missing required data in {filename}")
                    continue

                dedup_df = df.drop_duplicates(subset=["Employee Id", "Function Name"])
                dedup_df = dedup_df[~dedup_df["Function Name"].isin(["Bin Scout Trans", "Cart Runner Trans", "Tote Stacking", "Transfer In Ambssdor", "Transfer In Training", "PrEditor Receive"])]
                if "Paid Hours-Total(function,employee)" in dedup_df.columns:
                    hours = dedup_df["Paid Hours-Total(function,employee)"].sum()
                    total_hours += hours
                else:
                    print(f"[WARN] 'Paid Hours' column not found in {filename}")
                print("I should be trying to delete the file now")
                if test_mode:
                    time.sleep(5)
                

            except Exception as e:
                print(f"[ERROR] Could not process {filename}: {e}")
            finally:
                print("I am trying to delete the file now")
                if os.path.exists(filepath):
                    print(f"[INFO] Deleting {filename}")
                    os.remove(filepath)

        sites_dict[site]["actual staffing"] = round(total_hours*4)
        print(f"[INFO] {site} - Actual Staffing: {sites_dict[site]['actual staffing']} hours")

    return sites_dict

def pull_tot(sites_dict, driver):
    """
    Downloads tot reports for each site and process, sums hours.
    """

    # Load timezone deltas
    tz_df = pd.read_csv("timezones.csv")
    tz_lookup = dict(zip(tz_df["Site"], tz_df["Delta to EST"]))

    # Prep timestamp
    now = datetime.now()

    for site in sites_dict:
        site_delta = tz_lookup.get(site, 0)
        local_now = now + timedelta(hours=site_delta)

        current_minute = local_now.minute
        if current_minute > 15:
            start_hour = local_now.hour - 1
        else:
            start_hour = local_now.hour - 2

        if start_hour < 0:
            # edge case: crosses midnight
            start_hour += 24
            local_now -= timedelta(days=1)

        end_hour = (start_hour + 1) % 24
        end_date = local_now if start_hour < 23 else local_now + timedelta(days=1)

        # Format time
        local_date_str = local_now.strftime("%Y/%m/%d")
        start_dt_local = datetime.combine(local_now.date(), datetime.min.time()) + timedelta(hours=start_hour)
        end_dt_local = start_dt_local + timedelta(hours=1)
        start_dt_utc = (start_dt_local - timedelta(hours=site_delta)).replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")
        end_dt_utc = (end_dt_local - timedelta(hours=site_delta)).replace(tzinfo=ZoneInfo("America/New_York")).astimezone(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")

        total_hours = 0

        url = (
            f"https://fclm-portal.amazon.com/reports/timeOnTask?"
            f"reportFormat=CSV&warehouseId={site}&maxIntradayDays=30"
            f"&spanType=Intraday&startDateIntraday={local_date_str}&startHourIntraday={start_hour}"
            f"&startMinuteIntraday=0&endDateIntraday={end_date.strftime('%Y/%m/%d')}&endHourIntraday={end_hour}"
            f"&endMinuteIntraday=0"
        )

        driver.execute_script(f"window.open('{url}', '_blank');")

        filename = f"timeOffTask-ppr-{site}-{local_now.strftime("%Y%m%d")}0000-{end_date.strftime("%Y%m%d")}0000.csv"
        filepath = os.path.join(os.getcwd(), filename)

        if test_mode:
            print(f"[INFO] Downloading {filename} from {url}")
        # Wait for download (max 30s)
        for _ in range(15):
            if os.path.exists(filepath):
                print(f"[INFO] Downloaded {filename}")
                if test_mode:
                    time.sleep(5) #test mode
                break
            time.sleep(1)
        if not os.path.exists(filepath):
            driver.execute_script(f"window.open('{url}', '_blank');")
            for _ in range(15):
                if os.path.exists(filepath):
                    break
                time.sleep(1)
            if not os.path.exists(filepath):
                print(f"[WARN] File did not download: {filename}")
                continue

        try:
            df = pd.read_csv(filepath)
            if df.empty or "Time On Task" not in df.columns or "Total Time" not in df.columns:
                print(f"[WARN] Missing required data in {filename}")
                continue

            #dedup_df = df.drop_duplicates(subset=["Employee Id", "Function Name"])
            total_hours = df["Total Time"].sum()-df["Time On Task"].sum()
            print("I should be trying to delete the file now")
            if test_mode:
                time.sleep(5)
            

        except Exception as e:
            print(f"[ERROR] Could not process {filename}: {e}")
        finally:
            print("I am trying to delete the file now")
            if os.path.exists(filepath):
                print(f"[INFO] Deleting {filename}")
                os.remove(filepath)

        sites_dict[site]["site_tot"] = round(total_hours)
        print(f"[INFO] {site} - TOT: {sites_dict[site]['site_tot']} hours")

    return sites_dict   

def calculate_deltas(sites_dict):
    """
    Calculates deltas to recommended and glidepath.
    """
    for site in sites_dict:
        actual = sites_dict[site]["actual staffing"]
        rec = sites_dict[site]["recommended_staffing"]
        sites_dict[site]["delta_to_recommended"] = actual - rec
    return sites_dict


def format_slack_message(sites_dict):
    """
    Formats the final Slack message with a table of the staffing data
    and includes highest-overrun and highest-total sites.
    """
    header = f"{'Site':<6} {'Goal HC':>8} {'Actual HC':>10} {'HC Δ':>8}"
    lines = [header, "-" * len(header)]

    # Identify sites with max delta_to_glidepath
    sorted_by_glidepath_delta = sorted(sites_dict.items(), key=lambda x: x[1]["delta_to_recommended"], reverse=True)
    bottom1_staffing_site, bottom1_staffing_data = sorted_by_glidepath_delta[0]
    bottom2_staffing_site, bottom2_staffing_data = sorted_by_glidepath_delta[1]
    bottom3_staffing_site, bottom3_staffing_data = sorted_by_glidepath_delta[2]
    bottom1_staffing_delta = bottom1_staffing_data["delta_to_recommended"]
    bottom2_staffing_delta = bottom2_staffing_data["delta_to_recommended"]
    bottom3_staffing_delta = bottom3_staffing_data["delta_to_recommended"]

    # Identify site with max site_tot
    sorted_by_site_tot = sorted(sites_dict.items(), key=lambda x: x[1].get("site_tot", 0), reverse=True)
    bottom1_tot_site, bottom1_tot_data = sorted_by_site_tot[0]
    bottom2_tot_site, bottom2_tot_data = sorted_by_site_tot[1]
    bottom3_tot_site, bottom3_tot_data = sorted_by_site_tot[2]
    bottom1_tot_delta = bottom1_tot_data.get("site_tot", 0)
    bottom2_tot_delta = bottom2_tot_data.get("site_tot", 0)
    bottom3_tot_delta = bottom3_tot_data.get("site_tot", 0)

    # Build table
    for site, data in sorted_by_glidepath_delta:
        line = (
            f"{site:<6} "
            f"{data['recommended_staffing']:>8} "
            f"{data['actual staffing']:>10} "
            f"{data['delta_to_recommended']:>8}"
        )
        lines.append(line)

    message = "\n".join(lines)

    return {
        "text": message,
        "bottom1_staffing_site": bottom1_staffing_site,
        "bottom2_staffing_site": bottom2_staffing_site,
        "bottom3_staffing_site": bottom3_staffing_site,
        "bottom1_staffing_delta": str(bottom1_staffing_delta),
        "bottom2_staffing_delta": str(bottom2_staffing_delta),
        "bottom3_staffing_delta": str(bottom3_staffing_delta),
        "bottom1_tot_site": bottom1_tot_site,
        "bottom2_tot_site": bottom2_tot_site,
        "bottom3_tot_site": bottom3_tot_site,
        "bottom1_tot_delta": str(bottom1_tot_delta),
        "bottom2_tot_delta": str(bottom2_tot_delta),
        "bottom3_tot_delta": str(bottom3_tot_delta)
    }


# main

def main():

    # Launch browser for manual authentication
    print("Launching Firefox for Midway auth... you have 20 seconds.")
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.getcwd())
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    driver = selenium_wire_webdriver.Firefox(options=options)
    driver.get("https://atoz.amazon.work/")  # Or the exact URL you want to pre-auth

    #time.sleep(7200)
    time.sleep(30)  # Wait for manual login and cert push
    print("Auth window complete. Continuing...")

    sites_dict = create_sites_dict()

    update_goals(sites_dict, driver)
    
    #hourly update
    while True:

        if (datetime.now().hour > 9 and datetime.now().hour <14) or (datetime.now().hour > 21) or datetime.now().hour < 2:
            update_goals(sites_dict, driver)
        sites_dict = get_shift_goals(sites_dict)
        sites_dict = calculate_recommended_staffing(sites_dict)
        #sites_dict = apply_glidepath(sites_dict)

        #while (datetime.now().minute < 41):
        #    time.sleep(60)
        sites_dict = pull_actuals(sites_dict, driver)
        sites_dict = pull_tot(sites_dict, driver)
        sites_dict = calculate_deltas(sites_dict)
        
        slack_payload = format_slack_message(sites_dict)

        #while (datetime.now().minute > 10):
        #    time.sleep(60)

        response = requests.post(SLACKBOT_URL, json=slack_payload)
        if response.status_code != 200:
            print(f"Slack post failed with status code {response.status_code}: {response.text}")
        else:
            print("Slack message sent successfully.")

        # Sleep for an hour before the next update
        time.sleep(3600)



if __name__ == "__main__":
    main()
