import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Web Scraper Preview")

target_url = "https://google.com"  # Change this to your URL

# 1. Add headers to look like a real browser (fixes 90% of blocking issues)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(target_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. Look for the title safely
    heading_element = soup.find('h1')

    # 3. Add a fallback check so the app never crashes
    if heading_element:
        headline = heading_element.text.strip()
        st.success(f"Latest Update from Site: **{headline}**")
    else:
        # Fallback to the main webpage title if <h1> isn't found
        page_title = soup.title.text if soup.title else "No title found"
        st.warning(f"Could not find an H1 tag. Webpage title is: **{page_title}**")

except Exception as e:
    st.error(f"Failed to connect to the website: {e}")
