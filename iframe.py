import re
from urllib.parse import urljoin, urlparse
import bs4
import requests
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client

st.set_page_config(
    page_title="Streamlit Web Browser",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Supabase Setup ---
@st.cache_resource
def init_supabase() -> Client:
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)


supabase = init_supabase()


# --- Helper: Page Fetcher & Renderer ---
def fetch_webpage(url: str):
  """Fetches raw web content server-side to bypass client-side iframe blocks."""
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  response = requests.get(url, headers=headers, timeout=10)
  response.raise_for_status()

  soup = bs4.BeautifulSoup(response.text, "html.parser")

  # Inject <base> tag so relative CSS/JS/Image links resolve correctly
  base_tag = soup.new_tag("base", href=url)
  if soup.head:
    soup.head.insert(0, base_tag)
  else:
    soup.insert(0, base_tag)

  # Extract Page Metadata
  title = soup.title.string.strip() if soup.title else url

  # Extract clean text for Reader Mode
  for element in soup(["script", "style", "nav", "footer", "iframe"]):
    element.extract()
  clean_text = re.sub(r"\s+", " ", soup.get_text(separator="\n")).strip()

  return title, str(soup), clean_text


# --- Browser State Management ---
if "current_url" not in st.session_state:
  st.session_state["current_url"] = ""
if "view_mode" not in st.session_state:
  st.session_state["view_mode"] = "Visual Browser"

# --- Sidebar: Bookmarks & History ---
with st.sidebar:
  st.header("🔖 Saved Bookmarks")
  try:
    response = (
        supabase.table("bookmarks")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    bookmarks = response.data

    if not bookmarks:
      st.info("No saved bookmarks yet.")
    for item in bookmarks:
      col1, col2 = st.columns([4, 1])
      with col1:
        if st.button(
            f"🌐 {item['title'][:25]}...",
            key=f"bm_{item['id']}",
            use_container_width=True,
        ):
          st.session_state["current_url"] = item["url"]
          st.rerun()
      with col2:
        if st.button("❌", key=f"del_{item['id']}"):
          supabase.table("bookmarks").delete().eq("id", item["id"]).execute()
          st.rerun()
  except Exception as e:
    st.error(f"Supabase connection issue: {e}")

# --- Browser Header / Navigation Bar ---
st.title("🌐 Python Web Browser")

col_input, col_go = st.columns([5, 1])
with col_input:
  nav_url = st.text_input(
      "URL or Search Query",
      value=st.session_state["current_url"],
      placeholder="Enter URL (e.g., https://example.com) or search term...",
      label_visibility="collapsed",
  )
with col_go:
  navigate = st.button("Go / Search", use_container_width=True)

if navigate and nav_url.strip():
  target = nav_url.strip()
  # Detect if input is a direct URL or search term
  if not target.startswith(("http://", "https://")) and "." in target:
    target = "https://" + target
  elif not target.startswith(("http://", "https://")):
    target = f"SEARCH:{target}"

  st.session_state["current_url"] = target
  st.rerun()

# --- Main Engine View ---
current = st.session_state["current_url"]

if not current:
  st.info(
      "Enter a website URL or search term above to begin browsing the web."
  )

elif current.startswith("SEARCH:"):
  # --- Live Search Results Page ---
  query = current.replace("SEARCH:", "")
  st.subheader(f"🔍 Search Results for: '{query}'")

  try:
    from googlesearch import search

    results = list(search(query, num_results=10, advanced=True))

    for idx, item in enumerate(results):
      with st.container():
        st.markdown(f"### [{item.title}]({item.url})")
        st.caption(f"🔗 {item.url}")
        st.write(
            item.description
            if item.description
            else "No preview description."
        )

        b_col1, b_col2 = st.columns([1, 4])
        with b_col1:
          if st.button("Open in Browser 🚀", key=f"open_{idx}"):
            st.session_state["current_url"] = item.url
            st.rerun()
        with b_col2:
          if st.button("Bookmark 🔖", key=f"bm_search_{idx}"):
            supabase.table("bookmarks").insert(
                {"title": item.title, "url": item.url, "category": "Search Result"}
            ).execute()
            st.toast("Saved to Supabase!")
      st.divider()
  except Exception as e:
    st.error(f"Search failed: {e}")

else:
  # --- Web Page Viewer Mode ---
  st.session_state["view_mode"] = st.radio(
      "View Mode",
      ["Visual Browser", "Reader View"],
      horizontal=True,
      label_visibility="collapsed",
  )

  try:
    with st.spinner(f"Loading {current}..."):
      title, html_content, reader_text = fetch_webpage(current)

    # Action Toolbar
    act_col1, act_col2, act_col3 = st.columns([3, 1, 1])
    with act_col1:
      st.subheader(f"📄 {title}")
    with act_col2:
      if st.button("Bookmark Page 🔖", use_container_width=True):
        supabase.table("bookmarks").insert(
            {"title": title, "url": current, "category": "Browsed Page"}
        ).execute()
        st.toast("Saved to Supabase!")
    with act_col3:
      st.markdown(
          f"[Open External ↗️]({current})", unsafe_allow_html=True
      )

    st.divider()

    # Render Content
    if st.session_state["view_mode"] == "Visual Browser":
      # Direct HTML rendering inside custom viewer frame
      components.html(html_content, height=800, scrolling=True)
    else:
      # Stripped down clean Reader View
      st.text_area(
          "Page Text Content", value=reader_text, height=700
      )

  except Exception as e:
    st.error(f"Failed to fetch webpage at `{current}`: {e}")
