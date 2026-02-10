import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# Add the parent directory to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integrations.firefox import FirefoxIntegration

class CedricIntegration:
    def __init__(self, driver=None):
        if driver:
            self.driver = driver
        else:
            self.driver = FirefoxIntegration.get_authenticated_driver()
        self.wait = WebDriverWait(self.driver, 30)

    def get_response(self, message):
        self.driver.get("https://console.harmony.a2z.com/internal-ai-assistant/")

        # Wait for the textarea to be visible and enter the message
        textarea = self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "textarea[aria-label='input-message'][placeholder='Message Cedric...']")
        ))
        time.sleep(3)
        textarea.send_keys(message)

        # Wait for the submit button to be visible and click it
        submit_button = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.awsui_variant-primary_vjswe_1nbam_248[data-analytics-funnel-value^='button:r1g:']")
        ))
        submit_button.click()

        # Wait for the response message to be visible and return the text
        response_div = self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.chat-bubble.chat-assistant.right-left-display > div > div.awsui_text-content_6absk_1ct3v_98")
        ))
        time.sleep(3)
        response_message = response_div.text

        return response_message

if __name__ == "__main__":
    # Test the CedricIntegration
    cedric = CedricIntegration()
    response = cedric.get_response("Hello Cedric!")
    print("Cedric's Response:", response)

    # Keep the browser open for a short while to manually inspect
    time.sleep(10)
    cedric.driver.quit()
