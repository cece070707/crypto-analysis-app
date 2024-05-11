import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
import requests

# Configuration de l'URL de base pour les fichiers de données
base_url = 'https://raw.githubusercontent.com/cece070707/crypto-analysis-app/main/Data/'

# Configuration des tickers Yahoo Finance pour chaque cryptomonnaie
ticker_map = {
    'ADA Cardano': 'ADA-USD',
    'BCH Bitcoin Cash': 'BCH-USD',
    'BTC Bitcoin': 'BTC-USD',
    'ETH Ethereum': 'ETH-USD',
    'LTC Litecoin': 'LTC-USD',
    'XRP Ripple': 'XRP-USD'
}

def load_crypto_data(filename):
    """Charge les données historiques depuis un fichier CSV sur GitHub."""
    url = f"{base_url}{filename}"
    df = pd.read_csv(url, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'price'}, inplace=True)
    df['Date_heure'] = pd.to_datetime(df['Date_heure'], errors='coerce')  # Convertir les dates
    return df[['Date_heure', 'price']]

def load_recent_data(ticker):
    """Charge les données des deux dernières années depuis Yahoo Finance."""
    end_date = datetime.now()
    start_date = end_date - pd.DateOffset(years=2)
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    data.reset_index(inplace=True)
    data.rename(columns={"Date": "Date_heure", "Close": "price"}, inplace=True)
    return data[['Date_heure', 'price']]

def plot_crypto_price(data, title):
    """Crée un graphique Plotly pour les données de prix d'une cryptomonnaie."""
    fig = go.Figure(data=[go.Scatter(x=data['Date_heure'], y=data['price'], mode='lines')])
    fig.update_layout(
        title=title,
        xaxis_title='Date and Time',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=True
    )
    return fig

def get_news(api_key, q):
    """Récupère les nouvelles financières depuis une API de nouvelles."""
    url = f"https://newsapi.org/v2/everything?q={q}&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles

# Affichage du titre et description de l'application
st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. Explore real-time and historical market data!')

# Widget pour choisir une cryptomonnaie
option = st.selectbox(
    'Which cryptocurrency data would you like to see?',
    list(ticker_map.keys())
)

# Chargement et affichage des données historiques
data = load_crypto_data(f"{option.replace(' ', '_')}.csv")
fig = plot_crypto_price(data, f"{option} Historical Price Over Time")
st.plotly_chart(fig)

# Chargement et affichage des données récentes
recent_data = load_recent_data(ticker_map[option])
recent_fig = plot_crypto_price(recent_data, f"{option} Price Last 2 Years")
st.plotly_chart(recent_fig)

# Barre de recherche
search_value = st.text_input("Search by Date/Time or Close Value:")
if search_value:
    filtered_data = data[data.apply(lambda row: search_value.lower() in row.astype(str).lower(), axis=1)]
    st.dataframe(filtered_data)
else:
    st.dataframe(data)

# Affichage des nouvelles (Remplacez 'your_api_key' par votre clé API de NewsAPI)
api_key = 'your_api_key'
news_items = get_news(api_key, option)
st.write("Latest News")
for item in news_items:
    st.write(f"{item['title']} - {item['description']}")
