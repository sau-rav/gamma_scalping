from dataHandler import *
import configparser
import datetime

path = ""
output_file = None

def openOutputFile():
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    global path, output_file
    path = config.get('Output Data Section', 'output_file_path')
    erase_contents_file = open(path, 'w+') # clear previous data
    erase_contents_file.truncate(0)
    erase_contents_file.close()

    output_file = open(path, "a+") # append mode 
    output_file.write("idx,timestamp,action,quantity,price\n")

def closeOutputFile():
    global output_file
    output_file.close()

def sellRequest(quantity, idx):
    price = getSpotPriceFuture(idx, 'avg')
    # write the trade to file
    curr_time = getTimeStamp(idx)
    output_file.write("{},{},sell,{},{}\n".format(idx, curr_time, quantity, price)) 
    return price * quantity

def buyRequest(quantity, idx):
    price = getSpotPriceFuture(idx, 'avg')
    # write the trade to file
    curr_time = getTimeStamp(idx)
    output_file.write("{},{},buy,{},{}\n".format(idx, curr_time, quantity, price)) 
    return -price * quantity

def appendToFile(str):
    output_file.write(str)

# openOutputFile()
# closeOutputFile()
# str = "2020/01/01 15:29:55.229"
# date = str.split(' ')[0]
# year, month, date = date.split('/')
# d1 = datetime.datetime(int(year), int(month), int(date)).date()
# d2 = getMonthEnd(d1)
# print(type(d1))
# print(d1)
# print(type(d2))
# print(d2)
# print((d2 - d1).days)
# print(testFunction())