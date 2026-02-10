import datetime
import subprocess
import os


#Missing metric for area audit completion!
#DIOT should look back to a different day

def main():
    today = datetime.datetime.today().weekday()
    
    if today == 0:  # Monday
        designations = ['prior-week', 'wtd']
    else:
        designations = ['prior-day']

    for designation in designations:
        print(f"Running report for {designation}")
        script_path = os.path.join(os.path.dirname(__file__), 'deep_dive_report.py')
        subprocess.run(['python', script_path, designation])

if __name__ == "__main__":
    main()
