import time
import subprocess

def run_jambot():
    try:
        # Run the jambot.py script
        subprocess.run(["python", "jambot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running jambot.py: {e}")

if __name__ == "__main__":
    while True:
        # Run jambot.py
        run_jambot()
        
        # Wait for 5 minutes (300 seconds) before running again
        time.sleep(300)
