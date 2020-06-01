from dataHandler import *

def sellRequest(quantity, idx):
    price = getSpotPrice(idx, 'bid')
    return price * quantity

def buyRequest(quantity, idx):
    price = getSpotPrice(idx, 'ask')
    return -price * quantity
