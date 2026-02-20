import pandas as pd
import numpy as np

def apply_smc_features(df):
    df['Hour'] = df['time'].dt.hour
    df['Session_NY'] = np.where((df['Hour'] >= 8) & (df['Hour'] <= 11), 1, 0)
    
    df['4H_High'] = df['high'].rolling(window=48).max().shift(1)
    df['4H_Low'] = df['low'].rolling(window=48).min().shift(1)
    
    df['Sweep_High'] = np.where((df['high'] > df['4H_High']) & (df['close'] < df['4H_High']), 1, 0)
    df['Sweep_Low'] = np.where((df['low'] < df['4H_Low']) & (df['close'] > df['4H_Low']), 1, 0)
    
    df['FVG_Bull'] = np.where(df['low'] > df['high'].shift(2), 1, 0)
    df['FVG_Bear'] = np.where(df['high'] < df['low'].shift(2), 1, 0)
    
    df['Trend'] = np.where(df['close'] > df['close'].rolling(50).mean(), 1, -1)
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Target'] = np.where(df['close'].shift(-6) > df['close'], 1, 0)
    
    return df.dropna()