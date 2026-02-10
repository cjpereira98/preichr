import time
#import keyboard
from datetime import date
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def Open_Main_TOT():
    driver.get(totUrl)
    driver.find_element(By.XPATH, xpathHide).click()

def Get_Number_Of_Links():
    links = []
    links = driver.find_elements(By.CLASS_NAME, 'tot-row')
    #links = driver.find_elements_by_class_name('tot-row')
    return len(links)

def Open_Links(linkNum, pausedSpot):
    tabcount = 0
    for x in range(pausedSpot ,linkNum):  # replace 10 with linkNum limited for now
        actions = ActionChains(driver)
        print('Checking {} out of {}'.format(x, linkNum))
        xpath2 = '//*[@id="content-penal"]/table/tbody/tr[{}]/td[1]/a'.format(x)
        link = driver.find_element(By.XPATH, xpath2)
        
        percentXpath = '/html/body/div[4]/div[2]/table/tbody/tr[{}]/td[6]'.format(x)
        
        if driver.find_element(By.XPATH, percentXpath).text != '0':
            if driver.find_element(By.XPATH, (xpath2)).text != '':
                element = driver.find_element(By.XPATH, (xpath2))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
                tabcount += 1
            else:
                continue

        if tabcount == 5:
            tabPause = tabcount
            return tabPause, 'pause', x
    return tabcount, 'end'

def Get_Most_Recent(processList):
    try:
        duplicates = {}
        for i in set(processList):
            duplicates[i] = processList.count(i)
        return  max(duplicates, key=duplicates.get)
    except:
        print('Error, no recent labor tracking!')
        return 'Error!'

def Function_Breakdown(mostTracked):
    primaryFunction = mostTracked[:mostTracked.find('♦')]
    secondaryFunction = mostTracked[-(len(mostTracked) - mostTracked.find('♦')):].replace('♦' ,'')

    return primaryFunction, secondaryFunction

def Sleep_time(sleeptime, reason):
    for x in range(1, sleeptime +1):
        print('Pause for {}, {}/{}'.format(reason, x, sleeptime))
        time.sleep(1)

def Change_Tot(totSpots, mostTracked):
    print('Changing All TOT to: {}'.format(mostTracked))
    ##Sleep_time(5, 'Verify Function')

    failedCounter = 0
    retryFailedCounter = 0
    retrySpots = []
    closebutton = '//*[@id="tot"]/div/div[1]/a/span'
    submitButton = '//*[@id="totSubmit"]'

    primaryFunction = Function_Breakdown(mostTracked)[0]
    secondaryFunction = Function_Breakdown(mostTracked)[1]

    for index, x in enumerate(totSpots):
        xpath = '//*[@id="content-panel"]/div[1]/table/tbody/tr[{}]/td[5]/p'.format(x)
        try:
            driver.find_element(By.XPATH, (xpath)).click()
        except:
            print('testing timeout')
            timeout = 10
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(driver, timeout).until(element_present)

            driver.find_element(By.XPATH, (xpath)).click()

        select = Select(driver.find_element(By.XPATH, ('//*[@id="newLaborProcessId"]')))
        select.select_by_visible_text(primaryFunction)

        print('testing timeout')
        timeout = 10
        element_present = EC.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(driver, timeout).until(element_present)

        #try:
        print('Trying Tot Spot {}/{}...'.format(index +1, len(totSpots)))
        select = Select(driver.find_element(By.XPATH, ('//*[@id="newLaborFunctionId"]')))
        ##Sleep_time(2, 'Pause')
        select.select_by_visible_text(secondaryFunction)
        driver.find_element(By.XPATH, (submitButton)).click()

        Sleep_time(5, 'Loading Submit')
        a = Alert(driver)
        a.accept()

        print('Dissmissing Success Message.')

        if index + 1 < len(totSpots):
            Sleep_time(10, 'Loading Refresh')
        # except:

        #     driver.find_element(By.XPATH, (closebutton)).click()
        #     failedCounter += 1
        #     retrySpots.append(x)
        #     print('Failed')

    successPercent = (len(totSpots) - failedCounter) / len(totSpots)
    print("Success Percent: {:.0%}".format(successPercent))

    if len(retrySpots) > 0:
        print('Failed {} Edits out of {}.'.format(failedCounter, len(totSpots)))
        print('Retrying {} Edits...'.format(len(retrySpots)))

        for index, x in enumerate(retrySpots):
            #Sleep_time(10, 'Loading Secondairies (RETRY)')
            xpath = '//*[@id="content-panel"]/div[1]/table/tbody/tr[{}]/td[5]/p'.format(x) 
            driver.find_element(By.XPATH, (xpath)).click()

            select = Select(driver.find_element(By.XPATH, ('//*[@id="newLaborProcessId"]')))
            select.select_by_visible_text(primaryFunction)


            try:
                print('Retrying Tot Spot {}/{}...'.format(index +1, len(totSpots)))
                select = Select(driver.find_element(By.XPATH, ('//*[@id="newLaborFunctionId"]')))
                
                select.select_by_visible_text(secondaryFunction)
                driver.find_element(By.XPATH, (submitButton)).click()

                #Sleep_time(10, 'Loading Submit')
                a = Alert(driver)
                a.accept()
                print('Dissmissing Success Message.')

                if index + 1 < len(retrySpots):
                    Sleep_time(10, 'Loading Refresh')
            except:
                driver.find_element(By.XPATH, (closebutton)).click()
                retryFailedCounter += 1
                print('Failed')

        successPercent = (len(retrySpots) - retryFailedCounter) / len(retrySpots)
        successPercent = "Success Percent: {:.0%}".format(successPercent)

        if retryFailedCounter > 0:
            print('{} of Retries Successful! ({} failed out of {}).'.format(successPercent, retryFailedCounter, len(retrySpots)))
        else:
            print(('{} of Retries Successful! ({} failed out of {}).'.format(successPercent, retryFailedCounter, len(retrySpots))))
    else:
        print('Edits for this AA Complete, continue to Next.')

