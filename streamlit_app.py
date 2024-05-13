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
    df['Date_heure'] = pd.to_datetime(df['Date_heure'], format='%d/%m/%Y %H:%M', errors='coerce')
    return df[['Date_heure', 'price']]

def load_recent_data(ticker):
    """Charge les données des cinqs dernières années depuis Yahoo Finance."""
    end_date = datetime.now()
    start_date = end_date - pd.DateOffset(years=5)
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

def get_news(api_key, q, category=""):
    """Fetches news from NewsAPI, filtered by query and category."""
    base_url = "https://newsapi.org/v2/everything?"
    search_query = q if not category else f"{q} AND {category}"
    url = f"{base_url}q={search_query}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        news_df = pd.DataFrame(articles)
        news_df = news_df[['title', 'description']]
        return news_df
    else:
        st.error(f"Failed to fetch news: HTTP {response.status_code}")
        return pd.DataFrame()

api_key = 'c9c5cccd294f4fb2a51ced5ed618de86'  # Your real API key

tabs = st.tabs(["Data View", "Investment Advice", "Telegram Access", "Sentiment Analysis"])

with tabs[0]:
    st.write('This database has been utilized to study the various fluctuations in the price of this cryptocurrency.')
    option = st.selectbox(
        'Which cryptocurrency data would you like to see?',
        list(ticker_map.keys())
    )
    data = load_crypto_data(f"{option.replace(' ', '_')}.csv")
    st.dataframe(data)
    fig = plot_crypto_price(data, f"{option} Historical Price Over Time")
    st.plotly_chart(fig)
    recent_data = load_recent_data(ticker_map[option])
    recent_fig = plot_crypto_price(recent_data, f"{option} Price Last 2 Years")
    st.plotly_chart(recent_fig)

    # Fetch crypto-specific news in the first tab
    st.markdown("**Latest Cryptocurrency News**")
    crypto_news_df = get_news(api_key, option, category="cryptocurrency")
    st.dataframe(crypto_news_df)

# Fetch general news once and display in other tabs
general_news_df = get_news(api_key, "world news")  # You can change "world news" to any general topic

with tabs[1]:
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)

with tabs[2]:
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)

with tabs[3]:
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)
