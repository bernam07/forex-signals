import MetaTrader5 as mt5
import xgboost as xgb
import time
import pandas as pd
from src.data_fetcher import get_historical_data
from src.features import apply_smc_features

def execute_trade(symbol, action, lot_size):
    price = mt5.symbol_info_tick(symbol).ask if action == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": action,
        "price": price,
        "deviation": 20,
        "magic": 1001,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    return mt5.order_send(request)

def close_all_positions(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return
    
    for pos in positions:
        action = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).bid if action == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": action,
            "position": pos.ticket,
            "price": price,
            "deviation": 20,
            "magic": 1001,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        mt5.order_send(request)

def bot_loop(bot_state, model_path, tg_bot, chat_id):
    features = ['Sweep_High', 'Sweep_Low', 'FVG_Bull', 'FVG_Bear', 'Session_NY', 'Trend', 'RSI']
    target_profit = 15.0
    last_trade_time = None

    while True:
        if not bot_state['is_running'] or not bot_state['symbol']:
            time.sleep(2)
            continue
            
        symbol = bot_state['symbol']
        lot_size = bot_state['lot_size']
        
        model = xgb.XGBClassifier()
        model.load_model(model_path)
        
        df = get_historical_data(symbol, mt5.TIMEFRAME_M5, 200)
        df = apply_smc_features(df)
        
        if df.empty:
            time.sleep(5)
            continue
            
        latest_data = df[features].tail(1)
        prediction = model.predict(latest_data)[0]
        current_candle_time = df['time'].iloc[-1]
        current_rsi = latest_data['RSI'].iloc[0]
        
        current_time = pd.Timestamp.now().strftime("%H:%M:%S")
        positions = mt5.positions_get(symbol=symbol)
        num_positions = len(positions) if positions else 0
        
        print(f"[{current_time}] a analisar {symbol} | RSI: {current_rsi:.2f} | Posições: {num_positions}")
        
        if positions:
            total_profit = sum([p.profit for p in positions])
            
            if total_profit >= target_profit:
                close_all_positions(symbol)
                tg_bot.send_message(chat_id, f"✅ Cesto fechado com lucro de {total_profit:.2f}€ em {symbol}!")
                last_trade_time = current_candle_time
                time.sleep(5)
                continue

        if last_trade_time != current_candle_time:
            if prediction == 1:
                execute_trade(symbol, mt5.ORDER_TYPE_BUY, lot_size)
                tg_bot.send_message(chat_id, f"📈 Compra executada em {symbol}.")
                last_trade_time = current_candle_time
            elif prediction == 0:
                execute_trade(symbol, mt5.ORDER_TYPE_SELL, lot_size)
                tg_bot.send_message(chat_id, f"📉 Venda executada em {symbol}.")
                last_trade_time = current_candle_time

        time.sleep(10)