def Switch_Tabs(currentTab, tabCount):
    if currentTab == 0:
        print('Moving to next tab group!')
        driver.switch_to.window(driver.window_handles[currentTab])
    else:
        tabPer = (currentTab-1)/tabCount[0]
        print('Moving to AA #{}/{}.  {:.0%} Complete!'.format(currentTab, tabCount[0], tabPer))
        driver.switch_to.window(driver.window_handles[currentTab])

def Fix_TOT(getAllFunctions,trimDateMonth, noTrack):
    list2 = []
    processList = []
    totSpots = []
    
    for index, x in enumerate(getAllFunctions):
        x = x[:x.find(trimDateMonth)].strip()
        
        if x.find('Time Off Task') != -1:
            totSpots.append(index + 1)
            list2.append(x)
        else:
            list2.append(x)

        #print(list2)
        
        if x.find('♦') > 1:
            # make list of what they were tasked into previously
            processList.append(x)
            
    #print(processList)

    mostTracked = Get_Most_Recent(processList)
    #print(mostTracked)
    
    #print(totSpots) ##############

    if len(totSpots) > 0:
        if not(mostTracked in noTrack):
            if not(mostTracked in autoTrack):
                changeTot = input('This AA was mostly tracked into: {}. Would you like to copy this for ALL the AA\'s TOT? y/n: '.format(mostTracked))
                if changeTot == 'y':
                    Change_Tot(totSpots, mostTracked)
                else:
                    noTrack.append(mostTracked)
                    print('-------------------Edit Diverted, Continue to Next. ------ {}'.format(mostTracked))
            else: 
                print('-------------------Path is in Auto Track list! Changing TOT. ------ {}'.format(mostTracked))
                Change_Tot(totSpots, mostTracked)
        else:
            print('-------------------Edit Diverted, Continue to Next. ------ {}'.format(mostTracked))
    else:
        print('No TOT found for this AA! Continue to Next.')

    print('No Track: {}'.format(noTrack))

def Get_All_Functions():  # call after opening to 1 aa
    #Sleep_time(1, 'Loading AA page.')
    xpathAllFunctions = 'table.ganttChart > tbody:nth-child(2)'

    r = str(driver.find_element(By.CSS_SELECTOR, xpathAllFunctions).text)
    #r = r.replace('♦', '♦')
    
    r = r.splitlines()
    #print(r)
    
    return r

