import streamlit as st
import requests
from bs4 import BeautifulSoup

# Fetch the site data from the backend server instead of the frontend browser
response = requests.get("https://google.com")
soup = BeautifulSoup(response.text, 'html.parser')

# Grab a specific headline or text block
headline = soup.find('h1').text

st.write(f"Latest Update from Site: **{headline}**")
