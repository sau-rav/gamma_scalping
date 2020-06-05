import numpy as np
from bs import *
from dataHandler import *
from requestHandler import *
from functions import *
import datetime

class GammaScalping:
    def __init__(self, symbol, call_strike, put_strike, call_expiry, put_expiry, num_contracts_call, num_contracts_put, risk_free_rate, curr_date, gamma_position, init_idx):
        self.s_symbol = symbol
        self.c_strike = call_strike # strike price of put option
        self.p_strike = put_strike # strike price of call option
        self.c_expiry = call_expiry # time till expiration of call expressed in years
        self.p_expiry = put_expiry # time till expiration of put expressed in years
        self.c_expiry_date = getMonthEnd(curr_date)
        self.p_expiry_date = getMonthEnd(curr_date)
        self.c_contracts = num_contracts_call  # a contract contains of 100 options (of the type call or put)
        self.p_contracts = num_contracts_put
        self.rate = risk_free_rate 
        self.g_position = gamma_position # gamma position is long(long gamma) or short(short gamma)
        self.total_futures = 0 # total number of futures in hand, will hedge using futures
        self.balance = self.getInitialBalance(init_idx) 
        self.delta_tolerence = 0.5
        self.deltaHedge(init_idx)

    def getInitialBalance(self, init_idx):
        # spot_price = getSpotPrice(0, 'avg')
        # sigma = getImpliedVolatility(spot_price, self.c_strike, self.c_expiry, self.rate, 0)
        call_premium = getOptionPremium(init_idx, 'call', 'ask')
        put_premium = getOptionPremium(init_idx, 'put', 'ask')
        
        bal = 0
        if self.g_position == 'long':
            bal = -(call_premium * self.c_contracts * 100 + put_premium * self.p_contracts * 100)
        elif self.g_position == 'short':
            bal = (call_premium * self.c_contracts * 100 + put_premium * self.p_contracts * 100)
        print("Balance after spending premium : {}\n".format(bal))
        return bal

    def calcDelta(self, idx):
        spot_price = getSpotPrice(idx, self.rate, 'avg') # mid price of bid ask
        sigma = getImpliedVolatility(spot_price, self.c_strike, self.c_expiry, self.rate, idx) 

        call_delta = getDelta(spot_price, self.c_strike, self.c_expiry, self.rate, sigma, 'call') # need to change c_expiry accoring to idx
        assert call_delta <= 1 and call_delta >= 0, 'Call delta not in range error'
        print("call delta : {}".format(call_delta)) # apply checks -> applied

        put_delta = getDelta(spot_price, self.p_strike, self.p_expiry, self.rate, sigma, 'put') # need to change the p_expiry according to idx (timestamp)
        assert put_delta <= 0 and put_delta >= -1, 'Put delta not in range error'
        print("put delta : {}".format(put_delta))
        
        if self.g_position == 'long':
            delta_value = self.total_futures + call_delta * self.c_contracts * 100 + put_delta * self.p_contracts * 100
        elif self.g_position == 'short':
            delta_value = self.total_futures - call_delta * self.c_contracts * 100 - put_delta * self.p_contracts * 100
        return delta_value

    def deltaHedge(self, idx):
        # updating c_expiry, p_expiry according to currdate
        curr_date = getCurrentDate(idx)
        self.c_expiry = (self.c_expiry_date - curr_date).days / 365
        self.p_expiry = (self.p_expiry_date - curr_date).days / 365

        print("-----------Performing hedging.. at idx = {} timestamp : {} ------------".format(idx, getTimeStamp(idx)))
        delta = self.calcDelta(idx)
        print("Total delta before hedge : {}".format(delta))
        
        if delta > 0 + self.delta_tolerence: ## look at round off while hedging -> handled
            # initiate sell request
            sell_quantity = roundToNearestInt(delta)
            balance_change = sellRequest(sell_quantity, idx)
            self.balance += balance_change
            self.total_futures -= sell_quantity
            delta -= sell_quantity
        elif delta < 0 - self.delta_tolerence:
            # initiate buy request
            buy_quantity = roundToNearestInt(-delta)
            balance_change = buyRequest(buy_quantity, idx)
            self.balance += balance_change
            self.total_futures += buy_quantity
            delta += buy_quantity
                    
        # print("Final delta : {}".format(self.calcDelta(idx)))
        print("Total delta after hedge : {}".format(delta))
        return self.balance
    
    


