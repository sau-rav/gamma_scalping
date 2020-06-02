import datetime
import calendar

def roundToNearestInt(val):
    decimal_part = val - int(val)
    if decimal_part <= 0.5:
        return int(val)
    else:
        return int(val) + 1

def getMonthEnd(query_date):
    last_day = calendar.monthrange(query_date.year, query_date.month)[1]
    return datetime.datetime(query_date.year, query_date.month, last_day).date()

# d = datetime.datetime.now().date()
# print(getMonthEnd(d))