import time
from selenium import webdriver
from datetime import date
import datetime

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()  # Optional argument, if not specified will search path.

baseUrl = "https://www.sevenrooms.com"
location = "topgolfsanjose"
partySize = 6
golftime = "7:00PM"
isDebug = False

# Get date string
week = datetime.timedelta(days=7)
today = date.today() + week
d = today.strftime("%Y-%m-%d")
print("d = ", d)

url = f"{baseUrl}/reservations/{location}?default_date={d}&default_party_size={partySize}&default_time={golftime}"

driver.get(url)

if(isDebug):
    text_file = open("dump.html", "w")
    n = text_file.write(driver.page_source)
    text_file.close()

# Load the search button and click it
WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[text()="Search"]'))).click()

