import time
import os
import sys
import pyautogui
from selenium import webdriver
from turbo_ps import main as turbo_ps_main

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from ampy.integrations.firefox import FirefoxIntegration

def run_continuously(driver_pool):
    last_run_timestamp = time.time()
    while True:
        pyautogui.moveRel(1, 0, duration=0.1)  # Move mouse 1 pixel to the right
        pyautogui.moveRel(-1, 0, duration=0.1)  # Move mouse 1 pixel to the left
        current_timestamp = time.time()
        elapsed_minutes = min(int((current_timestamp - last_run_timestamp) / 60), 60)
        if elapsed_minutes == 0:
            elapsed_minutes = 5  # Default to 5 minutes if it's the first run or elapsed time is less than 1 minute
        turbo_ps_main(driver_pool, elapsed_minutes)
        last_run_timestamp = current_timestamp
        time.sleep(10)  # Wait for 10 seconds before running again (adjust as necessary)

if __name__ == "__main__":
    driver_pool = FirefoxIntegration.get_authenticated_driver_pool(fcm_auth=True, num_drivers=5)  # Create a pool of 5 drivers
    run_continuously(driver_pool)
