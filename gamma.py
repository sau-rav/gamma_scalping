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
        self.rate = risk_free_rate # gamma position is pos(long gamma) or neg(short gamma)
        self.g_position = gamma_position # current position in terms of deltas
        self.current_position = 0
        self.delta_tolerence = 20

    def calcDelta(self):
        spot_price = getSpotPrice()
        sigma = getVolatility()

        call_delta = getDelta(spot_price, c_strike, c_expiry, rate, sigma, 'call')
        put_delta = getDelta(spot_price, p_strike, p_expiry, rate, sigma, 'put')
        delta_value = current_position + call_delta * c_contracts * 100 + put_delta * p_contracts * 100
        return delta_value

    def deltaHedge(self):
        delta = calcDelta()
        if delta > 0 + delta_tolerence:
            # initiate sell request
            spot_price = getSpotPrice()
            sell_quantity = delta / spot_price
            delta_change = sellRequest(sell_quantity)
            current_position = delta + delta_change
        elif delta < 0 - delta_tolerence:
            # initiate buy request
            spot_price = getSpotPrice()
            buy_quantity = delta / spot_price
            delta_change = buyRequest(buyRequest)
            current_position = delta + delta_change
        return current_position
    
    def getCurrentPosition(self):
        return current_position


