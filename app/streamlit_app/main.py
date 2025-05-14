import streamlit as st
import requests
import plotly.graph_objs as go
import pandas as pd
import time

API_BASE = "http://localhost:8001"

# --- Price History Chart Function ---
def plot_price_history(history):
    if not history:
        st.info("No price history to plot.")
        return
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['price'], mode='lines+markers', line=dict(color='#1976d2'), name='Price'))
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Price',
        template='plotly_white',
        margin=dict(l=10, r=10, t=30, b=10),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(
    page_title="Stock Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Hide streamlit default menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("📈 Real-Time Stock Dashboard")

# Fetch stock list
stocks = requests.get(f"{API_BASE}/stocks/stocks").json()
if not stocks:
    st.warning("No stocks available.")
    st.stop()

def stock_label(stock):
    return f"{stock['symbol']} - {stock['name']}"

stock_options = {stock_label(s): s for s in stocks}
selected_label = st.selectbox("Select Stock", list(stock_options.keys()), help="Choose a stock to view details and trade.")
selected_stock = stock_options[selected_label]
stock_id = selected_stock['id']

# --- Main Card: Stock Info and Buy/Sell ---
st.subheader(f"{selected_stock['symbol']} - {selected_stock['name']}")
st.metric("Current Price", f"${selected_stock['price']:.2f}")

col1, col2 = st.columns(2)
with col1:
    quantity = st.number_input("Quantity", min_value=1, value=1, help="Number of shares to trade.")
with col2:
    price = st.number_input("Price", min_value=0.01, value=float(selected_stock['price']), format="%.2f", help="Order price per share.")

buy_col, sell_col = st.columns(2)
buy_clicked = buy_col.button("Buy", use_container_width=True)
sell_clicked = sell_col.button("Sell", use_container_width=True)

if buy_clicked or sell_clicked:
    order_type = "BUY" if buy_clicked else "SELL"
    order_data = {
        "stock_id": stock_id,
        "order_type": order_type,
        "quantity": quantity,
        "price": price
    }
    resp = requests.post(f"{API_BASE}/trades/orders", json=order_data)
    if resp.status_code == 200:
        st.success(f"✅ Order placed: {order_type} {quantity} @ ${price}")
    else:
        st.error(f"❌ Order failed: {resp.text}")

# Fetch and plot price history
history = requests.get(f"{API_BASE}/stocks/stocks/{stock_id}/history").json()
st.subheader("Price History")
plot_price_history(history)

# --- Timer logic for rerun ---
time.sleep(3)  # Fixed 3-second interval
st.rerun()
