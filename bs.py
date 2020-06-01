import numpy as np
import scipy.stats as si
from dataHandler import *

# S : spot price
# K : strike price
# T : time to expiry (in years)
# r : risk free interest rate (in decimal)
# sigma : volatility (in decimal)
# days : number of trading days per year
def getPrice(S, K, T, r, sigma, option):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    if option == 'call':
        result = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    if option == 'put':
        result = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return result

def getImpliedVolatility(S, K, T, r, idx):
    C = getOptionPrice(idx, 'call', 'avg')
    res = C / (0.4 * S * np.exp(-r * T) * np.sqrt(T))
    # np.sqrt((np.log(K / S) - r * T) / (T * (Er + 3 / 2))) # formula fron another research paper
    return res

def getDelta(S, K, T, r, sigma, option):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = si.norm.cdf(d1, 0.0, 1.0)
    if option == 'put':
        result = -si.norm.cdf(-d1, 0.0, 1.0)
    return result

def getGamma(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T))
    return result

def getTheta(S, K, T, r, sigma, option, days):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    if option == 'put':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0)
    return result / days

def getVega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T)
    return result
