from gamma import *
from dataHandler import *
import configparser

config = configparser.ConfigParser()
config.readfp(open(r'config.txt'))

RISK_FREE_RATE = 0.069 # int(config.get('Variable Section', 'rate'))
STRIKE_PRICE = 100 # int(config.get('Variable Section', 'strike_price'))
ROLLLING_WINDOW_SIZE = 0 # int(config.get('Variable Section', 'offset')) # window size on which historical volatility is calculated
# if historical volatility is not calculated use rolling hash
dataset_size = initiateDatabase(ROLLLING_WINDOW_SIZE)
openOutputFile()

idx = ROLLLING_WINDOW_SIZE
status = 'NO_POSITION'

for i in range(idx, dataset_size):
    hist_volatility = getHistoricalVolatility(i)

    # S = getSpotPrice(idx, RISK_FREE_RATE, 'avg')
    # K = STRIKE_PRICE
    # curr_date = getCurrentDate(idx)
    # T = (getMonthEnd(curr_date) - curr_date).days / 365
    # r = RISK_FREE_RATE
    # impl_volatility = getImpliedVolatility(S, K, T, r, idx)
    impl_volatility = getIVFromDataset(i)
    # if its precalculated just return it
    # print("historical volatility {}, implied volatility {}".format(hist_volatility, impl_volatility))
    
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

print("\nInitialising {} Gamma Scalping at idx {}".format(status, idx))
gamma_scalp = GammaScalping('ABC', S, K, T, T, 1, 1, RISK_FREE_RATE, curr_date, status, idx)
print("Balance after delta hedge = {}\n".format(gamma_scalp.balance))

for i in range(idx+1, dataset_size):
    curr_date = getCurrentDate(idx)
    if curr_date > expiry_date:
        break
    gamma_scalp.deltaHedge(i)
    print("Balance after delta hedge = {}\n".format(gamma_scalp.balance))

closeOutputFile()
