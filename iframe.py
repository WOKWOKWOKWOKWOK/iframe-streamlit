import streamlit as st
from googlesearch import search
from supabase import create_client, Client

st.set_page_config(page_title="Live Web Search Engine", page_icon="🌐", layout="centered")

# --- Supabase Initialization ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.title("🌐 Live Web Search Engine")

# --- Search Bar ---
query = st.text_input("Search the web...", placeholder="Type anything (e.g. crazygames, tech news)...")
max_results = st.slider("Results count", min_value=5, max_value=20, value=10)

if query.strip():
    with st.spinner(f"Searching live web for '{query}'..."):
        try:
            # Execute Google Search query
            results = list(search(query, num_results=max_results, advanced=True))
            
            if not results:
                st.warning("No results found.")
            else:
                st.caption(f"Showing top {len(results)} live results for **{query}**")
                
                for idx, item in enumerate(results):
                    with st.container():
                        title = item.title if item.title else item.url
                        description = item.description if item.description else "No description available."
                        
                        st.markdown(f"### [{title}]({item.url})")
                        st.caption(f"🔗 {item.url}")
                        st.write(description)
                        
                        # Save result directly to Supabase
                        col1, col2 = st.columns([5, 1])
                        with col2:
                            if st.button("Bookmark 🔖", key=f"btn_{idx}_{item.url}"):
                                supabase.table("bookmarks").insert({
                                    "title": title,
                                    "url": item.url,
                                    "category": "Saved Result"
                                }).execute()
                                st.toast("Saved to Supabase!")
                                
                    st.divider()

        except Exception as e:
            st.error(f"Search error: {e}")

else:
    # Display saved bookmarks from Supabase when search bar is empty
    st.subheader("📌 Recently Saved Bookmarks")
    try:
        response = supabase.table("bookmarks").select("*").order("created_at", desc=True).limit(5).execute()
        saved_items = response.data

        if not saved_items:
            st.info("Type a query above to start searching the live internet.")
        else:
            for item in saved_items:
                st.markdown(f"• [{item['title']}]({item['url']}) — *{item.get('category', 'General')}*")
    except Exception:
        st.info("Type a query above to search.")
