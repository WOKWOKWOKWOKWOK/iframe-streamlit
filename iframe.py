import streamlit as st

st.title("Unblocked Iframe Website")

# The website that usually blocks iframes (e.g., wikipedia or a news site)
target_url = "https://google.com" 

# Route it through the allorigins proxy wrapper
unblocked_url = f"https://allorigins.win{target_url}"

# Render the unblocked site
st.iframe(unblocked_url, height=700)
