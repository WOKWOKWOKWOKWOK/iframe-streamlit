import streamlit as st
from duckduckgo_search import DDGS
from supabase import Client, create_client

st.set_page_config(
    page_title="Live Web Search Engine", page_icon="🌐", layout="centered"
)


# --- Supabase Setup ---
@st.cache_resource
def init_supabase() -> Client:
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)


supabase = init_supabase()

st.title("🌐 Live Web Search Engine")

# --- Search Bar ---
query = st.text_input(
    "Search the web...", placeholder="Type anything (e.g. latest tech news)..."
)
max_results = st.slider("Results count", min_value=5, max_value=20, value=10)

if query.strip():
  # 1. Log search query to Supabase (optional)
  try:
    supabase.table("bookmarks").insert(
        {"title": f"Search: {query}", "url": f"https://duckduckgo.com/?q={query}", "category": "Search Query"}
    ).execute()
  except Exception:
    pass  # Ignore if schema doesn't match

  # 2. Query the live web
  with st.spinner(f"Searching the web for '{query}'..."):
    try:
      results = []
      with DDGS() as ddgs:
        ddgs_results = ddgs.text(query, max_results=max_results)
        if ddgs_results:
          results = list(ddgs_results)

      if not results:
        st.warning("No live web results found.")
      else:
        st.caption(f"Showing top {len(results)} live results for **{query}**")

        # 3. Display Live Search Results
        for item in results:
          with st.container():
            st.markdown(f"### [{item['title']}]({item['href']})")
            st.caption(f"🔗 {item['href']}")
            st.write(item["body"])

            # Save result directly to Supabase as a bookmark
            col1, col2 = st.columns([5, 1])
            with col2:
              if st.button("Bookmark 🔖", key=item["href"]):
                supabase.table("bookmarks").insert({
                    "title": item["title"],
                    "url": item["href"],
                    "category": "Saved Result",
                }).execute()
                st.toast("Saved to Supabase!")

          st.divider()

    except Exception as e:
      st.error(f"Error fetching live results: {e}")

else:
  # Display recently saved bookmarks from Supabase when search bar is empty
  st.subheader("📌 Recently Saved Bookmarks")
  response = (
      supabase.table("bookmarks")
      .select("*")
      .order("created_at", desc=True)
      .limit(5)
      .execute()
  )
  saved_items = response.data

  if not saved_items:
    st.info("Type a query above to start searching the live internet.")
  else:
    for item in saved_items:
      st.markdown(f"• [{item['title']}]({item['url']}) — *{item.get('category', 'General')}*")
