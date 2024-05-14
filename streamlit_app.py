import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
import requests
import plotly.express as px
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Importation conditionnelle pour transformers
try:
    from transformers import RobertaTokenizer, RobertaForSequenceClassification
    import torch

    # Chargement du modèle et du tokenizer pré-entraînés
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForSequenceClassification.from_pretrained(model_name)

    def analyse_sentiment(texte):
        input_encodé = tokenizer(texte, return_tensors='pt', truncation=True, max_length=512)
        sortie = model(**input_encodé)
        probabilités = torch.nn.functional.softmax(sortie.logits, dim=-1)
        score_sentiment = torch.argmax(probabilités, dim=-1).item()
        return score_sentiment

    etiquettes_sentiment = {0: "NÉGATIF", 1: "NEUTRE", 2: "POSITIF"}
    couleurs_sentiment = {0: 'background-color: red', 1: 'background-color: orange', 2: 'background-color: green'}

except ImportError as e:
    st.error(f"Échec de l'importation des bibliothèques nécessaires pour l'analyse de sentiment : {e}")
    st.stop()

@st.cache
def load_telegram_data():
    fichiers = [
        'Data/Telegram_sentiment_bis_1.csv',
        'Data/Telegram_sentiment_bis_2.csv',
        'Data/Telegram_sentiment_bis_3.csv'
    ]
    data_frames = []
    for fichier in fichiers:
        df = pd.read_csv(fichier, sep=';', engine='python', names=['channel', 'text', 'sentiment_type'], header=0)
        data_frames.append(df)
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df

def clean_text(df, text_field):
    stop = stopwords.words('english')
    lemmatizer = WordNetLemmatizer()
    df[text_field] = df[text_field].fillna('').astype(str)
    df[text_field] = df[text_field].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in x.split() if word not in stop]))
    df[text_field] = df[text_field].str.replace('[^\w\s]', '', regex=True)
    return df

def apply_color(val):
    colors = {'NEGATIVE': 'background-color: red', 'NEUTRAL': 'background-color: orange', 'POSITIVE': 'background-color: green'}
    return colors.get(val, '')

def filter_telegram_data(df, channel_filter, sentiment_filter, keyword):
    if channel_filter:
        df = df[df['channel'].isin(channel_filter)]
    if sentiment_filter:
        df = df[df['sentiment_type'].isin(sentiment_filter)]
    if keyword:
        df = df[df['text'].str.contains(keyword, case=False, na=False)]
    return df

def plot_sentiment_distribution(df):
    if df.empty:
        st.warning("Aucune donnée disponible à afficher après l'application des filtres.")
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
                 title='Distribution des types de sentiments',
                 labels={'count': 'Nombre de messages', 'sentiment_type': 'Type de sentiment'},
                 color_discrete_map={'POSITIVE': 'green', 'NEGATIVE': 'red', 'NEUTRAL': 'orange'})

    fig.update_layout(xaxis_title='Type de sentiment', yaxis_title='Nombre de messages')
    return fig

base_url = 'https://raw.githubusercontent.com/cece070707/crypto-analysis-app/main/Data/'
ticker_map = {
    'ADA Cardano': 'ADA-USD',
    'BCH Bitcoin Cash': 'BCH-USD',
    'BTC Bitcoin': 'BTC-USD',
    'ETH Ethereum': 'ETH-USD',
    'LTC Litecoin': 'LTC-USD',
    'XRP Ripple': 'XRP-USD'
}

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
    fig.update_layout(title=title, xaxis_title='Date et Heure', yaxis_title='Prix (USD)', xaxis_rangeslider_visible=True)
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
        st.error(f"Échec de la récupération des actualités : HTTP {response.status_code}")
        return pd.DataFrame()

api_key = 'c9c5cccd294f4fb2a51ced5ed618de86'  # Utilisez votre véritable clé API

tabs = st.tabs(["Vue des données", "Conseils d'investissement", "Accès Telegram", "Analyse de Sentiment"])

