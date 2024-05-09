import streamlit as st
import pandas as pd
import yfinance as yf

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. Explore real-time and historical market data!')

@st.cache
def load_crypto_data(ticker):
    data = yf.download(ticker, start="2023-01-01", end="2023-12-31", progress=False)
    data.reset_index(inplace=True)
    data.rename(columns={"Date": "Date_heure", "Close": "price"}, inplace=True)
    return data[['Date_heure', 'price']]

cryptos = {
    'ADA Cardano': 'ADA-USD',
    'BCH Bitcoin Cash': 'BCH-USD',
    'BTC Bitcoin': 'BTC-USD',
    'ETH Ethereum': 'ETH-USD',
    'LTC Litecoin': 'LTC-USD',
    'XRP Ripple': 'XRP-USD'
}

option = st.selectbox(
   'Which cryptocurrency data would you like to see?',
   list(cryptos.keys()))

data = load_crypto_data(cryptos[option])

search_column = st.selectbox('Select column to search:', ['Date_heure', 'price'])
search_value = st.text_input("Search by Date/Time or Close Value:")
if search_value:
    filtered_data = data[data[search_column].astype(str).str.contains(search_value, case=False)]
    st.dataframe(filtered_data)
else:
    st.dataframe(data)

if st.button('Show Chart'):
    st.line_chart(data.set_index('Date_heure')['price'])
