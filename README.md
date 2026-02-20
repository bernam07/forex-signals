# MT5 XGBoost Martingale Trading Bot

An advanced algorithmic trading bot for MetaTrader 5 (MT5) that uses Machine Learning (XGBoost) focused on stationary mathematical data (ATR, Returns) to predict short-term market direction. The bot is fully controllable via Telegram and employs a highly aggressive **Grid Trading with Martingale** strategy, managing dynamic order baskets and adapting to market volatility and broker costs in real-time.

## Key Features

* **Stationary Machine Learning:** XGBClassifier model trained with robust, stationary variables (Percentage Returns, Distance to 50 MA, ATR Pct, and RSI), eliminating model collapse when encountering new absolute price highs or lows.
* **Martingale Execution Engine:** Dynamically calculates the initial lot size based on the account balance and doubles the volume (2.0x multiplier) with each new position opened against the trend, forcing the basket to close at the slightest market pullback.
* **Survival Logic (Target Breakeven):** The profit target grows with each new order, but if the grid reaches a critical depth (4+ positions), the bot abandons profit-seeking and adjusts the target to *Breakeven* (€0.50) strictly to save the account from liquidation.
* **Institutional Protection Filters:**
  * **Daily Goal:** Automatically suspends trading operations once it achieves a 10% daily profit based on the initial capital.
  * **Spread Filter:** Blocks the opening and expansion of the grid if the broker's spread exceeds a safe threshold (protecting the account against the overnight *Rollover* widening).
* **Dynamic Visual Alerts:** The engine plots invisible charts in memory (`matplotlib.use('Agg')`), marking your exact open positions and floating profit, and sends the *screenshot* directly to your Telegram the moment the market moves heavily against you.

## Prerequisites

* Python 3.9 or higher.
* MetaTrader 5 terminal installed and running on Windows.
* MT5 account configured for **Hedging** (mandatory for grid trading).
* **Maximum Leverage (e.g., 1:400 or 1:500)** if operating with small account balances (< €1,000).
* "Algo Trading" permissions enabled (green button) in the MT5 terminal.

## Installation and Setup

1. Clone this repository:
~~~bash
git clone [https://github.com/bernam07/forex-signals.git](https://github.com/bernam07/forex-signals.git)
cd forex-signals
~~~

2. Install the required dependencies:
~~~bash
pip install -r requirements.txt
~~~

3. Create a `.env` file in the root directory with your actual broker account credentials:
~~~env
MT5_LOGIN= YOUR_LOGIN
MT5_PASSWORD= YOUR_PASSWORD
MT5_SERVER= YOUR_SERVER_NAME
TELEGRAM_BOT_TOKEN= YOUR_BOTFATHER_TOKEN
TELEGRAM_CHAT_ID= YOUR_CHAT_ID
~~~

## How to Use?

Start the main script:
~~~bash
python main.py
~~~

The bot will remain in listening mode. Open your bot on Telegram and use the following commands:

* `/start` - Opens the menu to select the currency pair and start the predictive engine.
* `/stop` - Stops the analysis and the opening of new initial positions (already open grids will continue to be managed until the basket closes).
* `/status` - Shows the current execution status, active pair, and the lot size being used.

## Severe Risk Warning

This bot uses a **Martingale** strategy. It does not have a fixed *Stop Loss* per order. Instead, it relies on extreme leverage and free margin to open increasingly larger lots to average the operation's entry price. 

It was specifically optimized for **Cent** accounts or a high-risk approach on small capital (e.g., 1:500 leverage with €50 to €100). Running this system during high-impact macroeconomic news events or in strong, unilateral trending markets without pullbacks will result in free margin depletion and total account liquidation (*Margin Call*). Use exclusively with risk capital ("casino money") and adopt the habit of withdrawing your initial capital as soon as the account doubles.