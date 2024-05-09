import streamlit as st

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. More features coming soon!')
import streamlit as st
import pandas as pd

# Définir les chemins ici si nécessaire
chemin_de_base = 'path/to/your/data/'

# Vos fonctions de chargement de données
def load_crypto_data(file_path):
    df = pd.read_csv(file_path, delimiter=';', decimal=',', skiprows=1)
    df.rename(columns={df.columns[0]: 'Date_heure', df.columns[1]: 'Close'}, inplace=True)
    return df

def load_telegram_data(file_path):
    df = pd.read_csv(file_path, delimiter=';', decimal=',')
    df.drop(df.columns[0], axis=1, inplace=True)
    return df

