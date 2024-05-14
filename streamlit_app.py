import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
import requests
import plotly.express as px
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

# Chargement des données Telegram
@st.cache_data
def load_telegram_data():
    files = [
        'Data/Telegram_sentiment_bis_1.csv',
        'Data/Telegram_sentiment_bis_2.csv',
        'Data/Telegram_sentiment_bis_3.csv'
    ]
    data_frames = []
    for file in files:
        df = pd.read_csv(file, sep=';', engine='python', names=['channel', 'text', 'sentiment_type'], header=0)
        data_frames.append(df)
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df

# Fonction de nettoyage de texte
def clean_text(df, text_field):
    stop = stopwords.words('english')
    lemmatizer = WordNetLemmatizer()
    df[text_field] = df[text_field].fillna('').astype(str)
    df[text_field] = df[text_field].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in x.split() if word not in stop]))
    df[text_field] = df[text_field].str.replace('[^\w\s]', '', regex=True)
    return df

# Define the color mapping for sentiment display
def apply_color(val):
    colors = {'NEGATIVE': 'background-color: red', 'NEUTRAL': 'background-color: orange', 'POSITIVE': 'background-color: green'}
    return colors.get(val, '')

# Filter and search functionality for Telegram messages
def filter_telegram_data(df, channel_filter, sentiment_filter, keyword):
    if channel_filter:
        df = df[df['channel'].isin(channel_filter)]
    if sentiment_filter:
        df = df[df['sentiment_type'].isin(sentiment_filter)]
    if keyword:
        df = df[df['text'].str.contains(keyword, case=False, na=False)]
    return df

# Visualization of sentiment distribution
def plot_sentiment_distribution(df):
    if df.empty:
        st.warning("No data available to display after applying filters.")
        return None

    sentiment_counts = df['sentiment_type'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment_type', 'count']

    all_sentiments = pd.DataFrame({
        'sentiment_type': ['POSITIVE', 'NEUTRAL', 'NEGATIVE'],
        'count': [0, 0, 0]
    })

    sentiment_counts = pd.merge(all_sentiments, sentiment_counts, on='sentiment_type', how='left').fillna(0)
    sentiment_counts['count'] = sentiment_counts['count_x'] + sentiment_counts['count_y']
    sentiment_counts = sentiment_counts[['sentiment_type', 'count']]

    fig = px.bar(sentiment_counts, x='sentiment_type', y='count', color='sentiment_type',
                 title='Distribution of Sentiment Types',
                 labels={'count': 'Number of Messages', 'sentiment_type': 'Sentiment Type'},
                 color_discrete_map={'POSITIVE': 'green', 'NEGATIVE': 'red', 'NEUTRAL': 'orange'})

    fig.update_layout(xaxis_title='Sentiment Type', yaxis_title='Number of Messages')
    return fig

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

# Fonctions de traitement des données, chargement des données récentes et affichage des prix
def load_crypto_data(filename):
    url = f"{base_url}{filename}"
    df = pd.read_csv(url, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'price'}, inplace=True)
    df['Date_heure'] = pd.to_datetime(df['Date_heure'], format='%d/%m/%Y %H:%M', errors='coerce')
    return df[['Date_heure', 'price']]

def load_recent_data(ticker):
    end_date = datetime.now()
    start_date = end_date - pd.DateOffset(years=5)
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
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

# Fonction d'analyse de sentiment
def analyze_sentiment(text):
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits[0]
    labels = ["NEGATIVE", "NEUTRAL", "POSITIVE"]
    _, predicted_class = torch.max(scores, dim=0)
    return labels[predicted_class]

# Configuration des onglets
tabs = st.tabs(["Data View", "Investment Advice", "Telegram Access", "Sentiment Analysis"])

with tabs[0]:
    st.write('This database has been utilized to study the various fluctuations in the price of this cryptocurrency.')
    option = st.selectbox('Which cryptocurrency data would you like to see?', list(ticker_map.keys()))
    data = load_crypto_data(f"{option.replace(' ', '_')}.csv")
    st.dataframe(data)
    fig = plot_crypto_price(data, f"{option} Historical Price Over Time")
    st.plotly_chart(fig)
    recent_data = load_recent_data(ticker_map[option])
    recent_fig = plot_crypto_price(recent_data, f"{option} Price Last 5 Years")
    st.plotly_chart(recent_fig)

    # Fetch and display crypto-specific news
    st.markdown("**Latest Cryptocurrency News**")
    crypto_news_df = get_news(api_key, option, category="cryptocurrency")
    st.dataframe(crypto_news_df)

with tabs[1]:
    st.markdown("**Investment Advice**")
    videos = [
        ("How To Invest In Crypto Full Beginners Guide", "https://www.youtube.com/watch?v=Yb6825iv0Vk"),
        ("First step in crypto investing", "https://www.youtube.com/watch?v=WFQRXDqLUHY"),
        ("Crypto Review 2023", "https://www.youtube.com/watch?v=K8qYdD1sC7w"),
        ("5 Altcoins To Buy NOW During This Crypto Crash", "https://www.youtube.com/watch?v=b3XoFKeEoeg"),
        ("Crypto Taxes", "https://www.youtube.com/watch?v=bUp4ZSC03QE")
    ]
    for title, url in videos:
        st.markdown(f"### {title}")
        st.video(url)
    st.markdown("For more comprehensive advice, explore all videos on [Jungernaut's YouTube Channel](https://www.youtube.com/@Jungernaut).")

    # Display crypto-specific news in this tab as well
    st.markdown("**Latest Cryptocurrency News**")
    investment_news_df = get_news(api_key, "cryptocurrency")
    st.dataframe(investment_news_df)

# Fetch general news once and display in other tabs
general_news_df = get_news(api_key, "world news")

with tabs[2]:
    st.markdown("**Telegram Access**")
    telegram_df = load_telegram_data()
    channel_filter = st.sidebar.multiselect('Filter by Channel:', options=telegram_df['channel'].unique())
    sentiment_filter = st.sidebar.multiselect('Filter by Sentiment:', options=telegram_df['sentiment_type'].unique())
    keyword = st.sidebar.text_input("Search Keyword:")
    
    filtered_data = filter_telegram_data(telegram_df, channel_filter, sentiment_filter, keyword)
    st.dataframe(filtered_data.style.applymap(apply_color, subset=['sentiment_type']))
    
    fig = plot_sentiment_distribution(filtered_data)
    if fig is not None:
        st.plotly_chart(fig)
    else:
        st.error("Failed to generate sentiment distribution chart.")
    
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)

with tabs[3]:
    st.markdown("**Sentiment Analysis**")
    user_input = st.text_area("Enter your message:")
    if st.button("Analyze"):
        if user_input:
            sentiment = analyze_sentiment(user_input)
            if sentiment:
                color_map = {"NEGATIVE": "red", "NEUTRAL": "orange", "POSITIVE": "green"}
                st.markdown(f"<span style='color:{color_map[sentiment]};'>{sentiment}</span>", unsafe_allow_html=True)
            else:
                st.error("Sentiment analysis failed.")
        else:
            st.warning("Please enter a message to analyze.")
    
    st.markdown("**Latest News**")
    st.dataframe(general_news_df)
