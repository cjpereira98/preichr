from selenium import webdriver
from selenium.webdriver.common.by import By
from random import choice, random
import time

# Initialize WebDriver
driver = webdriver.Chrome()  # Replace with your browser's driver

# Open the target web page
driver.get("https://apollo-audit.corp.amazon.com/audits/new?audit_type_id=8673")  # Replace with your form's URL

#time to authenticate
time.sleep(20)

#Get logins to process
with open('logins.txt', 'r') as file:
    logins = file.read().splitlines()

# Function to fill and submit the form
def fill_and_submit_form(iteration, two_logins):
    # Fill the Dock Door Number
    dock_door_number = 212 + iteration
    driver.find_element(By.ID, "audit_properties_Dock Door #").send_keys(str(dock_door_number))

    # Set fixed dropdown values
    driver.find_element(By.ID, "audit_properties_Shift").send_keys("FHD")
    driver.find_element(By.ID, "audit_properties_Auditor Login").send_keys("preichr")
    driver.find_element(By.ID, "audit_properties_Auditor Role").send_keys("AM")
    driver.find_element(By.ID, "audit_properties_Are all associates and/or managers wearing hard hats while inside the trailer").send_keys("Yes")

    # Fluid unload - conditional setting
    if dock_door_number in [211, 214, 215, 218, 219, 222]:
        driver.find_element(By.ID, "audit_properties_Is fluid unload occurring inside a trailer? If yes, please select the safety mechanism in place").send_keys("DeStuff-It")
    else:
        driver.find_element(By.ID, "audit_properties_Is fluid unload occurring inside a trailer? If yes, please select the safety mechanism in place").send_keys("Step Stool")

    # Random selection for unloading stage
    unloading_stages = ["Front of Trailer", "Middle of Trailer", "End of Trailer "]
    driver.find_element(By.ID, "audit_properties_What stage of unloading are they inside the trailer").send_keys(choice(unloading_stages))

    #time.sleep(15)
    #Checkboxes with probabilities
    if random() < 0.8:
        label_xpath = "//label[input[@id='audit_properties_Is the quality of the wall safe? Select all unsafe observations below or N/A if safe. If unsafe, escalate to leadership!_are_the_boxes_leaning_towards_the_associate']]"
        driver.find_element(By.XPATH, label_xpath).click()
        label_xpath = "//label[input[@id='audit_properties_Is the quality of the wall safe? Select all unsafe observations below or N/A if safe. If unsafe, escalate to leadership!_na']]"
        driver.find_element(By.XPATH, label_xpath).click()



    # Set fixed values for remaining fields and deselect checkboxes
    # Add similar lines for other fields as per your requirements
        
    # Select No to controlled fall
    driver.find_element(By.ID, "audit_properties_Is a controlled fall require").send_keys("No")

    driver.find_element(By.ID, "audit_properties_If controlled fall required, was a controlled fall completed").send_keys("N/A")

    # Select Yes to feeling safe
    driver.find_element(By.ID, "audit_properties_Does the associate feel safe working inside the trailer").send_keys("Yes")

    #Deselect improper grip
    label_xpath = "//label[input[@id='audit_properties_Are the Associates following the proper procedure to unload the trailer? If not, select all that apply._improper_grip']]"
    driver.find_element(By.XPATH, label_xpath).click()
    
    #select N/A for AA issues
    label_xpath = "//label[input[@id='audit_properties_Are the Associates following the proper procedure to unload the trailer? If not, select all that apply._na']]"
    driver.find_element(By.XPATH, label_xpath).click()   

    #deselect no lights
    label_xpath = "//label[input[@id='audit_properties_Overall Environment_no_lights']]"
    driver.find_element(By.XPATH, label_xpath).click()

    #select n/a for trailer issues
    label_xpath = "//label[input[@id='audit_properties_Overall Environment_na']]"
    driver.find_element(By.XPATH, label_xpath).click()

    #select yes for jam pole
    driver.find_element(By.ID, "audit_properties_Is there a jam pole or tool available controlled falls at this trailer door? (there should be one pole for every two doors)").send_keys("No")

    #Select yes for good working order
    driver.find_element(By.ID, "audit_properties_Is the flex conveyor or DeStuff-It in good working order with no visible defects or damage").send_keys("Yes")

    #Select n/a for coaching provided by leadership
    driver.find_element(By.ID, "audit_properties_If applicable, was coaching provided by leadership").send_keys("N/A")

    #Input N/A for employee login
    driver.find_element(By.ID, "apollo-employee-login").send_keys(two_logins[0] + "," + two_logins[1])

    #95% chance of no congestion
    if random() < 0.85:
        driver.find_element(By.ID, "audit_properties_Is any congestion observed in the designated 5s locations on Inbound/Outbound dock").send_keys("No")
    else:
        driver.find_element(By.ID, "audit_properties_Is any congestion observed in the designated 5s locations on Inbound/Outbound dock").send_keys("Yes")

    #95% chance of no boxes on built walls
    if random() < 0.95:
        driver.find_element(By.ID, "audit_properties_Are there any boxes located on top of built walls that are not properly secured down and could potentially cause a falling risk").send_keys("No")
    else:
        driver.find_element(By.ID, "audit_properties_Are there any boxes located on top of built walls that are not properly secured down and could potentially cause a falling risk").send_keys("Yes")

    driver.find_element(By.ID, "audit_properties_Check for De-Stuff-It Safety Devices Being Tampered").send_keys("No")



    # Wait and Review the form before submission
    time.sleep(5)  # Adjust time as needed for review

    # Uncomment the next line to submit the form
    driver.find_element(By.ID, "audit-submit").click()

# Loop to fill and submit the form 10 times
for i in range(10):
    two_logins = logins[:2]
    del logins[:2]
    fill_and_submit_form(i, two_logins)
    # Add a delay if needed between form submissions
    time.sleep(5)  # Adjust time as needed


# Close the browser when done
driver.quit()