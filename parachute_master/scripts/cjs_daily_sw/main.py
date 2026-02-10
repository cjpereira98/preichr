import os
import sys
import glob
import time
import schedule
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Add necessary directories to system path for importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from ampy.integrations.ppr import ProcessPathRollupIntegration
from ampy.integrations.firefox import FirefoxIntegration
from ampy.integrations.slack import SlackIntegration

from config.config import FC

# Main entry point
if __name__ == "__main__":
    # Needs to be run with an argument to specify 'prior day', 'prior week', or 'week to date'

    firefox_integration = FirefoxIntegration()
    driver = firefox_integration.get_authenticated_driver()

    # use integrations to download the following data - these integrations need to be capable of processing the input 'prior day', 'prior week', or 'week to date'
    # historical big box
    # dense adjusted dump
    # historical cplh dump
    # IBD blended dump
    # hours versus shift plan detail
    # total building shift plan
    # shift plan audit
    # miscellaneous hours deep dive

    # calculate a bunch of metrics

    # CPLH ACT v GOAL
    # act cplh
    # op cplh
    # mix adj op cplh

    # FINANCE
    # Hours gain/loss to dense adj op
    # Non Controllable Cost Impact
    # Non FC Controllable Hours
    # Controllable Dense Adj OP Impact
    # Controllable Cost impact

    # SHIFT PLAN
    # % to shift Plan CPLH
    # Abs Hours Shift Plan Deviation
    # Total Hours to Plan
    # SP % to Raw OP
    # SP % to Mix Adj OP
    # Excess Hours to Plan
    # Abs Hours Variance
    # SP CC
    # SP % to Adjusted CC

    # BIG BOX
    # Adj CC
    # PR Pallets
    # CPP Pallet Delta Adj
    # PR CPP Immpact
    # % to Adj CC

    # IBD BLENDED
    # Planned IBD Blended
    # Actual IBD Blended
    # Planned Online Blended
    # Actual Online Blended

    # VET/VTO
    # Recommendation
    # VET Posted
    # VTO Posted
    # VET Accepted
    # VTO Accepted
    # VET Take Rate
    # VTO Take Rate


    driver.quit()
    #scheduler()