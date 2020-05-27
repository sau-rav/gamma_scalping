import numpy as np
from bs import *
from data import *
from request import *

class GammaScalping:
    def __init__(self, symbol, call_strike, put_strike, call_expiry, put_expiry, num_contracts_call, num_contracts_put, risk_free_rate, gamma_position):
        self.s_symbol = symbol
        self.c_strike = call_strike # strike price of put option
        self.p_strike = put_strike # strike price of call option
        self.c_expiry = call_expiry # time till expiration of call expressed in years
        self.p_expiry = put_expiry # time till expiration of put expressed in years
        self.c_contracts = num_contracts_call  # a contract contains of 100 options (of the type call or put)
        self.p_contracts = num_contracts_put
        self.rate = risk_free_rate 
        self.g_position = gamma_position # gamma position is long(long gamma) or short(short gamma)
        self.delta_tolerence = 0
        self.total_stocks = 0 # total number of stocks in hand
        self.balance = self.getInitialBalance() 
        self.deltaHedge(0)

    def getInitialBalance(self):
        spot_price = getSpotPrice(0)
        sigma = getVolatility()
        call_premium = getOptionPrice(spot_price, self.c_strike, self.c_expiry, self.rate, sigma, 'call')
        put_premium = getOptionPrice(spot_price, self.p_strike, self.p_expiry, self.rate, sigma, 'put')
        bal = -(call_premium * self.c_contracts * 100 + put_premium * self.p_contracts * 100)
        print("Balance after spending premium : {}".format(bal))
        return bal

    def calcDelta(self, idx):
        spot_price = getSpotPrice(idx)
        sigma = getVolatility()

        call_delta = getDelta(spot_price, self.c_strike, self.c_expiry - idx / 365, self.rate, sigma, 'call')
        print("call delta : {}".format(call_delta))
        put_delta = getDelta(spot_price, self.p_strike, self.p_expiry - idx / 365, self.rate, sigma, 'put')
        print("put delta : {}".format(put_delta))
        delta_value = self.total_stocks + call_delta * self.c_contracts * 100 + put_delta * self.p_contracts * 100
        return delta_value

    def deltaHedge(self, idx):
        print("-----------Performing hedging.. at t = {}------------".format(idx))
        delta = self.calcDelta(idx)
        print("Total delta : {}".format(delta))
        if delta > 0 + self.delta_tolerence:
            # initiate sell request
            spot_price = getSpotPrice(idx)
            sell_quantity = delta
            balance_change = sellRequest(sell_quantity, idx)
            self.balance += balance_change
            self.total_stocks -= sell_quantity
        elif delta < 0 - self.delta_tolerence:
            # initiate buy request
            spot_price = getSpotPrice(idx)
            buy_quantity = -delta
            balance_change = buyRequest(buy_quantity, idx)
            self.balance += balance_change
            self.total_stocks += buy_quantity
        # print("Final delta : {}".format(self.calcDelta(idx)))
        return self.balance
    
    