def Fix_TOT_URL(): 
    get_url = str(driver.current_url)
    #print("The current url is:"+get_url)
    
    x = get_url.find(';')   #len(get_url)
    url1 = get_url[:x]
    url2 = get_url[get_url.find('?'):]

    fixed_url = url1 + url2

    return fixed_url
    


noTrack = ['Prep Recorder♦PrepRcvUniversal.INT', 'RC Sort♦RC Sort Primary', 'Transfer Out♦Palletize - Case', 'Transfer Out Dock♦Dock Pallet Loader','Error!','LP-Receive♦PrEditor Receive','Transfer Out♦Fluid Load - Case', 'Receive-Support♦Decant Non-TI', 'RC Sort♦UIS_5lb_ToteWrangle', 'Admin/HR/IT♦TOM_YARD_CHECKIN/OUT', 'Case Transfer In♦Case Transfer In', 'UnrecognizedProcess♦UnrecognizedFunction', 'Transfer In Dock♦Decant','Each-Receive♦ReceiveUniversal.INT', 'Transfer Out♦Fluid Load - Tote', 'Transfer Out Dock♦Pallet Movement', 'Each-Receive♦ReceiveUniversal.BEG', 'Prep Recorder♦PrepRcvUniversal.BEG', 'RC Sort♦UIS_5lb_Induct', 'Each-Receive♦Each Receive', 'LP-Receive♦Depalletize-CP']

autoTrack = ['Transfer Out♦Wall Builder', 'Receive Dock♦Receive Line Loader', 'IB Problem Solve♦Stow to Prime PSolve', 'Receive Dock♦Receive Dock Crew', 'Transfer Out Dock♦TransferOut DockCrew', 'Transfer Out♦Water Spider', 'Transfer Out Dock♦Ship Clerk', 'Receive-Support♦MHE Support', 'Transfer Out♦Robotic Water Spider', 'Transfer Out Lead/PA♦Transfer Out Lead/PA', 'Inbound Lead/PA♦Dock Lead/PA', 'Receive-Support♦Rcv WaterSpider', 'RC Sort♦Water Spider', 'Transfer Out♦Trans Out Overflow']

today = date.today()
yesterday = date.today() - timedelta(days=1)

todayS = str(today)
yesterdayS = str(yesterday)

driver = webdriver.Firefox()
driver.implicitly_wait(60)
totUrl = 'https://fclm-portal.amazon.com/reports/timeOnTask?reportFormat=HTML&warehouseId=SWF2&maxIntradayDays=30&spanType=Intraday&startDateIntraday=2024%2F11%2F07&startHourIntraday=6&startMinuteIntraday=15&endDateIntraday=2024%2F11%2F08&endHourIntraday=0&endMinuteIntraday=0'
xpathHide = '//*[@id="hideRows"]'  # xpath for hide button, cant veri

trimDateMonth = str(today.strftime('%m/'))    #uncomment this to make it work for this month

Open_Main_TOT()
linkNum = Get_Number_Of_Links()
tabCount = Open_Links(linkNum, 1)

while tabCount[1] == 'pause':
    for currentTab in range(1, tabCount[0] + 1):
        Switch_Tabs(currentTab, tabCount)
        fixed_url = Fix_TOT_URL()
        driver.get(fixed_url)
        
        Fix_TOT(Get_All_Functions(), trimDateMonth, noTrack)

    for closeTabNum in reversed(range(1, 6)):
        Switch_Tabs(closeTabNum, tabCount)
        driver.close()

    Switch_Tabs(0, tabCount)

    #Open_Main_TOT()
    tabCount = Open_Links(linkNum, tabCount[2])  # linknum stays the same, because hiding the others does nothing.

for currentTab in range(1, tabCount[0] + 1):
    Switch_Tabs(currentTab, tabCount)
    Fix_TOT(Get_All_Functions(), trimDateMonth, noTrack)

print(noTrack)

driver.quit()