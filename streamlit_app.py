import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
import requests

# Configuration de l'URL de base pour les fichiers de données et des tickers Yahoo Finance
base_url = 'https://raw.githubusercontent.com/cece070707/crypto-analysis-app/main/Data/'
ticker_map = {
    'ADA Cardano': 'ADA-USD',
    'BCH Bitcoin Cash': 'BCH-USD',
    'BTC Bitcoin': 'BTC-USD',
    'ETH Ethereum': 'ETH-USD',
    'LTC Litecoin': 'LTC-USD',
    'XRP Ripple': 'XRP-USD'
}

# Configuration des fonctions de traitement des données et de l'API
def load_crypto_data(filename):
    url = f"{base_url}{filename}"
    df = pd.read_csv(url, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'price'}, inplace=True)
    df['Date_heure'] = pd.to_datetime(df['Date_heure'], format='%d/%m/%Y %H:%M', errors='coerce')
    return df[['Date_heure', 'price']]

def load_recent_data(ticker):
    end_date = datetime.now()
    start_date = end_date - pd.DateOffset(years=2)
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    data.reset_index(inplace=True)
    data.rename(columns={"Date": "Date_heure", "Close": "price"}, inplace=True)
    return data[['Date_heure', 'price']]

def plot_crypto_price(data, title):
    fig = go.Figure(data=[go.Scatter(x=data['Date_heure'], y=data['price'], mode='lines')])
    fig.update_layout(title=title, xaxis_title='Date and Time', yaxis_title='Price (USD)', xaxis_rangeslider_visible=True)
    return fig

def get_news(api_key, q, category=""):
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

api_key = 'c9c5cccd294f4fb2a51ced5ed618de86'  # Use your real API key

# Setup tabs
tabs = st.tabs(["Data View", "Investment Advice", "Telegram Access", "Sentiment Analysis"])

with tabs[0]:
    st.write('This database has been utilized to study the various fluctuations in the price of this cryptocurrency.')
    option = st.selectbox('Which cryptocurrency data would you like to see?', list(ticker_map.keys()))
    data = load_crypto_data(f"{option.replace(' ', '_')}.csv")
    st.dataframe(data)
    fig = plot_crypto_price(data, f"{option} Historical Price Over Time")
    st.plotly_chart(fig)
    recent_data = load_recent_data(ticker_map[option])
    recent_fig = plot_crypto_price(recent_data, f"{option} Price Last 2 Years")
    st.plotly_chart(recent_fig)

    # Fetch and display crypto-specific news
    st.markdown("**Latest Cryptocurrency News**")
    crypto_news_df = get_news(api_key, option, category="cryptocurrency")
    st.dataframe(crypto_news_df)

# Fetch general news once for display in other tabs
general_news_df = get_news(api_key, "world news")  # You can adjust the query to fit your needs

with tabs[1]:
    st.markdown("**Investment Advice**")
    st.markdown("""
    Below are some handpicked videos from YouTube that provide insightful trading advice and fundamental analyses of the cryptocurrency market.
    """)
    videos = {
        "5 Altcoins To Buy NOW During This Crypto Crash": "https://www.youtube.com/watch?v=b3XoFKeEoeg",
        "How To Invest In Crypto Full Beginners Guide": "https://www.youtube.com/watch?v=Yb6825iv0Vk",
        "Crypto Review 2023": "https://www.youtube.com/watch?v=K8qYdD1sC7w",
        "First step in crypto investing": "https://www.youtube.com/watch?v=WFQRXDqLUHY",
        "Crypto Taxes": "https://www.youtube.com/watch?v=bUp4ZSC03QE"
    }
    for title, url in videos.items():
        st.markdown(f"### {title}")
        st.video(url)
    st.markdown("For more comprehensive advice, explore all videos on [Jungernaut's YouTube Channel](https://www.youtube.com/@Jungernaut).")

    # Display general news
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)

with tabs[2]:
    st.markdown("**Telegram Access**")
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)

with tabs[3]:
    st.markdown("**Sentiment Analysis**")
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)

