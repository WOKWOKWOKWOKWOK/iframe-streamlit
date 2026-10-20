import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Bookmark Search", page_icon="🔖", layout="centered")

# Initialize Supabase connection
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.title("🔖 Bookmark Search Engine")

# --- Sidebar: Add New Bookmark ---
with st.sidebar:
    st.header("Add New Bookmark")
    with st.form("add_bookmark_form", clear_on_submit=True):
        title = st.text_input("Title")
        url = st.text_input("URL")
        category = st.text_input("Category")
        submitted = st.form_submit_button("Save Bookmark")

        if submitted:
            if title and url:
                supabase.table("bookmarks").insert({
                    "title": title,
                    "url": url,
                    "category": category
                }).execute()
                st.success("Bookmark saved!")
                st.rerun()
            else:
                st.warning("Please enter both a title and a URL.")

# --- Search Bar ---
search_query = st.text_input("🔍 Search bookmarks by title, URL, or category...", "")

# Query database based on schema (id, title, url, category, created_at)
if search_query.strip():
    response = (
        supabase.table("bookmarks")
        .select("*")
        .or_(f"title.ilike.%{search_query}%,url.ilike.%{search_query}%,category.ilike.%{search_query}%")
        .order("created_at", desc=True)
        .execute()
    )
else:
    response = (
        supabase.table("bookmarks")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

bookmarks = response.data

st.write(f"**Found {len(bookmarks)} bookmark(s)**")

# --- Display Results ---
for item in bookmarks:
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### [{item['title']}]({item['url']})")
            cat = item.get("category") if item.get("category") else "Uncategorized"
            created = item.get("created_at", "")[:10]
            st.caption(f"📁 Category: **{cat}** | 📅 Added: {created}")
        with col2:
            if st.button("Delete", key=f"del_{item['id']}"):
                supabase.table("bookmarks").delete().eq("id", item["id"]).execute()
                st.rerun()
    st.divider()
