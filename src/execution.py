import MetaTrader5 as mt5
import xgboost as xgb
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Garante que o gráfico é gerado apenas na memória
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from src.data_fetcher import get_historical_data
from src.features import apply_smc_features

def get_filling_mode(symbol):
    """Detecta automaticamente o modo de preenchimento aceite pela corretora."""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return mt5.ORDER_FILLING_FOK
        
    if symbol_info.filling_mode == 1:
        return mt5.ORDER_FILLING_FOK
    elif symbol_info.filling_mode == 2:
        return mt5.ORDER_FILLING_IOC
    elif symbol_info.filling_mode >= 3:
        return mt5.ORDER_FILLING_IOC
    else:
        return mt5.ORDER_FILLING_RETURN

def check_daily_goal(virtual_balance, target_pct=0.10):
    """Verifica se já atingimos 10% de lucro sobre a banca hoje."""
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    
    # Busca o histórico de trades fechadas hoje
    history_deals = mt5.history_deals_get(start_of_day, now)
    if history_deals is None or len(history_deals) == 0:
        return False, 0.0
        
    daily_profit = sum([d.profit for d in history_deals if d.magic == 1001])
    goal_value = virtual_balance * target_pct
    
    if daily_profit >= goal_value:
        return True, daily_profit
    return False, daily_profit

def execute_trade(symbol, action, lot_size, max_spread_pips=3.0):
    """Executa a ordem apenas se o spread for aceitável."""
    tick = mt5.symbol_info_tick(symbol)
    spread = (tick.ask - tick.bid) / mt5.symbol_info(symbol).point / 10 # Converte para pips
    
    if spread > max_spread_pips:
        print(f"Ordem bloqueada: Spread atual ({spread:.1f}) acima do limite ({max_spread_pips})")
        return False

    price = tick.ask if action == mt5.ORDER_TYPE_BUY else tick.bid
    filling_type = get_filling_mode(symbol)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": action,
        "price": price,
        "deviation": 20,
        "magic": 1001,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }
    
    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Erro na ordem: {result.comment if result else 'Falha total'}")
        return False
        
    return True

def close_position(symbol, ticket, volume, pos_type):
    """Fecha uma posição específica."""
    action = mt5.ORDER_TYPE_SELL if pos_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    tick = mt5.symbol_info_tick(symbol)
    price = tick.bid if action == mt5.ORDER_TYPE_SELL else tick.ask
    filling_type = get_filling_mode(symbol)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": action,
        "position": ticket,
        "price": price,
        "deviation": 20,
        "magic": 1001,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }
    return mt5.order_send(request)

def close_all_positions(symbol):
    """Fecha todas as posições abertas do par."""
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            close_position(symbol, pos.ticket, pos.volume, pos.type)

def send_chart_alert(symbol, df, tg_bot, chat_id, num_positions, positions):
    """Envia gráfico com linhas das ordens e lucro atual."""
    plt.figure(figsize=(10, 5))
    plt.plot(df['time'].tail(60), df['close'].tail(60), color='black', linewidth=1.5)
    
    total_profit = sum([p.profit for p in positions])
    
    for p in positions:
        color = 'green' if p.type == mt5.ORDER_TYPE_BUY else 'red'
        plt.axhline(y=p.price_open, color=color, linestyle='--', alpha=0.6)
        
    plt.title(f"{symbol} - {num_positions} Pos. | Lucro: {total_profit:.2f}€")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    tg_bot.send_photo(chat_id, photo=buf, caption=f"⚠️ Grelha ativa: {num_positions} posições.\nLucro Atual: {total_profit:.2f}€")

def bot_loop(bot_state, model_path, tg_bot, chat_id):
    features = ['Session_NY', 'Returns', 'High_Low_Range', 'Close_Open_Range', 'Dist_MA_50', 'ATR_Pct', 'RSI']
    last_trade_time = None
    virtual_balance = 50.0 # Simulação de banca de 50€
    last_alert_level = 0

    while True:
        if not bot_state['is_running'] or not bot_state['symbol']:
            time.sleep(2)
            continue
            
        current_time = pd.Timestamp.now().strftime("%H:%M:%S")
        
        # 1. Verificação de Conexão
        if not mt5.terminal_info().connected:
            print(f"[{current_time}] Offline. A aguardar...")
            time.sleep(10)
            continue

        # 2. Verificação de Meta Diária (Protege o lucro do dia)
        goal_reached, today_profit = check_daily_goal(virtual_balance)
        if goal_reached:
            print(f"[{current_time}] Meta atingida ({today_profit:.2f}€). A descansar até amanhã.")
            tg_bot.send_message(chat_id, f"💰 Meta Diária Atingida! Lucro: {today_profit:.2f}€. Bot suspenso por segurança.")
            time.sleep(3600) # Dorme por 1 hora antes de verificar novamente
            continue
            
        symbol = bot_state['symbol']
        positions = mt5.positions_get(symbol=symbol)
        num_positions = len(positions) if positions else 0
        
        # 3. Lógica Martingale Dinâmica
        base_lot = 0.01
        current_grid_lot = round(base_lot * (2.0 ** num_positions), 2)
        
        # 4. Lógica de Sobrevivência (Target Breakeven)
        # Se tivermos mais de 4 posições, focamos em sair com lucro mínimo (0.50€) para salvar a conta
        if num_positions >= 4:
            basket_target_profit = 0.50 
        else:
            basket_target_profit = (base_lot * 20.0) + (num_positions * 2.0)

        # 5. Processamento de Sinais
        df = get_historical_data(symbol, mt5.TIMEFRAME_M5, 200)
        if df is None or df.empty:
            time.sleep(5); continue
            
        if num_positions >= 3 and num_positions > last_alert_level:
            send_chart_alert(symbol, df, tg_bot, chat_id, num_positions, positions)
            last_alert_level = num_positions
            
        df = apply_smc_features(df)
        prediction = xgb.XGBClassifier()
        prediction.load_model(model_path)
        pred = prediction.predict(df[features].tail(1))[0]
        current_candle_time = df['time'].iloc[-1]
        
        print(f"[{current_time}] {symbol} | Pos: {num_positions} | Target: {basket_target_profit:.2f}€")
        
        # 6. Gestão do Cesto
        if positions:
            total_profit = sum([p.profit for p in positions])
            if total_profit >= basket_target_profit:
                close_all_positions(symbol)
                tg_bot.send_message(chat_id, f"✅ Cesto liquidado! Lucro: {total_profit:.2f}€")
                last_trade_time = current_candle_time
                time.sleep(5); continue

        # 7. Execução de Novas Ordens (Sinal + Proteção de Vela)
        if last_trade_time != current_candle_time:
            action = mt5.ORDER_TYPE_BUY if pred == 1 else mt5.ORDER_TYPE_SELL
            if execute_trade(symbol, action, current_grid_lot):
                tg_bot.send_message(chat_id, f"🚀 Ordem aberta | Lote: {current_grid_lot} | Nível: {num_positions + 1}")
                last_trade_time = current_candle_time

        time.sleep(10)