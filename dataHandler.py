import pandas as pd
import configparser
import datetime
from functions import *

data = pd.DataFrame() # timestamp, order book data of future, call(at strike = predefined), put(at strike = predefined), historical_volatility, implied_volatility

def initiateDatabase(rolling_wind_size):
    # files required for initiating database, extracts name from a config file
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    path = config.get('Input Data Section', 'data_file_path')

    global data
    data = pd.read_csv(path)
    convertToNumeric()
    calculateAvgFuturePrice()
    # calculateHistoricalVolatility(rolling_wind_size) # for now assumed precalculated
    print(data)
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

def calculateHistoricalVolatility(rolling_wind_size):
    # calculated the historical volatility by rolling window standard deviation on average futures prices
    data['historical_volatility'] = data['future_avg'].rolling(rolling_wind_size).std()

def getIVFromDataset(idx):
    return data.loc[idx, 'implied_volatility']

def getTimeStamp(idx):
    return data.loc[idx, 'timestamp']

# initiateDatabase(0)
# calculateHistoricalVolatility()
# print(data.head())
# print("Loaded data..")   
# print(getSpotPrice(1, 'avg')) 
# print(getSpotPrice(1, 0.069, 'avg'))
# print(data.loc[1, 'call_ask'])
# print(getOptionPremium(1, 'call', 'ask'))

