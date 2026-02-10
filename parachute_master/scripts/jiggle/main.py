import time
import os
import sys
import pyautogui
import platform

# Append the path for importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from ampy.integrations.firefox import FirefoxIntegration

pyautogui.FAILSAFE = False  # Disable the fail-safe

def prevent_sleep():
    """
    Platform-specific function to prevent the computer from going to sleep.
    """
    if platform.system() == "Windows":
        # For Windows, use ctypes to prevent sleep
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000003)
    elif platform.system() == "Darwin":
        # For macOS, use caffeinate to prevent sleep
        os.system("caffeinate -u -t 3600 &")  # Prevent sleep for 1 hour
    elif platform.system() == "Linux":
        # For Linux, use xdotool to move the mouse
        os.system("xdotool key shift")  # Simulate a key press to prevent sleep

if __name__ == "__main__":
    prevent_sleep()
    while True:
        # Move the mouse slightly to prevent sleep as a fallback
        pyautogui.moveRel(10, 0, duration=0.1)  # Move mouse 1 pixel to the right
        pyautogui.moveRel(-10, 0, duration=0.1)  # Move mouse 1 pixel to the left
        time.sleep(10)  # Wait for 10 seconds before running again (adjust as necessary)
