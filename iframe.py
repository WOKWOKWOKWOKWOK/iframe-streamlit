import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from duckduckgo_search import DDGS

st.set_page_config(layout="wide", page_title="Web Portal", page_icon="🌐")

# Custom CSS to hide default headers, center elements, and style the search experience
st.markdown("""
    <style>
    .block-container {padding: 1.5rem 2rem;}
    [data-testid="stHeader"] {display: none;}
    footer {visibility: hidden;}
    
    /* Google-style search aesthetics */
    .google-title {
        font-family: 'Product Sans', Arial, sans-serif;
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        margin-top: 8% !important;
        margin-bottom: 25px !important;
        letter-spacing: -2px;
    }
    iframe {border: 1px solid #30363d; border-radius: 8px; background-color: white;}
    </style>
""", unsafe_allow_html=True)

# 1. State Management for Browsing Mode
if "active_url" not in st.session_state:
    st.session_state.active_url = None

# --- MODE A: THE LANDING PAGE (Google Search UI) ---
if st.session_state.active_url is None:
    # Render stylized Google Title
    st.markdown('<h1 class="google-title"><span style="color:#4285F4">G</span><span style="color:#EA4335">o</span><span style="color:#FBBC05">o</span><span style="color:#4285F4">g</span><span style="color:#34A853">l</span><span style="color:#EA4335">e</span></h1>', unsafe_allow_html=True)
    
    # Central Search Input Box
    with st.form("search_form", clear_on_submit=True):
        user_input = st.text_input(
            "Search Input",
            placeholder="Search the web or type a URL...",
            label_visibility="collapsed"
        )
        submit_search = st.form_submit_button("Search / Go", use_container_width=True)
        
        if submit_search and user_input.strip():
            query = user_input.strip()
            
            # Smart Detection: Is it a direct URL link or a text search phrase?
            if any(query.endswith(ext) for ext in ['.com', '.org', '.net', '.edu', '.de', '.io', '.html']) or query.startswith(('http://', 'https://')):
                if not query.startswith(('http://', 'https://')):
                    query = "https://" + query
                st.session_state.active_url = query
            else:
                # If it's a word/phrase, pass it to an unblocked internal search processing page
                encoded_query = urllib.parse.quote_plus(query)
                st.session_state.active_url = f"INTERNAL_SEARCH://{encoded_query}"
            st.rerun()

# --- MODE B: THE LIVE APP VIEWPORT (Hides search widgets completely) ---
else:
    # Small top utility anchor to let users exit back to the browser homepage
    col_back, _ = st.columns([1, 10])
    with col_back:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.active_url = None
            st.rerun()
            
    current_target = st.session_state.active_url

    # Handle internal search pages dynamically
    if current_target.startswith("INTERNAL_SEARCH://"):
        raw_query = urllib.parse.unquote_plus(current_target.replace("INTERNAL_SEARCH://", ""))
        st.subheader(f"🔍 Web Results for: {raw_query}")
        
        with st.spinner("Retrieving unblocked sources..."):
            try:
                with DDGS() as ddgs:
                    search_results = [r for r in ddgs.text(raw_query, max_results=10)]
                
                if search_results:
                    for result in search_results:
                        with st.container(border=True):
                            # Clicking title opens it safely directly inside your frame state
                            if st.button(result['title'], key=result['href']):
                                st.session_state.active_url = result['href']
                                st.rerun()
                            st.caption(f"🔗 {result['href']}")
                            st.write(result['body'])
                else:
                    st.warning("No indices found.")
            except Exception as e:
                st.error(f"Search API Error: {e}")
                
    # Handle real-time proxy layout rendering for links
    else:
        with st.spinner(f"Navigating to web workspace..."):
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = requests.get(current_target, headers=headers, timeout=12)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Base adjustment for absolute link matching layout rules
                if not soup.find('base'):
                    soup.insert(0, soup.new_tag('base', href=current_target))
                for s in soup(["script"]):
                    s.decompose()
                
                # Full frame canvas display
                st.components.v1.html(str(soup), height=850, scrolling=True)
            except Exception as e:
                st.error(f"Failed to securely render resource: {e}")
