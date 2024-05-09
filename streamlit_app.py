import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. Explore real-time and historical market data!')

# Fonction pour charger les données historiques
def load_historical_data(filename):
    url = f"https://raw.githubusercontent.com/cece070707/crypto-analysis-app/main/Data/{filename}"
    df = pd.read_csv(url, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'price'}, inplace=True)
    return df

@st.cache
def load_recent_data(ticker):
    end_date = datetime.now().strftime('%Y-%m-%d')
    data = yf.download(ticker, start="2024-04-11", end=end_date, interval='1d', progress=False)
    data.reset_index(inplace=True)
    data.rename(columns={"Date": "Date_heure", "Close": "price"}, inplace=True)
    return data[['Date_heure', 'price']]

# Dictionnaire de correspondance des noms de fichiers et tickers
crypto_assets = {
    'ADA Cardano': ('ADA_Cardano.csv', 'ADA-USD'),
    'BCH Bitcoin Cash': ('BCH_Bitcoin_cash.csv', 'BCH-USD'),
    'BTC Bitcoin': ('BTC_Bitcoin.csv', 'BTC-USD'),
    'ETH Ethereum': ('ETH_Ethereum.csv', 'ETH-USD'),
    'LTC Litecoin': ('LTC_Litecoin.csv', 'LTC-USD'),
    'XRP Ripple': ('XRP_Ripple.csv', 'XRP-USD')
}

option = st.selectbox('Which cryptocurrency data would you like to see?', list(crypto_assets.keys()))
historical_data = load_historical_data(crypto_assets[option][0])
recent_data = load_recent_data(crypto_assets[option][1])

# Fusion des données
full_data = pd.concat([historical_data, recent_data]).reset_index(drop=True)

# Recherche par date ou prix
search_value = st.text_input("Search by Date/Time or Price:")
if search_value:
    try:
        search_result = full_data[full_data['Date_heure'].str.contains(search_value)]
    except:
        search_result = full_data[full_data['price'].astype(str).str.contains(search_value)]
    st.dataframe(search_result)
else:
    st.dataframe(full_data)

if st.button('Show Chart'):
    st.line_chart(full_data.set_index('Date_heure')['price'])
