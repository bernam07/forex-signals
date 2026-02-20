import requests
import MetaTrader5 as mt5

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")

def get_account_update_message():
    account_info = mt5.account_info()
    if account_info is None:
        return "Erro: Não foi possível obter informações da conta."

    balance = account_info.balance
    equity = account_info.equity
    profit = account_info.profit
    
    pl_percentage = (profit / balance) * 100 if balance > 0 else 0.0

    msg = (
        f"📊 Update de Conta\n"
        f"Saldo: {balance:.2f}€\n"
        f"Equity: {equity:.2f}€\n"
        f"Lucro Flutuante: {profit:.2f}€\n"
        f"P/L: {pl_percentage:.2f}%\n"
    )
    return msg