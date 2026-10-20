import streamlit as st
from supabase import create_client, Client

# 1. Connect to Supabase using secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("🌐 My Personal Web Hub")

# 2. Sidebar to add new links
st.sidebar.header("Add New Link")
new_title = st.sidebar.text_input("Site Title")
new_url = st.sidebar.text_input("URL (https://...)")
new_cat = st.sidebar.selectbox("Category", ["Work", "Entertainment", "News", "Tech"])

if st.sidebar.button("Save Link"):
    if new_title and new_url:
        data = {"title": new_title, "url": new_url, "category": new_cat}
        supabase.table("bookmarks").insert(data).execute()
        st.sidebar.success("Saved!")
        st.rerun()

# 3. Main Dashboard: Search and Browse
search_query = st.text_input("🔍 Search my browser links...", "")

# Fetch data from Supabase
response = supabase.table("bookmarks").select("*").execute()
links = response.data

# Filter links based on search
if search_query:
    links = [l for l in links if search_query.lower() in l['title'].lower() or search_query.lower() in l['url'].lower()]

# Display links
if links:
    for link in links:
        st.markdown(f"### [{link['title']}]({link['url']})")
        st.caption(f"Category: {link['category']} | Added on: {link['created_at'][:10]}")
else:
    st.info("No links found. Add some in the sidebar!")
