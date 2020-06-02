from gamma import *
from dataHandler import *

RISK_FREE_RATE = 0.069
offset = 30 # hist_volatility_window calculation window
dataset_size = initiateDatabase()
# constantly need to look at historical volatility and decide whether to long or short gamma
idx = offset
status = 'NO_POSITION'

for i in range(idx, dataset_size):
    hist_volatility = getHistoricalVolatility(idx)

    S = getSpotPrice(idx, 'avg')
    K = S
    curr_date = getCurrentDate(idx)
    T = (getMonthEnd(curr_date) - curr_date).days / 365
    r = RISK_FREE_RATE
    impl_volatility = getImpliedVolatility(S, K, T, r, idx)
    
    if impl_volatility < hist_volatility:
        status = 'long'
        idx = i
        break
    elif impl_volatility > hist_volatility:
        status = 'short'
        idx = i
        break

S = getSpotPrice(idx)
K = S
curr_date = getCurrentDate(idx)
expiry_date = getMonthEnd(curr_date)
T = (expiry_date - curr_date).days / 365

gamma_scalp = GammaScalping('ABC', S, K, T, T, 1, 1, RISK_FREE_RATE, curr_date, status)
print("Balance after delta hedge = {}".format(gamma_scalp.balance))

for i in range(idx, dataset_size):
    curr_date = getCurrentDate(idx)
    if curr_date > expiry_date:
        break
    gamma_scalp.deltaHedge(i)
    print("Balance after delta hedge = {}".format(gamma_scalp.balance))
