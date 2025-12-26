import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options for headless browsing if desired
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Uncomment to run headless
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')


# Start the browser
browser = webdriver.Chrome(options=chrome_options)

# Load cookies from file (exported from Chrome)
import os
cookie_file = os.path.join(os.path.dirname(__file__), 'turo_cookies.json')
if os.path.exists(cookie_file):
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
    # Go to Turo home page to set domain
    browser.get('https://turo.com')
    for cookie in cookies:
        # Remove fields not accepted by Selenium
        cookie.pop('sameSite', None)
        cookie.pop('storeId', None)
        cookie.pop('hostOnly', None)
        cookie.pop('session', None)
        cookie.pop('id', None)
        # Selenium expects expiry as int, not float
        if 'expirationDate' in cookie:
            cookie['expiry'] = int(cookie.pop('expirationDate'))
        try:
            browser.add_cookie(cookie)
        except Exception as e:
            print(f"Could not add cookie: {cookie.get('name')} ({e})")

# Human-like delay function
def human_delay(min_sec=1.5, max_sec=3.5):
    import random
    time.sleep(random.uniform(min_sec, max_sec))

# Target Turo search URL
url = "https://turo.com/us/en/search?country=US&defaultZoomLevel=11&deliveryLocationType=city&endDate=&endTime=&flexibleType=NOT_FLEXIBLE&isMapSearch=false&itemsPerPage=200&latitude=27.7671271&location=St.%20Petersburg%2C%20FL%2C%20USA&locationType=CITY&longitude=-82.6384451&monthlyEndDate=01%2F19%2F2026&monthlyStartDate=10%2F19%2F2025&pickupType=ALL&placeId=ChIJQao6aWPmwogR_4vUvANAzAQ&region=FL&searchDurationType=DAILY&sortType=RELEVANCE&startDate=&startTime=&useDefaultMaximumDistance=true"

browser.get(url)
human_delay(2, 4)

# Wait for the page to load (adjust selector as needed)
WebDriverWait(browser, 10).until(lambda driver: False)
human_delay(1, 2)

# Get browser logs to find the API response (requires Chrome logging enabled)
logs = browser.get_log('performance')
api_url_fragment = '/api/v2/search'
api_response = None
for entry in logs:
    msg = entry.get('message', '')
    if api_url_fragment in msg and 'response' in msg:
        try:
            data = json.loads(msg)
            url = data['message']['params']['request']['url']
            if api_url_fragment in url:
                api_response = url
                break
        except Exception:
            continue

if api_response:
    print(f"API URL found: {api_response}")
    # Optionally, you can fetch the data using browser.execute_script or requests with cookies
else:
    print("API response not found in browser logs. Try enabling performance logging.")

# Clean up
browser.quit()
