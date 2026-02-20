import os
import telebot
from telebot import types
import threading
import MetaTrader5 as mt5
from dotenv import load_dotenv
from src.data_fetcher import initialize_mt5, get_historical_data
from src.features import apply_smc_features
from src.model import train_and_save_model
from src.execution import bot_loop

load_dotenv()

def main():
    my_login = int(os.getenv("MT5_LOGIN"))
    my_password = os.getenv("MT5_PASSWORD")
    my_server = os.getenv("MT5_SERVER")
    
    tg_token = os.getenv("TG_TOKEN")
    allowed_chat_id = int(os.getenv("TG_CHAT_ID"))
    
    initialize_mt5(my_login, my_password, my_server)
    
    bot = telebot.TeleBot(tg_token)
    
    bot_state = {
        'is_running': False,
        'symbol': None,
        'lot_size': 0.05
    }

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.id == allowed_chat_id:
            bot_state['is_running'] = False
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('EURUSD', callback_data='EURUSD')
            btn2 = types.InlineKeyboardButton('USDJPY', callback_data='USDJPY')
            btn3 = types.InlineKeyboardButton('GBPUSD', callback_data='GBPUSD')
            markup.row(btn1, btn2, btn3)
            bot.reply_to(message, "Escolhe o par para iniciar o bot:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def handle_query(call):
        if call.message.chat.id == allowed_chat_id:
            new_symbol = call.data
            bot_state['symbol'] = new_symbol
            bot.answer_callback_query(call.id, f"A preparar {new_symbol}...")
            bot.send_message(call.message.chat.id, f"A treinar modelo para {new_symbol}... Aguarda.")
            
            try:
                df_raw_new = get_historical_data(new_symbol, mt5.TIMEFRAME_M5, 50000)
                df_processed_new = apply_smc_features(df_raw_new)
                train_and_save_model(df_processed_new, "saved_xgboost_model.json")
                
                bot_state['is_running'] = True
                bot.send_message(call.message.chat.id, f"✅ Modelo treinado! Bot INICIADO em {new_symbol}.")
            except Exception as e:
                bot.send_message(call.message.chat.id, f"Erro ao processar: {str(e)}")

    @bot.message_handler(commands=['stop'])
    def send_stop(message):
        if message.chat.id == allowed_chat_id:
            bot_state['is_running'] = False
            bot.reply_to(message, "🛑 Bot PARADO.")

    @bot.message_handler(commands=['status'])
    def send_status(message):
        if message.chat.id == allowed_chat_id:
            estado = "A CORRER" if bot_state['is_running'] else "PARADO"
            par = bot_state['symbol'] if bot_state['symbol'] else "Nenhum"
            bot.reply_to(message, f"📊 Estado atual:\nExecução: {estado}\nPar: {par}\nLote: {bot_state['lot_size']}")

    bot_thread = threading.Thread(
        target=bot_loop, 
        args=(bot_state, "saved_xgboost_model.json", bot, allowed_chat_id),
        daemon=True
    )
    bot_thread.start()
    
    print("Telegram bot online! Vai ao Telegram e envia /start para começar.")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()