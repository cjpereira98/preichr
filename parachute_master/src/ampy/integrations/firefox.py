import os
import sys
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import BADGE, FCMPASS, FC

class FirefoxIntegration:
    @staticmethod
    def get_authenticated_driver(fcm_auth=False, hidden=False):
        """
        Returns a Selenium WebDriver instance using the specified Firefox profile for authentication.
        If hidden is set to True, the browser will run in headless mode.
        
        :param fcm_auth: Whether to perform FCM authentication.
        :param hidden: Whether to run the browser in headless mode.
        :return: A Selenium WebDriver instance.
        """
        # Load environment variables from .env file
        load_dotenv()

        # Get the Firefox profile path from environment variables
        profile_path = os.getenv('FIREFOX_PROFILE_DIR')

        options = Options()
        options.profile = webdriver.FirefoxProfile(profile_path)

        #experimental
        options.profile.set_preference("browser.sessionstore.resume_from_crash", False)
        options.profile.set_preference("browser.sessionstore.enabled", False)
        options.profile.set_preference("app.update.enabled", False)
        options.profile.set_preference("browser.safebrowsing.enabled", False)
        options.profile.set_preference("browser.safebrowsing.malware.enabled", False)
        options.profile.set_preference("extensions.enabledScopes", 0)
        options.profile.set_preference("extensions.autoDisableScopes", 15)

        #end experimental

        # Set up Firefox options for downloading files (if needed)
        download_dir = os.getcwd()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Enable headless mode if hidden is True
        if hidden:
            options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)

        driver.get("https://atoz.amazon.work/home")
        time.sleep(2)

        # Check for multiple tabs and close the second tab if it exists
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
            driver.close()
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])

        # Wait for the authenticated element
        try:
            # Verify if the current URL starts with "https://atoz"
            if not driver.current_url.startswith("https://atoz"):
                print("Authentication failed or timed out.")
                driver.quit()
                raise Exception("Failed to authenticate")
        except Exception as e:
            print("Authentication failed or timed out.")
            driver.quit()
            raise e
        
        if fcm_auth:
            driver.get("https://fcmenu-iad-regionalized.corp.amazon.com/secure/login")
            driver.find_element(By.ID, "badgeBarcodeId").send_keys(BADGE + Keys.ENTER)
            time.sleep(1)
            driver.find_element(By.ID, "password").send_keys(FCMPASS + Keys.ENTER)
            time.sleep(10)

            # Enter the FC site code into the site selection field
            site_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "qlInput"))
            )
            site_input.send_keys(FC + Keys.ENTER)
            time.sleep(3)

        return driver
    
    @staticmethod
    def get_authenticated_driver_pool(fcm_auth, num_drivers, hidden=False):
        """
        Returns a pool of authenticated Selenium WebDriver instances sequentially.
        If hidden is set to True, the browsers will run in headless mode.
        
        :param fcm_auth: Whether to perform FCM authentication.
        :param num_drivers: The number of drivers to create in the pool (between 2 and 20).
        :param hidden: Whether to run the browsers in headless mode.
        :return: A list of authenticated WebDriver instances.
        """
        # Ensure num_drivers is between 2 and 20
        num_drivers = max(2, min(20, num_drivers))

        # List to store the drivers
        driver_pool = []

        for _ in range(num_drivers):
            try:
                driver = FirefoxIntegration.get_authenticated_driver(fcm_auth, hidden=hidden)
                driver_pool.append(driver)
            except Exception as e:
                print(f"Failed to create driver: {e}")

        return driver_pool
