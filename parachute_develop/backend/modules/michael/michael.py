import os
import sys
import threading
import traceback
import subprocess

# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../decant_tote_audit')))

from integrations.slack import SlackIntegration
import main

def send_slack_message(message):
    # Slack webhook URL
    webhook_url = 'https://hooks.slack.com/workflows/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'

    # Prepare the message
    slack_message = {
        "message": message
    }

    # Send the message via SlackIntegration
    SlackIntegration.send_message(webhook_url, slack_message)

def pull_top_offenders():
    try:
        # Notify Slack that MICHAEL is starting the process
        send_slack_message("I am starting to pull top offenders.")

        # Run update_percent.py after downloading the csv file
        os.system('python ../decant_tote_audits/main.py')

    except Exception as e:
        # Send an error message to Slack if something goes wrong
        error_message = f"I encountered an error: {str(e)}\n{traceback.format_exc()}"
        send_slack_message(error_message)

def run_in_thread():
    thread = threading.Thread(target=pull_top_offenders)
    thread.start()

if __name__ == "__main__":
    run_in_thread()
