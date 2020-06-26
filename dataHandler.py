import pandas as pd
import numpy as np
import configparser
import datetime
import matplotlib.pyplot as plt
from functions import *
from bs import *

data = pd.DataFrame() # timestamp, order book data of future, call(at strike = predefined), put(at strike = predefined), historical_volatility, implied_volatility
# col names :- 
# index,time,timestamp,call_ask_iv,call_bid_iv,put_ask_iv,put_bid_iv,call_ask,call_bid,put_ask,put_bid,call_vega,put_vega,call_delta,put_delta,future_avg,future_ask,future_bid

def initiateDatabase(rolling_wind_size, STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE):
    # files required for initiating database, all config related data present in config.txt
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    path = config.get('Input Data Section', 'path5')

    global data
    data = pd.read_csv(path)
    convertToNumeric()
    # calculateAvgFuturePrice() # if future avg not calculated
    calculateImpliedVolatility(data.shape[0], STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE)
    calculateHistoricalVolatility(rolling_wind_size, data.shape[0]) # for now assumed precalculated
    plotHV_IV()
    return data.shape[0]

def convertToNumeric():
    # converts string data in all columns to float
    cols = data.columns.drop('timestamp')
    data[cols] = data[cols].apply(pd.to_numeric, errors = 'coerce')

def calculateAvgFuturePrice():
    # adds col for futures average price 
    data['future_avg'] = data[['future_bid', 'future_ask']].mean(axis = 1)

def getSpotPrice(idx, rate, type_of_data):
    # returns spot price for the underlying asset from the data available for future price by discounting
    if type_of_data == 'bid':
        return discountByRate(data.loc[idx, 'future_bid'], rate, getCurrentDate(idx))
    elif type_of_data == 'ask':
        return discountByRate(data.loc[idx, 'future_bid'], rate, getCurrentDate(idx))
    elif type_of_data == 'avg':
        return discountByRate(data.loc[idx, 'future_avg'], rate, getCurrentDate(idx))

def getSpotPriceFuture(idx, type_of_data):
    # return future price data from the dataset
    if type_of_data == 'bid':
        return data.loc[idx, 'future_bid']
    elif type_of_data == 'ask':
        return data.loc[idx, 'future_ask']
    elif type_of_data == 'avg':
        return data.loc[idx, 'future_avg']

def getOptionPremium(idx, option, type_of_data):
    # returns the option prices (bid, ask, avg) from the dataset
    if option == 'call':
        if type_of_data == 'bid':
            return data.loc[idx, 'call_bid']
        elif type_of_data == 'ask':
            return data.loc[idx, 'call_ask']
        elif type_of_data == 'avg':
            return (data.loc[idx, 'call_bid'] + data.loc[idx, 'call_ask']) / 2
    if option == 'put':
        if type_of_data == 'bid':
            return data.loc[idx, 'put_bid']
        elif type_of_data == 'ask':
            return data.loc[idx, 'put_ask']
        elif type_of_data == 'avg':
            return (data.loc[idx, 'put_bid'] + data.loc[idx, 'put_ask']) / 2

def getHistoricalVolatility(idx):
    # returns the historical volatility at any index from the dataset
    return data.loc[idx, 'historical_volatility']

def getCurrentDate(idx):
    # return current date for timestamp of any index
    date = data.loc[idx, 'timestamp'].split(' ')[0]
    year, month, day = date.split('/')
    return datetime.datetime(int(year), int(month), int(day)).date()

def getCurrentTime(idx):
    date = data.loc[idx, 'timestamp'].split(' ')[0]
    time = data.loc[idx, 'timestamp'].split(' ')[1]
    year, month, day = date.split('/')
    hour, min, sec = time.split(':')
    sec = sec.split('.')[0]
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(min), int(sec)).time()

def calculateHistoricalVolatility(rolling_wind_size, dataset_size):
    # calculated the historical volatility by rolling window standard deviation on ln(daily_returns)
    # daily_return = [0] * dataset_size
    # for i in range (0, dataset_size - 1):
    #     daily_return[i] = np.log(data.loc[i, 'future_avg'] / data.loc[i+1, 'future_avg'])
        # daily_return[i] = (data.loc[i, 'future_avg'] / data.loc[i+1, 'future_avg']) - 1
    
    # data['daily_return'] = daily_return
    # data['historical_volatility'] = data['daily_return'].rolling(rolling_wind_size).std() * np.sqrt(252 / (rolling_wind_size / (12 * 24 * 60))) # converted to annual

    # data['historical_volatility'] = (data['implied_volatility']).rolling(rolling_wind_size).median() 
    data['historical_volatility'] = (data['implied_volatility']).ewm(span = 500).mean()

def calculateImpliedVolatility(dataset_size, STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE):
    iv_values = []
    for i in range(dataset_size):
        S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
        curr_date = getCurrentDate(i)
        curr_time = getCurrentTime(i)
        T = ((getExpiryDate(curr_date) - curr_date).days - convertMinutesToDays(curr_time)) / 365
        C = getOptionPremium(i, 'call', 'avg')
        iv = getImpliedVolatilityBS(C, S, STRIKE_PRICE, T, RISK_FREE_RATE, i, IV_TOLERENCE)
        iv_values.append(iv)
    data['implied_volatility'] = iv_values
    # data['implied_volatility'] = data['implied_volatility'].ewm(span = 20).mean()

def getImpliedVolatility(idx):
    # val = data.loc[idx, 'call_bid_iv'] + data.loc[idx, 'call_ask_iv'] + data.loc[idx, 'put_bid_iv'] + data.loc[idx, 'put_ask_iv']
    # val /= 4
    val = data.loc[idx, 'implied_volatility']
    return val

def getTimeStamp(idx):
    return data.loc[idx, 'timestamp']

def getDelta(idx, option):
    if option == 'call':
        result = data.loc[idx, 'call_delta']
    if option == 'put':
        result = data.loc[idx, 'put_delta']
    return result

def plotHV_IV():
    # plt.plot(data['index'], (data['call_bid_iv'] + data['call_ask_iv'] + data['put_bid_iv'] + data['put_ask_iv']) / 4, label = 'iv_data')
    plt.plot(data['index'], data['implied_volatility'], label = 'iv_calc')
    plt.plot(data['index'], data['historical_volatility'], label = 'hv_calc')
    plt.savefig('iv_vs_hv.png')
    plt.show()