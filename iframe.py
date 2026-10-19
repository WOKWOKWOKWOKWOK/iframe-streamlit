import streamlit as st
import urllib.parse
from duckduckgo_search import DDGS

st.set_page_config(layout="wide", page_title="Web Portal", page_icon="🌐")

# Cleaned custom CSS for smooth interface navigation
st.markdown("""
    <style>
    .block-container {padding: 1.5rem 2rem;}
    [data-testid="stHeader"] {display: none;}
    footer {visibility: hidden;}
    
    /* Google-style title aesthetics */
    .google-title {
        font-family: Arial, sans-serif;
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        margin-top: 8% !important;
        margin-bottom: 25px !important;
        letter-spacing: -2px;
    }
    
    /* Clean formatting for search result cards */
    .result-link {
        font-size: 20px;
        color: #1a0dab;
        text-decoration: none;
        font-weight: 500;
    }
    .result-link:hover {
        text-decoration: underline;
    }
    .result-url {
        color: #006621;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .result-snippet {
        color: #545454;
        font-size: 14px;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# 1. State Management for Browsing Mode
if "active_query" not in st.session_state:
    st.session_state.active_query = None

# --- MODE A: THE LANDING PAGE (Google Search UI) ---
if st.session_state.active_query is None:
    st.markdown('<h1 class="google-title"><span style="color:#4285F4">G</span><span style="color:#EA4335">o</span><span style="color:#FBBC05">o</span><span style="color:#4285F4">g</span><span style="color:#34A853">l</span><span style="color:#EA4335">e</span></h1>', unsafe_allow_html=True)
    
    with st.form("search_form", clear_on_submit=True):
        user_input = st.text_input(
            "Search Input",
            placeholder="Search the web...",
            label_visibility="collapsed"
        )
        submit_search = st.form_submit_button("Search", use_container_width=True)
        
        if submit_search and user_input.strip():
            st.session_state.active_query = user_input.strip()
            st.rerun()

# --- MODE B: THE WEB RESULTS VIEW (Fixed connection errors) ---
else:
    # Navigation row
    col_back, _ = st.columns([1, 10])
    with col_back:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.active_query = None
            st.rerun()
            
    raw_query = st.session_state.active_query
    st.subheader(f"🔍 Web Results for: {raw_query}")
    st.write("---")
    
    with st.spinner("Retrieving search results..."):
        try:
            # Fetch results using the duckduckgo search wrapper safely
            with DDGS() as ddgs:
                search_results = [r for r in ddgs.text(raw_query, max_results=10)]
            
            if search_results:
                for result in search_results:
                    with st.container():
                        # Native HTML styling ensures it looks like genuine search outputs and avoids connection bans
                        st.markdown(f"""
                            <div>
                                <a class="result-link" href="{result['href']}" target="_blank">{result['title']}</a>
                                <div class="result-url">{result['href']}</div>
                                <div class="result-snippet">{result['body']}</div>
                            </div>
                            <br>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No search results found. Try adjusting your keywords.")
        except Exception as e:
            st.error(f"Search API Error: {e}")
