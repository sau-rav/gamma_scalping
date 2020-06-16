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
    output_file.write("idx,timestamp,action,delta_before,delta_after,delta_change,quantity_traded,PnL_closing_futures,PnL_closing_options,PnL_total\n")

def closeOutputFile():
    global output_file
    output_file.close()

def sellRequest(quantity, idx, delta, total_futures, future_balance, option_cost_init, option_cost_final):
    price = getSpotPriceFuture(idx, 'bid')
    # write the trade to file
    curr_time = getTimeStamp(idx)
    future_balance += price * quantity
    total_futures -= quantity
    profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'ask') * total_futures
    profit_on_closing_options = option_cost_final - option_cost_init
    output_file.write("{},{},sell,{},{},{},{},{},{},{}\n".format(idx, curr_time, delta, delta - quantity, -quantity, quantity, profit_on_closing_futures, profit_on_closing_options, profit_on_closing_futures + profit_on_closing_options)) 
    return price * quantity
    # also output delta before position and after hedging in the -> done 
    # add PnL for futures and avegrage buy, sell price and current price
    # then output it with the treade data

def buyRequest(quantity, idx, delta, total_futures, future_balance, option_cost_init, option_cost_final):
    price = getSpotPriceFuture(idx, 'ask')
    # write the trade to file
    curr_time = getTimeStamp(idx)
    future_balance += price * quantity
    total_futures -= quantity
    profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'bid') * total_futures
    profit_on_closing_options = option_cost_final - option_cost_init
    output_file.write("{},{},buy,{},{},{},{},{},{},{}\n".format(idx, curr_time, delta, delta + quantity, quantity, quantity, profit_on_closing_futures, profit_on_closing_options, profit_on_closing_futures + profit_on_closing_options)) 
    return -price * quantity

def writePositionDataToFile(idx, status):
    curr_time = getTimeStamp(idx)
    output_file.write("{},{},{},,,,,,,\n".format(idx, curr_time, status))

def appendToFile(str):
    output_file.write(str)

# openOutputFile()
# closeOutputFile()