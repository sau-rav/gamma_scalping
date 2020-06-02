import pandas as pd
import configparser
from functions import *
import datetime

data = pd.DataFrame() # trade data + order book data of asset, call(at strike = spot_price), put(at strike = spot_price), futures
# asset_order_data = pd.DataFrame() # order book data to extract spot price for asset
# call_order_data = pd.DataFrame() # call option order book data to extract spot price for call option of asset ##### (at the money strike price data required at every new buy instant)
# put_order_data = pd.DataFrame() # put option order book data to extract spot price for put option of asset
# future_order_data = pd.DataFrame() # future order book data to extract spot price for futures for hedging (expiring at month end)
# using separate files for data may lead to misaligned data

def initiateDatabase():
    # files required for initiating database, extracts name from a config file
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    path1 = config.get('Data Section', 'path1')
    # path2 = config.get('Data Section', 'path2')
    # path3 = config.get('Data Section', 'path3')
    # makes sure historical volatility is precalculated in database
    global data
    data = pd.read_csv(path1)
    return data.shape[0]

def getSpotPrice(idx, type_of_data):
    # returns spot price for the underlying asset from the dataset
    if type_of_data == 'bid':
        return data.loc[idx, 'asset_bid']
    elif type_of_data == 'ask':
        return data.loc[idx, 'asset_ask']
    elif type_of_data == 'avg':
        return (data.loc[idx, 'asset_bid'] + data.loc[idx, 'asset_ask']) / 2

def getOptionPrice(idx, option, type_of_data):
    if option == 'call':
        # extract data from database
        if type_of_data == 'bid':
            return data[idx]['call_bid']
        elif type_of_data == 'ask':
            return data[idx]['call_ask']
        elif type_of_data == 'avg':
            return (data[idx]['call_bid'] + data[idx]['call_ask']) / 2
    if option == 'put':
        # extract data from database
        if type_of_data == 'bid':
            return data[idx]['put_bid']
        elif type_of_data == 'ask':
            return data[idx]['put_ask']
        elif type_of_data == 'avg':
            return (data[idx]['put_bid'] + data[idx]['put_ask']) / 2

def getHistoricalVolatility(idx):
    return data.loc[idx, 'historical_volatility']

def getCurrentDate(idx):
    return datetime.datetime.strptime(data.loc[idx, 'timestamp'], '%Y-%m-%d %H:%M:%S').date()

# print(initiateDatabase())
# print(data.head())
# print("Loaded data..")   
# print(getSpotPrice(1, 'avg')) 
