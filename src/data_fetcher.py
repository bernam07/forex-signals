import MetaTrader5 as mt5
import pandas as pd

def initialize_mt5(account_login, account_password, server_name):
    if not mt5.initialize(login=account_login, password=account_password, server=server_name):
        print(mt5.last_error())
        quit()

def get_historical_data(symbol, timeframe, num_bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df