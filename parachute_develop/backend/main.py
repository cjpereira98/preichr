# Standard Library Imports
import os
import sys
import subprocess
import time
from typing import List

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Parachute Modules
from config.config import CONTROLLER_DIR
from src.integrations.firefox import FirefoxIntegration
from src.integrations.slack import SlackIntegration

processes = {}

def send_slack_message(message):
    # Slack webhook URL for notifications
    webhook_url = 'https://hooks.slack.com/workflows/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'

    # Prepare the message
    slack_message = {
        "message": message
    }

    # Send the message via SlackIntegration
    SlackIntegration.send_message(webhook_url, slack_message)

def discover_script_directories(directory):
    return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

def find_entry_script(directory):
    entry_points = ['main.py', 'run.py']
    for script in entry_points:
        script_path = os.path.join(directory, script)
        if os.path.isfile(script_path):
            return script_path
    return None

def start_process(script_dir):
    script_path = find_entry_script(script_dir)
    if script_path:
        send_slack_message(f"Starting process for {script_dir}")
        return subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print(f"No entry script found in {script_dir}")
        return None

def restart_process(script_dir):
    if script_dir in processes:
        processes[script_dir].terminate()
        processes[script_dir].wait()
        send_slack_message(f"Restarting process for {script_dir} after termination")
    processes[script_dir] = start_process(script_dir)

def monitor_processes():
    while True:
        for script_dir, process in list(processes.items()):
            if process and process.poll() is not None:  # Process has terminated
                print(f'{script_dir} terminated, restarting...')
                send_slack_message(f"Process for {script_dir} terminated unexpectedly, restarting...")
                restart_process(script_dir)
        time.sleep(1)

if __name__ == '__main__':
    # Check if the machine is authenticated
    try:
        driver = FirefoxIntegration.get_authenticated_driver()
        driver.quit()
    except Exception as e:
        send_slack_message("Failed to authenticate. Exiting...")
        print("Failed to authenticate. Exiting...")
        exit(1)

    script_dirs = discover_script_directories(CONTROLLER_DIR)
    for script_dir in script_dirs:
        print(f'Starting {script_dir}... in {CONTROLLER_DIR}')
        script_path = os.path.join(CONTROLLER_DIR, script_dir)
        processes[script_dir] = start_process(script_path)
    monitor_processes()
