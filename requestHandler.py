from dataHandler import *
import configparser
import datetime

path = ""
output_file = None
summary_file = None
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
    global path, output_file, summary_file
    path = config.get('Output Data Section', 'output_file_path')
    erase_contents_file = open(path, 'w+') # clear previous data
    erase_contents_file.truncate(0)
    erase_contents_file.close()
    output_file = open(path, 'a+') # append mode 
    output_file.write("idx,timestamp,action,delta_before,delta_after,delta_change,quantity_traded,PnL_closing_futures,PnL_closing_options,PnL_total\n")

    path = config.get('Output Data Section', 'summary_file_path')
    erase_contents_file = open(path, 'w+') # clear previous data
    erase_contents_file.truncate(0)
    erase_contents_file.close()
    summary_file = open(path, 'a+') # append mode
    summary_file.write("start_timestamp,end_timestamp,position_taken,entry_iv,entry_hv,entry_diff,exit_iv,exit_hv,exit_diff,total_pnl,exit_criteria,profit/loss\n")

def closeOutputFile():
    global output_file, summary_file
    output_file.close()
    summary_file.close()

def sellRequest(action, quantity, idx, delta, total_futures, future_balance, option_cost_init, option_cost_final, profit_count, loss_count):
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
    if action == 'HEDGE':
        return [price * quantity, response, profit_count, loss_count]
    else:
        return total_pnl

def buyRequest(action, quantity, idx, delta, total_futures, future_balance, option_cost_init, option_cost_final, profit_count, loss_count):
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
    if action == 'HEDGE':
        return [-price * quantity, response, profit_count, loss_count]
    else:
        return total_pnl

def writePositionDataToTradeFile(idx, status):
    curr_time = getTimeStamp(idx)
    output_file.write("{},{},{},,,,,,,\n".format(idx, curr_time, status))

def writeToSummaryFile(start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, exit_iv, exit_hv, total_pnl, exit_criteria):
    if total_pnl > 0:
        summary_file.write("{},{},{},{},{},{},{},{},{},{},{},profit\n".format(start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, abs(entry_hv - entry_iv), exit_iv, exit_hv, abs(exit_hv - exit_iv), total_pnl, exit_criteria))
    else:
        summary_file.write("{},{},{},{},{},{},{},{},{},{},{},loss\n".format(start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, abs(entry_hv - entry_iv), exit_iv, exit_hv, abs(exit_hv - exit_iv), total_pnl, exit_criteria))

# def appendToFile(str):
#     output_file.write(str)

# openOutputFile()
# closeOutputFile()