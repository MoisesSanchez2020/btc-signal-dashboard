import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import streamlit.components.v1 as components
import time

# Page config
st.set_page_config(page_title="Bitcoin Signal Dashboard", layout="wide")
st.title("📈 Bitcoin Signal Dashboard")
st.subheader("Real-Time BTC Buy/Sell Signals (via CryptoCompare)")

# Sidebar inputs
st.sidebar.header("Settings")
short_window = st.sidebar.number_input("Short Window", min_value=2, value=5)
long_window = st.sidebar.number_input("Long Window", min_value=3, value=15)
refresh_rate = st.sidebar.number_input("Refresh Rate (sec)", min_value=5, value=10)
enable_bot = st.sidebar.checkbox("🤖 Enable Auto-Bot Mode")

st.sidebar.markdown("### Risk Management")
stop_loss_pct = st.sidebar.number_input("Stop Loss (%)", min_value=0.1, value=1.0)
take_profit_pct = st.sidebar.number_input("Take Profit (%)", min_value=0.1, value=2.0)

# Session state setup
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "position" not in st.session_state:
    st.session_state.position = None
if "last_bot_action" not in st.session_state:
    st.session_state.last_bot_action = None
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

price_data = st.session_state.price_data

# Fetch BTC price
def get_btc_price():
    url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data["USD"])
    except Exception as e:
        st.warning(f"CryptoCompare API Error: {e}")
        return None

# RSI Calculation
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD Calculation
def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

# Trade logging
def log_trade(side, entry_price, exit_price, pnl_pct):
    st.session_state.trade_log.append({
        "Side": side,
        "Entry Price": round(entry_price, 2),
        "Exit Price": round(exit_price, 2),
        "PnL (%)": round(pnl_pct, 2),
        "Time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Get live price
btc_price = get_btc_price()
st.write("DEBUG - BTC Price:", btc_price)

if btc_price:
    price_data.append({"time": pd.Timestamp.now(), "price": btc_price})
    st.write("DEBUG - Price Data Length:", len(price_data))

    if len(price_data) >= long_window:
        df = pd.DataFrame(price_data[-long_window:])
        prices = df["price"]
        short_ma = prices.rolling(short_window).mean()
        long_ma = prices.rolling(long_window).mean()

        # Determine signal
        signal = "⚖️ HOLD"
        if short_ma.iloc[-1] > long_ma.iloc[-1]:
            signal = "📈 BUY"
        elif short_ma.iloc[-1] < long_ma.iloc[-1]:
            signal = "📉 SELL"

        # Sound alert
        if signal != st.session_state.last_signal:
            if signal in ["📈 BUY", "📉 SELL"]:
                sound_alert = """
                <audio autoplay>
                    <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
                </audio>
                """
                components.html(sound_alert)
            st.session_state.last_signal = signal

        # ✅ FIXED Auto-Bot Mode
        already_in_trade = st.session_state.position is not None
        side = "BUY" if signal == "📈 BUY" else "SELL"

        if enable_bot and signal in ["📈 BUY", "📉 SELL"]:
            if not already_in_trade or (st.session_state.position and st.session_state.position["side"] != side):
                st.session_state.position = {
                    "side": side,
                    "entry_price": btc_price,
                    "time": pd.Timestamp.now()
                }
                st.session_state.last_bot_action = f"{side} at ${btc_price:,.2f}"

        st.metric("BTC Price (USD)", f"${btc_price:,.2f}")
        st.markdown(f"### Signal: {signal}")

        # Price Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=prices, mode='lines+markers', name='BTC Price'))
        fig.add_trace(go.Scatter(x=df["time"], y=short_ma, mode='lines', name='Short MA'))
        fig.add_trace(go.Scatter(x=df["time"], y=long_ma, mode='lines', name='Long MA'))
        fig.update_layout(
            title="BTC Price with Moving Averages",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

        # RSI
        rsi = calculate_rsi(prices, window=14)
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df["time"], y=rsi, mode='lines', name='RSI'))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(
            title="RSI (14-period)",
            xaxis_title="Time",
            yaxis_title="RSI Value",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

        # MACD
        macd, signal_line, hist = calculate_macd(prices)
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df["time"], y=macd, mode='lines', name='MACD'))
        fig_macd.add_trace(go.Scatter(x=df["time"], y=signal_line, mode='lines', name='Signal Line'))
        fig_macd.add_trace(go.Bar(x=df["time"], y=hist, name='Histogram'))
        fig_macd.update_layout(
            title="MACD (12-26-9)",
            xaxis_title="Time",
            yaxis_title="MACD Value",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig_macd, use_container_width=True)

        # Simulated Trading
        st.markdown("---")
        st.subheader("🧪 Simulated Scalping Mode")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🟢 BUY", use_container_width=True):
                st.session_state.position = {
                    "side": "BUY",
                    "entry_price": btc_price,
                    "time": pd.Timestamp.now()
                }
        with col2:
            if st.button("🔴 SELL", use_container_width=True):
                st.session_state.position = {
                    "side": "SELL",
                    "entry_price": btc_price,
                    "time": pd.Timestamp.now()
                }
        with col3:
            if st.button("❌ Close Position", use_container_width=True):
                st.session_state.position = None

        if st.session_state.position:
            pos = st.session_state.position
            entry = pos["entry_price"]
            side = pos["side"]
            change_pct = ((btc_price - entry) / entry) * 100 if side == "BUY" else ((entry - btc_price) / entry) * 100
            pnl_color = "green" if change_pct >= 0 else "red"

            st.markdown(f"""
            ### 📊 Active Trade
            - **Side:** {side}
            - **Entry Price:** ${entry:,.2f}
            - **Current Price:** ${btc_price:,.2f}
            - **Unrealized PnL:** <span style='color:{pnl_color}'>**{change_pct:.2f}%**</span>
            """, unsafe_allow_html=True)

            # SL/TP Auto Close
            closed = False
            reason = ""
            if side == "BUY":
                if change_pct <= -stop_loss_pct:
                    reason = "🛑 Stop Loss"
                    closed = True
                elif change_pct >= take_profit_pct:
                    reason = "🎯 Take Profit"
                    closed = True
            elif side == "SELL":
                if change_pct <= -stop_loss_pct:
                    reason = "🛑 Stop Loss"
                    closed = True
                elif change_pct >= take_profit_pct:
                    reason = "🎯 Take Profit"
                    closed = True

            if closed:
                log_trade(side, entry, btc_price, change_pct)
                st.session_state.position = None
                st.info(f"{reason} Triggered. Trade closed.")
        else:
            st.markdown("💤 _No open trade. Use the buttons above to start._")

        if enable_bot and st.session_state.last_bot_action:
            st.success(f"🤖 Auto-Bot Executed: {st.session_state.last_bot_action}")

        # 📊 Trade History
        if st.session_state.trade_log:
            st.markdown("### 📜 Trade History")
            df_log = pd.DataFrame(st.session_state.trade_log)
            st.dataframe(df_log, use_container_width=True)

            csv = df_log.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Trade History as CSV",
                data=csv,
                file_name='trade_history.csv',
                mime='text/csv'
            )

    else:
        st.info(f"Collecting data... Need at least {long_window} values.")
