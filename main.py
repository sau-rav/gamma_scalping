import configparser
from gamma import *
from dataHandler import *
from functions import *
from requestHandler import * 

config = configparser.ConfigParser()
config.readfp(open(r'config.txt'))

RISK_FREE_RATE = float(config.get('Variable Section', 'rate'))
STRIKE_PRICE = float(config.get('Variable Section', 'strike_price'))
ROLLLING_WINDOW_SIZE = int(config.get('Variable Section', 'rolling_window_size')) # window size on which historical volatility is calculated
SZ_CONTRACT = int(config.get('Variable Section', 'contract_size'))
NUM_CALL = int(config.get('Variable Section', 'num_call_to_trade'))
NUM_PUT = int(config.get('Variable Section', 'num_put_to_trade'))
IV_TOLERENCE = float(config.get('Variable Section', 'iv_tolerence'))
IV_HV_DIFF_TOLERENCE = float(config.get('Variable Section', 'iv_hv_diff_tolerence')) # difference over which IV and HV diff will not be tolerated and some position will be taken
NEG_SIGNAL_TOLERENCE = int(config.get('Variable Section', 'neg_signal_tolerence')) # count of negative signal that will be tolerated, after this reverse position will be taken

dataset_size = initiateDatabase(ROLLLING_WINDOW_SIZE)
# dataset_size = ROLLLING_WINDOW_SIZE + 10 # for now(let) for calculation purpose
openOutputFile()

idx = ROLLLING_WINDOW_SIZE
STATUS = 'NEUTRAL'
SIGNAL = 'NEUTRAL'
LAST_SIGNAL = 'NEUTRAL'
neg_signal_count = 1
gamma_scalp = None

for i in range(idx, dataset_size):
    hist_volatility = getHistoricalVolatility(i) * 100 # in percent format

    S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
    curr_date = getCurrentDate(i)
    T = (getExpiryDate(curr_date) - curr_date).days / 365
    impl_volatility = getImpliedVolatilityBS(S, STRIKE_PRICE, T, RISK_FREE_RATE, i, IV_TOLERENCE) * 100 # in percent format
    # impl_volatility = getImpliedVolatility(i)
    # print("implied volatility : {}, calculated : {}".format(impl_volatility, impl_volatility))
    # print("historical volatility {} %, implied volatility {} %".format(hist_volatility, impl_volatility))
    
    if impl_volatility < hist_volatility and abs(impl_volatility - hist_volatility) > IV_HV_DIFF_TOLERENCE: # some difference tolerence
        LAST_SIGNAL = SIGNAL
        SIGNAL = 'SHORT'  # long
    elif impl_volatility > hist_volatility and abs(impl_volatility - hist_volatility) > IV_HV_DIFF_TOLERENCE:
        LAST_SIGNAL = SIGNAL
        SIGNAL = 'LONG'  # short
    else:
        LAST_SIGNAL = SIGNAL
        SIGNAL = 'NEUTRAL'

    if STATUS == 'NEUTRAL' and SIGNAL == STATUS:
        continue
    elif STATUS == 'NEUTRAL' and SIGNAL != STATUS:
        if SIGNAL == LAST_SIGNAL:
            neg_signal_count += 1
        else:
            neg_signal_count = 1
        if neg_signal_count >= NEG_SIGNAL_TOLERENCE:
            STATUS = SIGNAL
            writePositionDataToFile(i, STATUS + ' START')
            gamma_scalp = GammaScalping('ABC', S, STRIKE_PRICE, T, T, NUM_CALL, NUM_PUT, SZ_CONTRACT, RISK_FREE_RATE, curr_date, STATUS, i, IV_TOLERENCE)
            neg_signal_count = 0
    elif SIGNAL == 'NEUTRAL' or STATUS == SIGNAL:
        gamma_scalp.deltaHedge(i)
        if SIGNAL == 'NEUTRAL':
            neg_signal_count = 0
    else:
        neg_signal_count += 1
        if neg_signal_count >= NEG_SIGNAL_TOLERENCE:
            gamma_scalp.closePosition(i)
            writePositionDataToFile(i, STATUS + ' EXIT')
            STATUS = SIGNAL
            writePositionDataToFile(i, STATUS + ' START')
            gamma_scalp = GammaScalping('ABC', S, STRIKE_PRICE, T, T, NUM_CALL, NUM_PUT, SZ_CONTRACT, RISK_FREE_RATE, curr_date, STATUS, i, IV_TOLERENCE)

closeOutputFile()
