# Parachute modules
import subprocess
import time
import os
from config.config import SCRIPTS_DIR
from src.ampy.integrations.firefox import FirefoxIntegration
from src.ampy.integrations.slack import SlackIntegration  # Import SlackIntegration

# Web Server modules
from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
    possible_scripts = ['main.py', 'run.py']
    for script in possible_scripts:
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

    script_dirs = discover_script_directories(SCRIPTS_DIR)
    for script_dir in script_dirs:
        print(f'Starting {script_dir}... in {SCRIPTS_DIR}')
        script_path = os.path.join(SCRIPTS_DIR, script_dir)
        processes[script_dir] = start_process(script_path)
    monitor_processes()

# Setup APIs
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/ps_staffing/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="ps_staffing.html", context={"id": id}
    )

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}