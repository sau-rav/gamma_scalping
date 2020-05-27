from data import *

def sellRequest(quantity, idx):
    price = getSpotPrice(idx)
    return price * quantity

def buyRequest(quantity, idx):
    price = getSpotPrice(idx)
    return -price * quantity
