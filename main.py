from gamma import *
from dataHandler import *
import configparser

config = configparser.ConfigParser()
config.readfp(open(r'config.txt'))

RISK_FREE_RATE = int(config.get('Variable Section', 'rate'))
STRIKE_PRICE = int(config.get('Variable Section', 'strike_price'))
ROLLLING_WINDOW_SIZE = int(config.get('Variable Section', 'offset')) # window size on which historical volatility is calculated
# if historical volatility is not calculated use rolling hash
dataset_size = initiateDatabase(ROLLLING_WINDOW_SIZE)
openOutputFile()

idx = ROLLLING_WINDOW_SIZE
status = 'NO_POSITION'

for i in range(idx, dataset_size):
    hist_volatility = getHistoricalVolatility(idx)

    S = getSpotPrice(idx, RISK_FREE_RATE, 'avg')
    K = STRIKE_PRICE
    curr_date = getCurrentDate(idx)
    T = (getMonthEnd(curr_date) - curr_date).days / 365
    r = RISK_FREE_RATE
    impl_volatility = getImpliedVolatility(S, K, T, r, idx)
    # if its precalculated just return it
    
    if impl_volatility < hist_volatility:
        status = 'long'
        idx = i
        break
    elif impl_volatility > hist_volatility:
        status = 'short'
        idx = i
        break

S = getSpotPrice(idx, RISK_FREE_RATE, 'avg')
K = STRIKE_PRICE
curr_date = getCurrentDate(idx)
expiry_date = getMonthEnd(curr_date)
T = (expiry_date - curr_date).days / 365

gamma_scalp = GammaScalping('ABC', S, K, T, T, 1, 1, RISK_FREE_RATE, curr_date, status)
print("Initiated {} Gamma Scalping".format(status))
print("Balance after delta hedge = {}".format(gamma_scalp.balance))

for i in range(idx, dataset_size):
    curr_date = getCurrentDate(idx)
    if curr_date > expiry_date:
        break
    gamma_scalp.deltaHedge(i)
    print("Balance after delta hedge = {}".format(gamma_scalp.balance))

closeOutputFile()
