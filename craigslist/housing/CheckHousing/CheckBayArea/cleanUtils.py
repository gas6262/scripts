import hashlib
import time

def cleanHood(hood):

    hood = hood.replace('(','')
    hood = hood.replace(')','')
    hood = hood.replace(' ','')
    hood = hood.split("/")[0]
    return hood

def getPrice(priceText):

    priceText = priceText.replace('$','')
    priceText = priceText.replace(',','')
    priceText.strip()
    price = int(priceText)
    return price

def getPostId(date, title):

    hash = hashlib.sha1()
    enc = (str(date) + title).encode('utf-8')
    hash.update(enc)

    h = hash.hexdigest()
    return h

def parseHousing(hI, housingJson):

    if 'br' in hI:
        val = hI.replace("\n", "").replace("br", "").strip()
        housingJson['br'] = int(val)

    elif 'ft' in hI:
        val = hI.replace("\n", "").replace("ft", "").strip()
        housingJson['ft'] = int(val)

    return housingJson

def getHousing(post):

    housingArea = post.find('span', class_='housing')

    housingJson = {
        "br": None,
        "size": None
    }

    if housingArea:
        housingText = housingArea.text.strip()
        housingArray = housingText.split("-")

        for hI in housingArray:
            housingJson = parseHousing(hI, housingJson)

    return housingJson

    