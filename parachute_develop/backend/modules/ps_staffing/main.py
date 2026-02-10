import time
import schedule
import subprocess

def run_ps_report():
    subprocess.run(["python", "run_ps_report.py"])

def run_throttle_ps_hours():
    subprocess.run(["python", "throttle_ps_hours.py"])

def scheduler():
    # Schedule run_ps_report.py at 08:00 AM and 08:00 PM
    schedule.every().day.at("08:00").do(run_ps_report)
    schedule.every().day.at("20:00").do(run_ps_report)

    # Schedule throttle_ps_hours.py at the specified times
    times = ["01:30", "02:00", "03:00", "04:00", "07:15", "08:00", "09:00", "10:00", "11:00",
             "13:15", "14:00", "15:00", "16:00", "19:15", "20:00", "21:00", "22:00", "23:00"]
    
    for t in times:
        schedule.every().day.at(t).do(run_throttle_ps_hours)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    scheduler()