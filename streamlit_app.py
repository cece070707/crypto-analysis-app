import streamlit as st
import pandas as pd
import requests

st.title('Crypto Analysis App')
st.write('Welcome to the Crypto Analysis App. More features coming soon!')

@st.cache
def load_crypto_data(api_url):
    response = requests.get(api_url)
    data = pd.DataFrame(response.json())
    data['Date_heure'] = pd.to_datetime(data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return data[['Date_heure', 'price']]

option = st.selectbox(
   'Which cryptocurrency data would you like to see?',
   ('ADA Cardano', 'BCH Bitcoin Cash', 'BTC Bitcoin', 'ETH Ethereum', 'LTC Litecoin', 'XRP Ripple'))

api_urls = {
    'ADA Cardano': 'https://api.example.com/ADA',
    'BCH Bitcoin Cash': 'https://api.example.com/BCH',
    'BTC Bitcoin': 'https://api.example.com/BTC',
    'ETH Ethereum': 'https://api.example.com/ETH',
    'LTC Litecoin': 'https://api.example.com/LTC',
    'XRP Ripple': 'https://api.example.com/XRP'
}

data = load_crypto_data(api_urls[option])

search_column = st.selectbox('Select column to search:', ['Date_heure', 'price'])
search_value = st.text_input("Search by Date/Time or Close Value:")
if search_value:
    filtered_data = data[data[search_column].astype(str).str.contains(search_value, case=False)]
    st.dataframe(filtered_data)
else:
    st.dataframe(data)

if st.button('Show Chart'):
    st.line_chart(data.set_index('Date_heure')['price'])

