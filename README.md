# 📈 Bitcoin Signal Dashboard

A real-time crypto trading assistant powered by Streamlit, Plotly, and the CryptoCompare API.

This interactive dashboard delivers **BTC buy/sell signals**, **live charts**, **technical indicators**, and **a simulated trading engine** — all built in Python and deployable via Streamlit Cloud.

---

## 🚀 Live Demo

🟢 [Click here to try the live app](https://share.streamlit.io/YOUR_APP_LINK)

---

## 🧠 Features

### ✅ Real-Time BTC Data
- Pulls live Bitcoin prices from CryptoCompare API
- Auto-refreshes on a custom timer

### 📉 Technical Indicators
- **Moving Averages (MA)** — Custom short/long windows
- **RSI (Relative Strength Index)** — Visual with overbought/oversold zones
- **MACD (Moving Average Convergence Divergence)**

### 📊 Interactive Charts
- Built with Plotly for a responsive, modern UI
- Real-time line charts and overlays

### 🤖 Auto-Bot Trading Logic
- Simulates long/short entry and exit
- Triggered based on MA crossovers
- Integrated stop-loss / take-profit logic
- Maintains trade history with download option

### 🔬 Backtesting Engine
- Runs simulated trades on the last 7 days of BTC data (1-hour candles)
- Displays all trades and performance summary
- Chart overlay of buy/sell markers

### 🏆 Local Leaderboard
- Stores best backtests locally in session state
- Sortable by Total PnL or Win Rate
- Resettable with one click
- Exportable to CSV

---

## 🛠️ Tech Stack

| Component       | Technology               |
|----------------|---------------------------|
| Frontend       | [Streamlit](https://streamlit.io) |
| Charts         | [Plotly](https://plotly.com/python/) |
| Data Handling  | [Pandas](https://pandas.pydata.org/) |
| API Source     | [CryptoCompare](https://min-api.cryptocompare.com/) |
| Hosting        | [Streamlit Cloud](https://streamlit.io/cloud) |

---

## 📁 File Structure

