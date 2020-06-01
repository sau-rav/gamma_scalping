from gamma import *
from dataHandler import *

initiateDatabase()
# constantly need to look at historical volatility and decide whether to long or short gamma

# gamma_scalp = GammaScalping('ABC', 100, 100, 0.086, 0.086, 1, 1, 0.0015, 'long')
# print("Balance after delta hedge = {}".format(gamma_scalp.balance))

# for i in range(1, 7):
#     gamma_scalp.deltaHedge(i)
#     print("Balance after delta hedge = {}".format(gamma_scalp.balance))
