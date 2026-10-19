import streamlit as st
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("🌐 100% Contained & Unblocked Web Engine")
st.write("Search and read web pages entirely inside this app. No new tabs required.")

# Initialize session state to keep track of what page the user is reading
if "viewing_url" not in st.session_state:
    st.session_state.viewing_url = None

# --- SIDEBAR SEARCH BAR ---
with st.sidebar:
    st.header("Search Controls")
    search_query = st.text_input("Search the web:", placeholder="Type here...")
    
    # Reset article viewer if a new search is performed
    if st.button("Clear Saved View"):
        st.session_state.viewing_url = None

# --- MAIN CONTENT AREA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔍 Search Results")
    if search_query:
        with st.spinner("Searching safely..."):
            try:
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(search_query, max_results=8)]
                
                if results:
                    for idx, result in enumerate(results):
                        with st.container(border=True):
                            st.markdown(f"### {result['title']}")
                            st.caption(f"URL: {result['href']}")
                            st.write(result['body'])
                            
                            # Clicking this updates our session state without changing tabs
                            if st.button(f"📖 Read Directly inside App", key=f"btn_{idx}"):
                                st.session_state.viewing_url = result['href']
                else:
                    st.warning("No results found.")
            except Exception as e:
                st.error(f"Search error: {e}")
    else:
        st.info("Enter a query in the sidebar to begin searching.")

with col2:
    st.subheader("📄 Safe Content Viewer")
    if st.session_state.viewing_url:
        st.info(f"Reading: {st.session_state.viewing_url}")
        
        with st.spinner("Extracting web text cleanly..."):
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                # Fetch text via python server, bypassing browser local filters
                response = requests.get(st.session_state.viewing_url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Strip out malicious script and style blocks
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                
                # Extract clean text segments
                paragraphs = soup.find_all(['h1', 'h2', 'h3', 'p'])
                
                if paragraphs:
                    for p in paragraphs:
                        if p.name in ['h1', 'h2', 'h3']:
                            st.markdown(f"## {p.text.strip()}")
                        else:
                            st.write(p.text.strip())
                else:
                    st.warning("Could not extract clean text paragraphs from this site. It might be heavily script-based.")
                    
            except Exception as e:
                st.error(f"Failed to fetch site content: {e}")
    else:
        st.info("Click 'Read Directly inside App' on any search result to view its content here.")
