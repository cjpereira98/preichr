import time
import schedule
import subprocess
import os

def gen_ti_report():
    script_path = os.path.join(os.path.dirname(__file__), 'ti_report.py')
    subprocess.run(['python', script_path])

def schedule_tasks():
    # Schedule the task to run every day at 7:30 AM
    schedule.every().day.at("08:00").do(gen_ti_report)

if __name__ == "__main__":
    schedule_tasks()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
