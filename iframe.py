import re
import bs4
import requests
import streamlit as st
from supabase import Client, create_client

st.set_page_config(
    page_title="Web Search Engine", page_icon="🔍", layout="centered"
)


# --- Supabase Initialization ---
@st.cache_resource
def init_supabase() -> Client:
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)


supabase = init_supabase()


# --- Helper: Web Scraper / Crawler ---
def scrape_url(url: str):
  """Fetch web page content and extract title and main text."""
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
  response = requests.get(url, headers=headers, timeout=8)
  response.raise_for_status()

  soup = bs4.BeautifulSoup(response.text, "html.parser")

  # Remove script and style elements
  for element in soup(["script", "style", "nav", "footer", "header"]):
    element.decompose()

  # Extract Title
  title = soup.title.string.strip() if soup.title else url

  # Extract Clean Text
  text = soup.get_text(separator=" ")
  clean_text = re.sub(r"\s+", " ", text).strip()

  return title, clean_text[:5000]  # Store up to first 5000 chars


# --- App UI ---
st.title("🔍 Web Search Engine")

# --- Indexer Sidebar ---
with st.sidebar:
  st.header("🕸️ Web Crawler / Indexer")
  st.write("Add URLs to scrape and index into your search engine database.")

  with st.form("index_form", clear_on_submit=True):
    target_url = st.text_input("Enter Web Page URL", placeholder="https://...")
    category = st.text_input("Category (Optional)", placeholder="Tech, News...")
    submit_crawl = st.form_submit_button("Scrape & Index Page")

    if submit_crawl:
      if target_url:
        if not target_url.startswith(("http://", "https://")):
          target_url = "https://" + target_url

        try:
          with st.spinner("Crawling web page content..."):
            page_title, page_content = scrape_url(target_url)

            supabase.table("bookmarks").insert({
                "title": page_title,
                "url": target_url,
                "category": category,
                "content": page_content,
            }).execute()

          st.success(f"Indexed: '{page_title}'")
          st.rerun()
        except Exception as e:
          st.error(f"Failed to crawl URL: {e}")
      else:
        st.warning("Please enter a valid URL.")

# --- Main Search Interface ---
query = st.text_input("Search the web index...", placeholder="Type keywords...")

if query.strip():
  # Search across Title, URL, Category, AND Page Body Content
  response = (
      supabase.table("bookmarks")
      .select("*")
      .or_(
          f"title.ilike.%{query}%,url.ilike.%{query}%,category.ilike.%{query}%,content.ilike.%{query}%"
      )
      .order("created_at", desc=True)
      .execute()
  )
else:
  response = (
      supabase.table("bookmarks")
      .select("*")
      .order("created_at", desc=True)
      .limit(10)
      .execute()
  )

results = response.data

st.caption(
    f"Showing {len(results)} result(s)"
    + (f" for '{query}'" if query else " (latest indexed)")
)

# --- Display Search Results ---
for item in results:
  with st.container():
    st.markdown(f"### [{item['title']}]({item['url']})")
    st.caption(f"🔗 {item['url']}")

    # Show snippet from scraped page content if available
    content = item.get("content")
    if content:
      snippet = content[:250] + "..." if len(content) > 250 else content
      st.write(snippet)

    cat = item.get("category") or "General"
    st.caption(f"🏷️ Category: **{cat}**")

    col1, col2 = st.columns([6, 1])
    with col2:
      if st.button("Delete", key=f"del_{item['id']}"):
        supabase.table("bookmarks").delete().eq("id", item["id"]).execute()
        st.rerun()

  st.divider()
