import streamlit as st
import requests
from bs4 import BeautifulSoup

# Maximize layout for a realistic browser viewport experience
st.set_page_config(layout="wide", page_title="Streamlit Web Browser", page_icon="🌐")

# Custom CSS styling to make the interface look exactly like a desktop browser
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    div[data-testid="stForm"] {border: 1px solid #30363d; border-radius: 10px; background-color: #0d1117; padding: 10px;}
    iframe {border: 1px solid #30363d; border-radius: 6px; background-color: white;}
    </style>
""", unsafe_allow_html=True)

# 1. Initialize Browser State Memory
HOME_PAGE = "https://wikipedia.org"

if "history" not in st.session_state:
    st.session_state.history = [HOME_PAGE]
if "history_index" not in st.session_state:
    st.session_state.history_index = 0

current_url = st.session_state.history[st.session_state.history_index]

# 2. Browser Navigation Controls (Top Ribbon)
st.title("🌐 Streamlit Cloud Browser")

# Create a sleek grid for navigation buttons and the address bar
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 12])

with nav_col1:
    # Disable Back button if we are at the beginning of history
    back_disabled = st.session_state.history_index == 0
    if st.button("⬅️", disabled=back_disabled, help="Back"):
        st.session_state.history_index -= 1
        st.rerun()

with nav_col2:
    # Disable Forward button if we are at the newest page
    forward_disabled = st.session_state.history_index == len(st.session_state.history) - 1
    if st.button("➡️", disabled=forward_disabled, help="Forward"):
        st.session_state.history_index += 1
        st.rerun()

with nav_col3:
    if st.button("🏠", help="Home"):
        # Append Home to history stack
        if st.session_state.history[-1] != HOME_PAGE:
            st.session_state.history = st.session_state.history[:st.session_state.history_index + 1]
            st.session_state.history.append(HOME_PAGE)
            st.session_state.history_index = len(st.session_state.history) - 1
        st.rerun()

# Use a form wrapper so hitting "Enter" in the address bar acts like a real browser search
with nav_col4:
    with st.form("url_form", clear_on_submit=False):
        url_input = st.text_input(
            "Address Bar",
            value=current_url,
            label_visibility="collapsed",
            placeholder="Type a URL (e.g., https://utopia.de) and press Enter..."
        )
        submit_btn = st.form_submit_button("Go", use_container_width=True)
        
        if submit_btn and url_input:
            # Clean URL format automatically
            if not url_input.startswith(("http://", "https://")):
                url_input = "https://" + url_input
            
            # If the user typed a new URL, wipe out forward history and add it to stack
            if url_input != current_url:
                st.session_state.history = st.session_state.history[:st.session_state.history_index + 1]
                st.session_state.history.append(url_input)
                st.session_state.history_index = len(st.session_state.history) - 1
                st.rerun()

# 3. Server-Side Rendering Core Engine
with st.spinner(f"Loading {current_url}..."):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        # Fetch the site through Streamlit Cloud infrastructure safely
        response = requests.get(current_url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Inject <base> tag so internal stylesheets and images evaluate relative to the source site
        if not soup.find('base'):
            base_tag = soup.new_tag('base', href=current_url)
            if soup.head:
                soup.head.insert(0, base_tag)
            else:
                soup.insert(0, base_tag)
        
        # Kill heavy analytics script structures that break local framing layout logic
        for element in soup(["script"]):
            element.decompose()

        render_html = str(soup)
        
        # 4. Viewport Output
        st.components.v1.html(render_html, height=750, scrolling=True)
        
    except Exception as e:
        st.error(f"⚠️ Browser Connection Error: {e}")
        st.warning("Make sure the address is completely correct and includes a real extension (like .org, .de, .com).")
