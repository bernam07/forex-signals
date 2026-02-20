import pandas as pd
import numpy as np

def apply_smc_features(df):
    df['Hour'] = df['time'].dt.hour
    df['Session_NY'] = np.where((df['Hour'] >= 8) & (df['Hour'] <= 11), 1, 0)
    
    df['Returns'] = df['close'].pct_change()
    
    df['High_Low_Range'] = (df['high'] - df['low']) / df['low']
    df['Close_Open_Range'] = (df['close'] - df['open']) / df['open']
    
    df['MA_50'] = df['close'].rolling(window=50).mean()
    df['Dist_MA_50'] = (df['close'] - df['MA_50']) / df['MA_50']
    
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR_14'] = true_range.rolling(14).mean()
    
    df['ATR_Pct'] = df['ATR_14'] / df['close']
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Target'] = np.where(df['close'].shift(-6) > df['close'], 1, 0)
    
    return df.dropna()