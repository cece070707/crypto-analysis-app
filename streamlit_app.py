import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. Explore real-time and historical market data!')

# Fonctions de chargement des données
def load_historical_data(filename):
    url = f"https://raw.githubusercontent.com/cece070707/crypto-analysis-app/main/Data/{filename}"
    df = pd.read_csv(url, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'price'}, inplace=True)
    df['Date_heure'] = pd.to_datetime(df['Date_heure'])  # Assurer que les dates sont au format datetime
    return df

@st.cache
def load_recent_data(ticker):
    end_date = datetime.now().strftime('%Y-%m-%d')
    data = yf.download(ticker, start="2024-04-11", end=end_date, interval='1d', progress=False)
    data.reset_index(inplace=True)
    data.rename(columns={"Date": "Date_heure", "Close": "price"}, inplace=True)
    data['Date_heure'] = pd.to_datetime(data['Date_heure'])
    return data[['Date_heure', 'price']]

# Fonction pour créer un graphique Plotly
def create_price_chart(data, title='Cryptocurrency Price Over Time'):
    fig = go.Figure(data=[go.Scatter(x=data['Date_heure'], y=data['price'], mode='lines')])
    fig.update_layout(
        title=title,
        xaxis_title='Date and Time',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=True
    )
    return fig

# Sélection et chargement des données
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
full_data = pd.concat([historical_data, recent_data]).reset_index(drop=True)

# Recherche et affichage des données
search_value = st.text_input("Search by Date/Time or Price:")
if search_value:
    try:
        search_result = full_data[full_data['Date_heure'].str.contains(search_value)]
    except:
        search_result = full_data[full_data['price'].astype(str).str.contains(search_value)]
    st.dataframe(search_result)
else:
    st.dataframe(full_data)

# Affichage du graphique
if st.button('Show Chart'):
    fig = create_price_chart(full_data, title=f"{option} Price Over Time")
    st.plotly_chart(fig)
