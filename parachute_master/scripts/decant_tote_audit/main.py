import os
import sys
import schedule
import time
import subprocess

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

#from scripts.decant_tote_audit.get_top_offenders import get_top_offenders

def run_get_top_offenders():
    script_path = os.path.join(os.path.dirname(__file__), 'get_top_offenders.py')
    subprocess.run(['python', script_path])

def schedule_tasks():
    # Define the schedule
    times = ["08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00",
             "20:00", "21:00", "22:00", "23:00", "00:00", "02:00", "03:00", "04:00"]

    for run_time in times:
        schedule.every().day.at(run_time).do(run_get_top_offenders)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_tasks()