with tabs[0]:
    st.write('Cette base de données a été utilisée pour étudier les différentes fluctuations du prix de cette cryptomonnaie.')
    option = st.selectbox('Quelle donnée de cryptomonnaie souhaitez-vous voir ?', list(ticker_map.keys()))
    data = load_crypto_data(f"{option.replace(' ', '_')}.csv")
    st.dataframe(data)
    fig = plot_crypto_price(data, f"{option} Prix Historique au Fil du Temps")
    st.plotly_chart(fig)
    recent_data = load_recent_data(ticker_map[option])
    recent_fig = plot_crypto_price(recent_data, f"{option} Prix des 5 Dernières Années")
    st.plotly_chart(recent_fig)

    st.markdown("**Dernières Actualités sur les Cryptomonnaies**")
    crypto_news_df = get_news(api_key, option, category="cryptocurrency")
    st.dataframe(crypto_news_df)

with tabs[1]:
    st.markdown("**Conseils d'investissement**")
    videos = [
        ("Comment investir dans les cryptomonnaies - Guide complet pour débutants", "https://www.youtube.com/watch?v=Yb6825iv0Vk"),
        ("Première étape pour investir dans les cryptomonnaies", "https://www.youtube.com/watch?v=WFQRXDqLUHY"),
        ("Revue des cryptomonnaies 2023", "https://www.youtube.com/watch?v=K8qYdD1sC7w"),
        ("5 Altcoins à acheter MAINTENANT pendant cette chute des cryptomonnaies", "https://www.youtube.com/watch?v=b3XoFKeEoeg"),
        ("Les taxes sur les cryptomonnaies", "https://www.youtube.com/watch?v=bUp4ZSC03QE")
    ]
    for title, url in videos:
        st.markdown(f"### {title}")
        st.video(url)
    st.markdown("Pour des conseils plus complets, explorez toutes les vidéos sur [la chaîne YouTube de Jungernaut](https://www.youtube.com/@Jungernaut).")

    st.markdown("**Dernières Actualités sur les Cryptomonnaies**")
    investment_news_df = get_news(api_key, "cryptocurrency")
    st.dataframe(investment_news_df)

general_news_df = get_news(api_key, "world news")

with tabs[2]:
    st.markdown("**Accès Telegram**")
    telegram_df = load_telegram_data()
    channel_filter = st.sidebar.multiselect('Filtrer par Canal :', options=telegram_df['channel'].unique())
    sentiment_filter = st.sidebar.multiselect('Filtrer par Sentiment :', options=telegram_df['sentiment_type'].unique())
    keyword = st.sidebar.text_input("Rechercher un Mot-Clé :")
    
    filtered_data = filter_telegram_data(telegram_df, channel_filter, sentiment_filter, keyword)
    st.dataframe(filtered_data.style.applymap(apply_color, subset=['sentiment_type']))
    
    fig = plot_sentiment_distribution(filtered_data)
    if fig is not None:
        st.plotly_chart(fig)
    else:
        st.error("Échec de la génération du graphique de distribution des sentiments.")
    
    st.markdown("**Dernières Actualités**")
    st.dataframe(general_news_df)

with tabs[3]:
    st.markdown("## Analyse de Sentiment")
    st.markdown("**Entrez votre message pour analyser le sentiment**")
    
    input_utilisateur = st.text_area("Entrez votre message ici :", height=150)
    if st.button("Analyser le Sentiment"):
        if input_utilisateur:
            score = analyse_sentiment(input_utilisateur)
            sentiment = etiquettes_sentiment[score]
            couleur = couleurs_sentiment[score]
            st.markdown(f"### Sentiment : {sentiment}")
            st.markdown(f'<h3 style="{couleur}">{sentiment}</h3>', unsafe_allow_html=True)
        else:
            st.warning("Veuillez entrer un message à analyser.")

    st.markdown("**Dernières Actualités**")
    st.dataframe(general_news_df)

