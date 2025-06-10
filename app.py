import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
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

# Store price history
if "price_data" not in st.session_state:
    st.session_state.price_data = []
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

        # Display metrics
        st.metric("BTC Price (USD)", f"${btc_price:,.2f}")
        st.markdown(f"### Signal: {signal}")

        # Chart with time on x-axis
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=prices, mode='lines+markers', name='BTC Price'))
        fig.add_trace(go.Scatter(x=df["time"], y=short_ma, mode='lines', name='Short MA'))
        fig.add_trace(go.Scatter(x=df["time"], y=long_ma, mode='lines', name='Long MA'))
        fig.update_layout(
            title="BTC Price with Moving Averages",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            legend_title="Legend",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(f"Collecting data... Need at least {long_window} values.")

else:
    st.error("Could not fetch BTC price.")

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()
