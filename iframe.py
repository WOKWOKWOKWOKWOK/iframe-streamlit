import streamlit as st

st.title("My App with an Embedded Website")

# Paste the URL of the site you want to display inside your Streamlit app
target_url = "https://crazygames.com"

# Render the iframe
st.iframe(target_url, height=600)
