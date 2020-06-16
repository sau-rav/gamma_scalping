import datetime
import calendar
import numpy as np

def roundToNearestInt(val):
    decimal_part = val - int(val)
    if decimal_part <= 0.5:
        return int(val)
    else:
        return int(val) + 1

def getExpiryDate(query_date):
    return datetime.datetime(2020, 5, 29).date() # later do it according to the expiry date chart
    last_day = calendar.monthrange(query_date.year, query_date.month)[1]
    return datetime.datetime(query_date.year, query_date.month, last_day).date()

def discountByRate(future_price, rate, curr_date):
    time = (getExpiryDate(curr_date) - curr_date).days / 365 # number of years
    return future_price * np.exp(-rate * time)

# d = datetime.datetime.now().date()
# print(getExpiryDate(d))
# print(discountByRate(100, 0.069, datetime.datetime.now().date()))
