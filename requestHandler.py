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
    output_file = open(path, "a") # append mode 

def closeOutputFile():
    global output_file
    output_file.close()

def sellRequest(quantity, idx):
    price = getSpotPriceFuture(idx, 'bid')
    # write the trade to file
    output_file.write("") 
    return price * quantity

def buyRequest(quantity, idx):
    price = getSpotPriceFuture(idx, 'ask')
    # write the trade to file
    output_file.write("") 
    return -price * quantity

def appendToFile(str):
    output_file.write(str)

# openOutputFile()
# closeOutputFile()
str = "2020/01/01 15:29:55.229"
date = str.split(' ')[0]
year, month, date = date.split('/')
d1 = datetime.datetime(int(year), int(month), int(date)).date()
d2 = getMonthEnd(d1)
print(type(d1))
print(d1)
print(type(d2))
print(d2)
print((d2 - d1).days)