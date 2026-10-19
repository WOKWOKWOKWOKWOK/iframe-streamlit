import streamlit as st
from duckduckgo_search import DDGS

st.set_page_col_config = {"layout": "wide"}
st.title("🌐 Fully Unblocked Search Engine")
st.write("Search the web directly inside this app without iframe blocks or restrictions.")

# 1. Search input bar
search_query = st.text_input("Enter your search query:", placeholder="Type something here...")

if search_query:
    st.write(f"### Results for: *{search_query}*")
    
    with st.spinner("Searching the web safely..."):
        try:
            # 2. Fetch unblocked results using the DuckDuckGo backend API
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(search_query, max_results=10)]
            
            # 3. Render results cleanly in Streamlit layout
            if results:
                for idx, result in enumerate(results):
                    # Boxed container for each search result
                    with st.container(border=True):
                        st.markdown(f"### [{result['title']}]({result['href']})")
                        st.caption(f"🔗 {result['href']}")
                        st.write(result['body'])
            else:
                st.warning("No results found for this query.")
                
        except Exception as e:
            st.error(f"Search error: {e}. Please try again.")
