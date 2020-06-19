from dataHandler import *
import configparser
import datetime

path = ""
output_file = None
break_off_profit = 0
break_off_loss = 0

def loadBreakOffParams():
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    global break_off_loss, break_off_profit
    break_off_profit = int(config.get('Variable Section', 'break_off_profit'))
    break_off_loss = int(config.get('Variable Section', 'break_off_loss'))

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

def sellRequest(quantity, idx, delta, total_futures, future_balance, option_cost_init, option_cost_final, profit_count, loss_count):
    price = getSpotPriceFuture(idx, 'bid')
    # write the trade to file
    curr_time = getTimeStamp(idx)
    future_balance += price * quantity
    total_futures -= quantity
    profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'ask') * total_futures
    profit_on_closing_options = option_cost_final - option_cost_init
    total_pnl = profit_on_closing_futures + profit_on_closing_options
    if total_pnl > 0:
        profit_count += 1
    elif total_pnl < 0:
        loss_count += 1
    response = 'NEUTRAL'
    if total_pnl >= break_off_profit:
        response = 'EXIT_P'
    elif loss_count / (loss_count + profit_count) > 0.90 and abs(total_pnl) > break_off_loss // 2 and abs(total_pnl) < break_off_loss and total_pnl < 0:
        response = 'EXIT_L'
    output_file.write("{},{},sell,{},{},{},{},{},{},{}\n".format(idx, curr_time, delta, delta - quantity, -quantity, quantity, profit_on_closing_futures, profit_on_closing_options, profit_on_closing_futures + profit_on_closing_options)) 
    return [price * quantity, response, profit_count, loss_count]
    # also output delta before position and after hedging in the -> done 
    # add PnL for futures and avegrage buy, sell price and current price
    # then output it with the treade data

def buyRequest(quantity, idx, delta, total_futures, future_balance, option_cost_init, option_cost_final, profit_count, loss_count):
    price = getSpotPriceFuture(idx, 'ask')
    # write the trade to file
    curr_time = getTimeStamp(idx)
    future_balance += price * quantity
    total_futures -= quantity
    profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'bid') * total_futures
    profit_on_closing_options = option_cost_final - option_cost_init
    total_pnl = profit_on_closing_futures + profit_on_closing_options
    if total_pnl > 0:
        profit_count += 1
    elif total_pnl < 0:
        loss_count += 1
    response = 'NEUTRAL'
    if total_pnl >= break_off_profit:
        response = 'EXIT_P'
    elif loss_count / (loss_count + profit_count) > 0.90 and abs(total_pnl) > break_off_loss // 2 and abs(total_pnl) < break_off_loss and total_pnl < 0:
        response = 'EXIT_L'
    output_file.write("{},{},buy,{},{},{},{},{},{},{}\n".format(idx, curr_time, delta, delta + quantity, quantity, quantity, profit_on_closing_futures, profit_on_closing_options, profit_on_closing_futures + profit_on_closing_options)) 
    return [-price * quantity, response, profit_count, loss_count]

def writePositionDataToFile(idx, status):
    curr_time = getTimeStamp(idx)
    output_file.write("{},{},{},,,,,,,\n".format(idx, curr_time, status))

def appendToFile(str):
    output_file.write(str)

# openOutputFile()
# closeOutputFile()