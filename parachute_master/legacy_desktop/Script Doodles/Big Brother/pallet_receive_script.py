import csv
import glob
import os
import re
import time
import threading
from datetime import datetime, timedelta
from urllib.parse import quote

import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# ============ CONFIG ============
# Exactly seven buckets (one per browser window)
SITES_BUCKETS = [
    ["LGB8", "ONT8", "LAS1", "LAX9"],
    ["FTW1", "MEM1", "MQJ1", "CLT2"],
    ["SMF3", "TEB9", "FWA4", "IND9"],
    ["GYR2", "IAH3", "ORF2", "GYR3"],
    ["RDU2", "RFD2", "RMN3", "MDW2"],
    ["AVP1", "SWF2", "ABE8"],
    ["VGT2", "MCC1", "SBD1", "SCK4"],
]

OUTPUT_CSV = "ytd_pr.csv"
PROCESS_ID = 1003032  # Pallet Receive
AUTH_URL = "https://atoz.amazon.work/"
DOWNLOAD_MIME = "text/csv"

# Time you get to log in per browser before we start pulling (tweak if needed)
AUTH_GRACE_SECONDS = 210

# ============ HELPERS ============

def sunday_of_week(d: datetime) -> datetime:
    # Return the Sunday of the week containing date d (Sunday=6 by weekday())
    return d - timedelta(days=(d.weekday() + 1) % 7)

def ytd_sundays_until_last_sunday(today: datetime) -> list[datetime]:
    jan1 = datetime(today.year, 1, 1)
    first_sun = jan1 if jan1.weekday() == 6 else (jan1 + timedelta(days=(6 - jan1.weekday())))
    last_sun = sunday_of_week(today)  # last completed Sunday (or today if Sunday)
    weeks = []
    cur = first_sun
    while cur <= last_sun:
        weeks.append(cur)
        cur += timedelta(days=7)
    return weeks

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def make_driver(download_dir: str) -> webdriver.Firefox:
    opts = Options()
    opts.set_preference("browser.download.folderList", 2)
    opts.set_preference("browser.download.dir", download_dir)
    opts.set_preference("browser.helperApps.neverAsk.saveToDisk", DOWNLOAD_MIME)
    opts.set_preference("pdfjs.disabled", True)
    drv = webdriver.Firefox(options=opts)
    drv.set_page_load_timeout(180)
    return drv

def wait_for_new_csv(prefix_glob: str, preexisting: set[str], timeout_s: int = 60) -> str | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        current = set(glob.glob(prefix_glob))
        new_files = list(current - preexisting)
        if new_files:
            newest = max(new_files, key=os.path.getmtime)
            time.sleep(2)  # let the file finish writing
            return newest
        time.sleep(1)
    return None

def parse_pr_pallets(csv_path: str) -> int | float | None:
    """
    Parse pr pallets by summing 'Jobs' for rows where 'Unit Type' == 'Case'.
    """
    import pandas as pd

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[ERROR] Could not read {csv_path}: {e}")
        return None

    # If the file is empty or missing required columns, bail out early
    if df.empty or "Unit Type" not in df.columns or "Jobs" not in df.columns:
        print(f"[WARN] Missing 'Unit Type' or 'Jobs' in {csv_path}")
        return None

    # Filter down to just Case rows
    case_df = df[df["Unit Type"].astype(str).str.strip().eq("Case")]

    if case_df.empty:
        return 0  # no Case rows, return zero

    # Sum the Jobs column
    try:
        total = case_df["Jobs"].sum(numeric_only=True)
        return float(total)
    except Exception as e:
        print(f"[ERROR] Failed to sum Jobs in {csv_path}: {e}")
        return None


    # Fallback: first numeric column sum
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            try:
                return float(df[c].sum())
            except Exception:
                pass

    return None

def build_weekly_url(site: str, week_start: datetime) -> str:
    """
    Mirrors the provided weekly URL shape.
    startDateDay: a day within the week (use Monday = week_start + 1)
    startDateWeek: the Sunday that starts the week
    """
    monday = week_start + timedelta(days=1)
    day_str = monday.strftime("%Y/%m/%d")
    week_str = week_start.strftime("%Y/%m/%d")
    q_day = quote(day_str, safe="")
    q_week = quote(week_str, safe="")
    return (
        f"https://fclm-portal.amazon.com/reports/functionRollup?"
        f"reportFormat=CSV&warehouseId={site}&processId={PROCESS_ID}"
        f"&startDateDay={q_day}&spanType=Week&startDateWeek={q_week}"
        f"&maxIntradayDays=1&startHourIntraday=0&startMinuteIntraday=0"
        f"&endHourIntraday=0&endMinuteIntraday=0"
    )

# ============ WORKER ============

write_lock = threading.Lock()

def worker(site_list: list[str], out_path: str, tmp_dir: str, ytd_weeks: list[datetime]):
    ensure_dir(tmp_dir)
    driver = make_driver(tmp_dir)

    try:
        # Manual auth: open AtoZ and give time to sign in
        try:
            driver.get(AUTH_URL)
        except Exception:
            pass
        time.sleep(AUTH_GRACE_SECONDS)

        for site in site_list:
            for wk in ytd_weeks:
                url = build_weekly_url(site, wk)

                # Snapshot preexisting files
                pattern = os.path.join(tmp_dir, f"functionRollupReport-{site}*.csv")
                preexisting = set(glob.glob(pattern))

                # Request the CSV in a new tab
                driver.execute_script(f"window.open('{url}','_blank');")

                csv_file = wait_for_new_csv(pattern, preexisting, timeout_s=90)
                if not csv_file:
                    # One retry in case of flake
                    csv_file = wait_for_new_csv(pattern, preexisting, timeout_s=30)

                if not csv_file:
                    print(f"[WARN] No CSV for {site} week {wk.date()} (URL: {url})")
                    continue

                try:
                    val = parse_pr_pallets(csv_file)
                except Exception as e:
                    print(f"[ERROR] Failed to parse {csv_file}: {e}")
                    val = None

                if val is not None:
                    with write_lock:
                        with open(out_path, "a", newline="") as f:
                            w = csv.writer(f)
                            num = int(val) if float(val).is_integer() else float(val)
                            w.writerow([site, wk.strftime("%Y-%m-%d"), num])

                try:
                    os.remove(csv_file)
                except Exception:
                    pass

    finally:
        try:
            driver.quit()
        except Exception:
            pass

# ============ MAIN ============

def main():
    today = datetime.now()
    weeks = ytd_sundays_until_last_sunday(today)

    # Prepare output header
    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["site", "week", "presort_cartons"])

    threads = []
    for i, bucket in enumerate(SITES_BUCKETS):
        tmp_dir = os.path.abspath(f"./_downloads_worker_{i+1}")
        t = threading.Thread(target=worker, args=(bucket, OUTPUT_CSV, tmp_dir, weeks), daemon=True)
        threads.append(t)
        t.start()
        time.sleep(1.5)  # small stagger

    for t in threads:
        t.join()

    print(f"[DONE] Wrote YTD presort to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
