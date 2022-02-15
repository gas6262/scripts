import time
from selenium import webdriver
from datetime import date
import datetime

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# Start te webdriver
driver = webdriver.Chrome()

baseUrl = "https://www.sevenrooms.com"
location = "topgolfsanjose"
partySize = 6
golftime = "7:00PM"
isDebug = False

# Get date string
week = datetime.timedelta(days=7)
today = date.today() + week
d = today.strftime("%Y-%m-%d")
'golfTimeValue' = datetime.datetime.strptime(golftime,'%I:%M%p')
print("d = ", d)

url = f"{baseUrl}/reservations/{location}?default_date={d}&default_party_size={partySize}&default_time={golftime}"

driver.get(url)

if(isDebug):
    text_file = open("dump.html", "w")
    n = text_file.write(driver.page_source)
    text_file.close()

# Load the search button and click it
WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[text()="Search"]'))).click()

WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="sr-side-scroll-row-main"]/button')))
slots = driver.find_elements_by_xpath('//*[@id="sr-side-scroll-row-main"]/button/div')

timeSlots = [{'timestring':s.text, 'dif':abs(golfTimeValue - datetime.datetime.strptime(s.text,'%I:%M %p')), 'parent':s.parent} for s in slots if s.text.endswith('m')]

# Raise an exception if there are no slots available
if(len(timeSlots) == 0):
    raise Exception('No golf slots are available')

timeSlots.sort(key=lambda x: x['dif'], reverse=True)

print("Selecting slot " + timeSlots[0]['timestring'])

timeSlots[0]['parent'].click()

print("Selecting slot " + timeSlots[0]['timestring'])