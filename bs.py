import numpy as np
import scipy.stats as si
from dataHandler import *
from requestHandler import *

# S : spot price
# K : strike price
# T : time to expiry (in years)
# r : risk free interest rate (in decimal)
# sigma : volatility (in decimal)
# days : number of trading days per year
def getOptionPremiumBS(S, K, T, r, sigma, option):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    if option == 'call':
        result = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    if option == 'put':
        result = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return result

def getImpliedVolatilityBS(S, K, T, r, idx, precision):
    C = getOptionPremium(idx, 'call', 'avg')
    # res = C / (0.4 * S * np.exp(-r * T) * np.sqrt(T)) 
    # return res
    # np.sqrt((np.log(K / S) - r * T) / (T * (Er + 3 / 2))) # formula fron another research paper
    iv_start = 0
    iv_end = 1
    while True:
        mid  = (iv_end + iv_start) / 2
        price_on_mid = getOptionPremiumBS(S, K, T, r, mid, 'call')
        # print("at mid = {}, actual iv = {}, price on mid : {}, C : {}".format(mid, getImpliedVolatility(idx),price_on_mid, C))
        if price_on_mid > C:
            iv_end = mid
        else:
            iv_start = mid
        if np.abs(price_on_mid - C) < precision:
            break
    return mid 

def getDeltaBS(S, K, T, r, sigma, option):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = si.norm.cdf(d1, 0.0, 1.0)
    if option == 'put':
        result = -si.norm.cdf(-d1, 0.0, 1.0)
    return result

def getGammaBS(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T))
    return result

def getThetaBS(S, K, T, r, sigma, option, days):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    if option == 'put':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0)
    return result / days

def getVegaBS(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T)
    return result

# print(getDelta(100, 100, .086, .069, .1, 'call'))
# print(getImpliedVolatility(424.85, 420, 22/365, 0.069, 1))
# print(getDelta(425, 420, 22/365, 0.069, 0.04, 'call') + getDelta(425, 420, 22/365, 0.069, 0.04, 'put'))
# initiateDatabase(100)
# C = getOptionPremium(0, 'call', 'avg')
# print(C)