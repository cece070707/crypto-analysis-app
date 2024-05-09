import streamlit as st
import pandas as pd

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. More features coming soon!')

# URL de base pour les fichiers de données sur GitHub
base_url = 'https://raw.githubusercontent.com/cece070707/crypto-analysis-app/main/Data/'

# Fonctions de chargement des données
def load_crypto_data(filename):
    url = f"{base_url}{filename}"
    df = pd.read_csv(url, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'Close'}, inplace=True)
    # Sélectionner uniquement les colonnes 'Date_heure' et 'Close'
    return df[['Date_heure', 'Close']]

# Widget pour choisir une cryptomonnaie
option = st.selectbox(
   'Which cryptocurrency data would you like to see?',
   ('ADA Cardano', 'BCH Bitcoin Cash', 'BTC Bitcoin', 'ETH Ethereum', 'LTC Litecoin', 'XRP Ripple'))

# Dictionnaire de correspondance des noms de fichiers
file_names = {
    'ADA Cardano': 'ADA_Cardano.csv',
    'BCH Bitcoin Cash': 'BCH_Bitcoin_cash.csv',
    'BTC Bitcoin': 'BTC_Bitcoin.csv',
    'ETH Ethereum': 'ETH_Ethereum.csv',
    'LTC Litecoin': 'LTC_Litecoin.csv',
    'XRP Ripple': 'XRP_Ripple.csv'
}

# Chargement des données en fonction de la sélection
data = load_crypto_data(file_names[option])

# Styliser les données
def highlight_cols(s):
    return ['background-color: #f0f9e8' if s.name in ['Close'] else 'background-color: #fffff9' for v in s]

# Affichage des données sans index et avec style
st.dataframe(data.style.apply(highlight_cols, axis=0).hide_index())

# Barre de recherche (optionnel)
st.write("Search Data:")
search_query = st.text_input("Enter Date/Close value to search:")
filtered_data = data[data.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
st.dataframe(filtered_data.style.apply(highlight_cols, axis=0).hide_index())
