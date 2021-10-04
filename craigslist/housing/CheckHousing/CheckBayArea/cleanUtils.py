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