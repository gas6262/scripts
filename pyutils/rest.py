import requests

def getJson(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def getText(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text