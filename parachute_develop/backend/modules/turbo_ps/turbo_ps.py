import os
import sys
import threading
import logging
from selenium import webdriver
from random import choice
from time import sleep
from urllib3 import PoolManager


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from integrations.dj import DirectedJackpotIntegration
from integrations.firefox import FirefoxIntegration
from integrations.sideline import SidelineIntegration
from integrations.container_research import ContainerResearchIntegration
from integrations.unbind import UnbindIntegration
from integrations.fc_research import FCResearchIntegration

# Set up logging
logging.basicConfig(filename='turbo_ps.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

driver_lock = threading.Lock()
driver_in_use = {}


def get_available_driver(driver_pool):
    with driver_lock:
        for driver in driver_pool:
            if not driver_in_use.get(driver, False):
                driver_in_use[driver] = True
                return driver
        return None

def release_driver(driver):
    with driver_lock:
        driver_in_use[driver] = False

def main(driver_pool=None, elapsed_minutes=5):
    if not driver_pool:
        driver_pool = FirefoxIntegration.get_authenticated_driver_pool(fcm_auth=True, num_drivers=5)  # Default to pool of 20 drivers

    # Get a random driver from the pool for each integration
    cr_driver = get_available_driver(driver_pool)
    container_research = ContainerResearchIntegration(cr_driver)

    dj_driver = get_available_driver(driver_pool)
    dj_integration = DirectedJackpotIntegration(dj_driver)

    sl_driver = get_available_driver(driver_pool)
    sideline_integration = SidelineIntegration(sl_driver)

    ub_driver = get_available_driver(driver_pool)
    unbind_integration = UnbindIntegration(ub_driver)

    fr_driver = get_available_driver(driver_pool)
    fr_integration = FCResearchIntegration(fr_driver)

    # Start threads for continuous operation
    cr_thread = threading.Thread(target=container_research.watch_ps, args=(dj_integration,))
    dj_thread = threading.Thread(target=dj_integration.inf_parse, args=(sideline_integration,unbind_integration, fr_integration))
    sideline_thread = threading.Thread(target=sideline_integration.inf_overage)
    ub_thread = threading.Thread(target=unbind_integration.inf_unbind, args=(dj_integration,))
    fr_thread = threading.Thread(target=fr_integration.inf_research, args=(sideline_integration,))


    cr_thread.start()
    dj_thread.start()
    sideline_thread.start()
    ub_thread.start()
    fr_thread.start()

    # Join threads to ensure they run continuously
    cr_thread.join()
    dj_thread.join()
    sideline_thread.join()
    ub_thread.join()
    fr_thread.join()

    
    #recent_containers = container_research.get_recent_containers(elapsed_minutes)
    #with open(containers_file, 'w') as file:
    #    for container in recent_containers:
    #        file.write(f"{container}\n")
    #container_research.close()

    #if not os.path.exists(containers_file):
    #    print(f"{containers_file} not found in the current working directory.")
    #    return

    #with open(containers_file, 'r') as file:
    #    containers = [line.strip() for line in file.readlines()]

    #dj_integration = DirectedJackpotIntegration(driver)
    #invalid_routing, invalid_container, virtually_empty = dj_integration.parse_containers(containers)

    #print(f"Invalid Routing Containers: {invalid_routing}")
    #print(f"Invalid Containers: {invalid_container}")
    #print(f"Virtually Empty Containers: {virtually_empty}")

    #if not os.path.exists(invalid_containers_file):
    #    print(f"{invalid_containers_file} not found in the current working directory.")
    #    return

    #with open(invalid_containers_file, 'r') as file:
    #    invalid_containers = [line.strip() for line in file.readlines()]

    #sideline_integration = SidelineIntegration(driver)
    #sideline_integration.overage_containers(invalid_containers)

    #dj_integration.close()
    # sideline_integration.close()

if __name__ == "__main__":
    main()
