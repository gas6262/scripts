import re
import requests
import os
from bs4 import BeautifulSoup

zillowUrlsFile = os.path.join(os.path.dirname(__file__), "listings.txt")
zillowUrlsFile = os.path.join(os.path.dirname(__file__), "listings.txt")
with open(zillowUrlsFile, "r") as f:
    zillowUrls = [line.strip() for line in f if line.strip()]

# Set your cookie string here if needed
cookie = r"...your cookie string..."
headers = {"Cookie": cookie} if cookie else {}

for zillowUrl in zillowUrls:
    response = requests.get(zillowUrl, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Search all script tags for 'agentName' JSON
    agent_name = None
    for script in soup.find_all("script"):
        if script.string and '"agentName"' in script.string:
            match = re.search(r'"agentName"\s*:\s*"([^"]+)"', script.string)
            if match:
                agent_name = match.group(1)
                break

    if agent_name:
        print(f"Agent Name: {agent_name}")
    else:
        print("Agent Name not found")
