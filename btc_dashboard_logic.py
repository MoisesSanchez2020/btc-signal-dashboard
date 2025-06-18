# This file will contain core app logic such as indicators and trading logic

import pandas as pd

# RSI Calculation
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# MACD Calculation
def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal, macd - signal

# Trade Logging
def log_trade(trade_log, side, entry_price, exit_price, pnl_pct):
    trade_log.append({
        "Side": side,
        "Entry Price": round(entry_price, 2),
        "Exit Price": round(exit_price, 2),
        "PnL (%)": round(pnl_pct, 2),
        "Time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    })
