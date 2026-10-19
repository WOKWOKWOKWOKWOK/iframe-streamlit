import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide", page_title="Unblocked Web Portal")

st.markdown("""
    <style>
    /* Maximize container space to make it feel like a real browser viewport */
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    iframe {border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

st.title("🌐 Network-Bypass Web Viewer")
st.write("Route restricted sites through server-side rendering to bypass local network filters.")

# 1. URL Navigation Bar
target_url = st.text_input("Enter any URL to unblock (include https://):", value="https://wikipedia.org")

if target_url:
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    with st.spinner(f"Routing and rendering {target_url} safely..."):
        try:
            # 2. Server fetches the site, bypassing local client blocks
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            response = requests.get(target_url, headers=headers, timeout=12)
            
            # 3. Parse HTML and fix broken assets (images, CSS links)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Inject a base tag so relative links load relative to the target website, not Streamlit
            if not soup.find('base'):
                base_tag = soup.new_tag('base', href=target_url)
                if soup.head:
                    soup.head.insert(0, base_tag)
                else:
                    soup.insert(0, base_tag)
            
            # Strip strict security frames that break rendering layouts
            for element in soup(["script"]):
                element.decompose()

            modified_html = str(soup)
            
            # 4. Render the entire live website layout smoothly
            st.components.v1.html(modified_html, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"Could not load the requested page. Error detail: {e}")
            st.info("💡 Some major sites require strict Javascript tracking (like Google or YouTube). Try using alternative documentation or wiki links.")