else:
    st.error("Could not fetch BTC price.")

# Backtest code starts here 👇 (must come BEFORE st.rerun)
st.markdown("---")
st.subheader("📊 Backtesting Engine")
...
# (All the backtesting logic here)

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()


if st.button("Run Backtest (last 7 days of 1h candles)"):
    with st.spinner("Fetching historical data..."):
        url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=168"
        try:
            hist_response = requests.get(url)
            hist_data = hist_response.json()["Data"]["Data"]
            df_hist = pd.DataFrame(hist_data)
            df_hist["time"] = pd.to_datetime(df_hist["time"], unit="s")
            df_hist.set_index("time", inplace=True)
            df_hist["short_ma"] = df_hist["close"].rolling(short_window).mean()
            df_hist["long_ma"] = df_hist["close"].rolling(long_window).mean()

            trades = []
            position = None

            for i in range(1, len(df_hist)):
                price = df_hist["close"].iloc[i]
                time_i = df_hist.index[i]
                short = df_hist["short_ma"].iloc[i]
                long = df_hist["long_ma"].iloc[i]

                signal = None
                if short > long and df_hist["short_ma"].iloc[i - 1] <= df_hist["long_ma"].iloc[i - 1]:
                    signal = "BUY"
                elif short < long and df_hist["short_ma"].iloc[i - 1] >= df_hist["long_ma"].iloc[i - 1]:
                    signal = "SELL"

                # Simulate position entry
                if signal and position is None:
                    position = {
                        "side": signal,
                        "entry_price": price,
                        "entry_time": time_i
                    }

                # Simulate SL/TP-based exit
                if position:
                    entry = position["entry_price"]
                    side = position["side"]
                    change_pct = ((price - entry) / entry) * 100 if side == "BUY" else ((entry - price) / entry) * 100

                    if change_pct <= -stop_loss_pct or change_pct >= take_profit_pct:
                        trades.append({
                            "Side": side,
                            "Entry": round(entry, 2),
                            "Exit": round(price, 2),
                            "PnL (%)": round(change_pct, 2),
                            "Open Time": position["entry_time"],
                            "Close Time": time_i
                        })
                        position = None

            if trades:
                df_trades = pd.DataFrame(trades)
                st.success(f"Backtest Complete: {len(df_trades)} trades")
                st.dataframe(df_trades, use_container_width=True)

                total_pnl = df_trades["PnL (%)"].sum()
                win_rate = (df_trades["PnL (%)"] > 0).mean() * 100

                st.markdown(f"""
                ### 📈 Backtest Summary
                - **Total Trades:** {len(df_trades)}
                - **Total PnL:** `{total_pnl:.2f}%`
                - **Win Rate:** `{win_rate:.1f}%`
                """)

                # Optional: CSV download
                csv = df_trades.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Backtest Results", csv, file_name="backtest_results.csv", mime="text/csv")
            else:
                st.warning("No trades were executed in the backtest.")
        except Exception as e:
            st.error(f"Error fetching historical data: {e}")
