import pandas as pd
import numpy as np
import configparser
import datetime
from functions import *
from requestHandler import *
from bs import *

data = pd.DataFrame() # timestamp, order book data of future, call(at strike = predefined), put(at strike = predefined), historical_volatility, implied_volatility
# col names : index,time,timestamp,call_ask_iv,call_bid_iv,put_ask_iv,put_bid_iv,call_ask,call_bid,put_ask,put_bid,call_vega,put_vega,call_delta,put_delta,future_avg,future_ask,future_bid

def initiateDatabase(rolling_wind_size):
    # files required for initiating database, extracts name from a config file
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    path = config.get('Input Data Section', 'data_file_path')

    global data
    data = pd.read_csv(path)
    convertToNumeric()
    # calculateAvgFuturePrice()
    calculateHistoricalVolatility(rolling_wind_size, data.shape[0]) # for now assumed precalculated
    print(data.tail())
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

def calculateHistoricalVolatility(rolling_wind_size, dataset_size):
    # calculated the historical volatility by rolling window standard deviation on average futures prices
    daily_return = [0] * dataset_size
    for i in range (0, dataset_size - 1):
        # daily_return[i] = np.log(data.loc[i+1, 'future_avg'] / data.loc[i, 'future_avg'])
        daily_return[i] = (data.loc[i+1, 'future_avg'] / data.loc[i, 'future_avg']) - 1
    
    data['daily_return'] = daily_return
    data['historical_volatility'] = data['daily_return'].rolling(rolling_wind_size).std()
    # data['historical_volatility'] = data['future_avg'].rolling(rolling_wind_size).std()

def getImpliedVolatility(idx):
    val = data.loc[idx, 'call_bid_iv'] + data.loc[idx, 'call_ask_iv'] # + data.loc[idx, 'put_bid_iv'] + data.loc[idx, 'put_ask_iv']
    val /= 2
    return val

def getTimeStamp(idx):
    return data.loc[idx, 'timestamp']

def getDelta(idx, option):
    if option == 'call':
        result = data.loc[idx, 'call_delta']
    if option == 'put':
        result = data.loc[idx, 'put_delta']
    return result

# initiateDatabase(100)
# # calculateHistoricalVolatility()
# print(data.tail())
# print("Loaded data..")   
# print(getSpotPrice(1, 'avg')) 
# print(getSpotPrice(1, 0.069, 'avg'))
# print(data.loc[1, 'call_ask'])
# print(getOptionPremium(1, 'call', 'ask'))
# idx = 1
# S = getSpotPrice(idx, 0.069, 'avg')
# K = 9300
# curr_date = getCurrentDate(idx)
# T = (getMonthEnd(curr_date) - curr_date).days / 365
# r = 0.069
# impl_volatility1 = getImpliedVolatility(S, K, T, r, 1, 0.1)
# print(impl_volatility1)
# print(getImpliedVolatility(idx))

