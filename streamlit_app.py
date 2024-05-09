import streamlit as st
import pandas as pd

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. More features coming soon!')

# Définir les chemins ici si nécessaire
chemin_de_base = 'files/Project/'

# Widget pour choisir une cryptomonnaie
option = st.selectbox(
   'Which cryptocurrency data would you like to see?',
   ('ADA Cardano', 'BCH Bitcoin Cash', 'BTC Bitcoin', 'ETH Ethereum', 'LTC Litecoin', 'XRP Ripple'))

# Fonctions de chargement des données
def load_crypto_data(file_path):
    df = pd.read_csv(file_path, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'Close'}, inplace=True)
    return df

def load_telegram_data(file_path):
    df = pd.read_csv(file_path, delimiter=';', decimal=',')
    df.drop(df.columns[0], axis=1, inplace=True)
    return df

# Chargement des données en fonction de la sélection
if option == 'ADA Cardano':
    data = load_crypto_data(chemin_de_base + 'ADA_Cardano.csv')
elif option == 'BCH Bitcoin Cash':
    data = load_crypto_data(chemin_de_base + 'BCH_Bitcoin_cash.csv')
elif option == 'BTC Bitcoin':
    data = load_crypto_data(chemin_de_base + 'BTC_Bitcoin.csv')
elif option == 'ETH Ethereum':
    data = load_crypto_data(chemin_de_base + 'ETH_Ethereum.csv')
elif option == 'LTC Litecoin':
    data = load_crypto_data(chemin_de_base + 'LTC_Litecoin.csv')
elif option == 'XRP Ripple':
    data = load_crypto_data(chemin_de_base + 'XRP_Ripple.csv')

# Affichage des données
st.write(f"Data for {option}:", data)

# Vous pouvez également ajouter ici la fonction pour afficher les graphiques si vous en avez.
