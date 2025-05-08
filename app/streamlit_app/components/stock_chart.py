import streamlit as st
import pandas as pd

def plot_price_history(history):
    if not history:
        st.info("No price history to plot.")
        return
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    st.line_chart(data=df, x='timestamp', y='price', use_container_width=True)
