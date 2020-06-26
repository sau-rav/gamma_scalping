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
SQUARE_OFF_COUNT = int(config.get('Variable Section', 'square_off_count'))
# FIRST_SIGNAL_TOLERENCE = int(config.get('Variable Section', 'first_signal_tolerence'))

dataset_size = initiateDatabase(ROLLLING_WINDOW_SIZE, STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE)
# dataset_size = ROLLLING_WINDOW_SIZE + 10
# [dataset_size, STRIKE_PRICE] = initiateDatabase(ROLLLING_WINDOW_SIZE) # load size and strike price from the dataset itself
openOutputFile()
loadBreakOffParams()

STATUS = 'NEUTRAL'
SIGNAL = 'NEUTRAL'
LAST_SIGNAL = 'NEUTRAL'
COUNT_TYPE = 'cumulative' # change it to continous for continous counting of the signal
RESPONSE = 'NEUTRAL'

idx = ROLLLING_WINDOW_SIZE
neg_signal_count = 1
sq_off_count = 0
gamma_scalp = None
all_trades_indexes = []
current_trade_indexes = []
entry_hv = 0
entry_iv = 0
entry_timestamp = ''
total_pnl = 0

for i in range(idx, dataset_size):
    hist_volatility = getHistoricalVolatility(i) * 100 # in percent format
    impl_volatility = getImpliedVolatility(i) * 100 # in percent format

    # parameters 
    S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
    curr_date = getCurrentDate(i)
    T = (getExpiryDate(curr_date) - curr_date).days / 365
    # print("historical volatility {} %, implied volatility {} %".format(hist_volatility, impl_volatility))
    
    if impl_volatility < hist_volatility and abs(impl_volatility - hist_volatility) > IV_HV_DIFF_TOLERENCE: # some difference tolerence
        LAST_SIGNAL = SIGNAL
        SIGNAL = 'LONG'  # long
    elif impl_volatility > hist_volatility and abs(impl_volatility - hist_volatility) > IV_HV_DIFF_TOLERENCE:
        LAST_SIGNAL = SIGNAL
        SIGNAL = 'SHORT'  # short
    else:
        LAST_SIGNAL = SIGNAL
        SIGNAL = 'NEUTRAL'

    if STATUS == 'NEUTRAL' and SIGNAL == STATUS:
        continue
    elif STATUS == 'NEUTRAL' and SIGNAL != STATUS:
        if SIGNAL == LAST_SIGNAL:
            neg_signal_count += 1 # continous count for the initial signal acceptance when status is neutral
        else:
            neg_signal_count = 1 # continous count variable
        if neg_signal_count >= NEG_SIGNAL_TOLERENCE / 2: # change this value for some tolerence in the initial signal acceptance initial signal count is taken as continous count variable
            STATUS = SIGNAL
            writePositionDataToTradeFile(i, STATUS + ' START : NEUTRAL')
            gamma_scalp = GammaScalping('ABC', S, STRIKE_PRICE, T, T, NUM_CALL, NUM_PUT, SZ_CONTRACT, RISK_FREE_RATE, curr_date, STATUS, i, IV_TOLERENCE)
            entry_hv = hist_volatility
            entry_iv = impl_volatility
            entry_timestamp = getTimeStamp(i)
            neg_signal_count = 0
            sq_off_count = 0

    elif SIGNAL == 'NEUTRAL' or STATUS == SIGNAL:
        sq_off_count += 1
        current_trade_indexes.append(i)
        if SIGNAL == 'NEUTRAL' and COUNT_TYPE == 'continous':
            neg_signal_count += 1 # if continous count
        if sq_off_count >= SQUARE_OFF_COUNT:
            sq_off_count = 0
            neg_signal_count = 0 # other option is neg_signal_count = neg_signal_count // 2
        RESPONSE = gamma_scalp.deltaHedge(i)
        if RESPONSE != 'NEUTRAL':
            total_pnl = gamma_scalp.closePosition(i)
            # trade points for graph
            if total_pnl > 0:
                all_trades_indexes.append([current_trade_indexes, 'profit'])
            else:
                all_trades_indexes.append([current_trade_indexes, 'loss'])
            current_trade_indexes = []
            # write data to file for analysis
            writePositionDataToTradeFile(i, STATUS + ' EXIT : RESPONSE ' + RESPONSE)
            writeToSummaryFile(entry_timestamp, getTimeStamp(i), gamma_scalp.g_position, entry_iv, entry_hv, impl_volatility, hist_volatility, total_pnl, RESPONSE)
            STATUS = 'NEUTRAL'
            sq_off_count = 0
            neg_signal_count = 0
    else:
        neg_signal_count += 1
        sq_off_count += 1
        current_trade_indexes.append(i)
        if neg_signal_count >= NEG_SIGNAL_TOLERENCE or sq_off_count >= SQUARE_OFF_COUNT:
            if neg_signal_count >= NEG_SIGNAL_TOLERENCE:
                total_pnl = gamma_scalp.closePosition(i)
                # trade points for graph
                if total_pnl > 0:
                    all_trades_indexes.append([current_trade_indexes, 'profit'])
                else:
                    all_trades_indexes.append([current_trade_indexes, 'loss'])
                current_trade_indexes = []
                # write data to file for analysis
                writePositionDataToTradeFile(i, STATUS + ' EXIT : NEG_SIGNAL')
                writeToSummaryFile(entry_timestamp, getTimeStamp(i), gamma_scalp.g_position, entry_iv, entry_hv, impl_volatility, hist_volatility, total_pnl, 'NEG_SIGNAL')
                STATUS = 'NEUTRAL'
            elif sq_off_count >= SQUARE_OFF_COUNT:
                total_pnl = gamma_scalp.closePosition(i)
                # trade points for graph
                if total_pnl > 0:
                    all_trades_indexes.append([current_trade_indexes, 'profit'])
                else:
                    all_trades_indexes.append([current_trade_indexes, 'loss'])
                current_trade_indexes = []
                # write data to file for analysis
                writePositionDataToTradeFile(i, STATUS + ' EXIT : SQR_OFF')
                writeToSummaryFile(entry_timestamp, getTimeStamp(i), gamma_scalp.g_position, entry_iv, entry_hv, impl_volatility, hist_volatility, total_pnl, 'SQR_OFF')
                STATUS = 'NEUTRAL'    
            sq_off_count = 0
            neg_signal_count = 0

closeOutputFile()
plotTrades(all_trades_indexes)
