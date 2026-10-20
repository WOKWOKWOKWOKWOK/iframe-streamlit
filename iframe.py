import re
import bs4
import requests
import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Ranked Web Search Engine", page_icon="🔍", layout="centered")

# --- Supabase Initialization ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- Helper: Web Crawler ---
def scrape_url(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers, timeout=8)
    response.raise_for_status()
    
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
        
    title = soup.title.string.strip() if soup.title else url
    text = soup.get_text(separator=" ")
    clean_text = re.sub(r"\s+", " ", text).strip()
    return title, clean_text[:5000]

# --- Helper: Relevance Ranker ---
def calculate_relevance_score(item: dict, query_terms: list[str]) -> float:
    """Calculates a relevance score based on keyword frequency and field weights."""
    score = 0.0
    title = (item.get("title") or "").lower()
    content = (item.get("content") or "").lower()
    category = (item.get("category") or "").lower()

    for term in query_terms:
        term_lower = term.lower()
        # Title matches are weighted highest (3x)
        score += title.count(term_lower) * 3.0
        # Category matches weighted 2x
        score += category.count(term_lower) * 2.0
        # Main body content matches
        score += content.count(term_lower) * 1.0

    return score

# --- App UI ---
st.title("🔍 Ranked Search Engine")

# --- Indexer Sidebar ---
with st.sidebar:
    st.header("🕸️ Web Crawler")
    with st.form("index_form", clear_on_submit=True):
        target_url = st.text_input("URL to Index", placeholder="https://...")
        category = st.text_input("Category", placeholder="Tech, News...")
        submit_crawl = st.form_submit_button("Index Page")

        if submit_crawl and target_url:
            if not target_url.startswith(("http://", "https://")):
                target_url = "https://" + target_url
            try:
                with st.spinner("Crawling content..."):
                    page_title, page_content = scrape_url(target_url)
                    supabase.table("bookmarks").insert({
                        "title": page_title,
                        "url": target_url,
                        "category": category,
                        "content": page_content
                    }).execute()
                st.success(f"Indexed: '{page_title}'")
                st.rerun()
            except Exception as e:
                st.error(f"Crawling failed: {e}")

# --- Search Bar ---
query = st.text_input("Search terms...", placeholder="Enter keywords...")

if query.strip():
    query_terms = query.strip().split()
    formatted_query = " & ".join(query_terms)
    
    # Perform Full-Text Search via Supabase FTS index
    try:
        response = (
            supabase.table("bookmarks")
            .select("*")
            .text_search("fts", formatted_query)
            .execute()
        )
        raw_results = response.data
    except Exception:
        # Fallback if FTS column isn't created yet
        response = (
            supabase.table("bookmarks")
            .select("*")
            .or_(f"title.ilike.%{query}%,content.ilike.%{query}%")
            .execute()
        )
        raw_results = response.data

    # Rank results by term frequency score
    ranked_results = []
    for item in raw_results:
        score = calculate_relevance_score(item, query_terms)
        ranked_results.append((score, item))
    
    # Sort descending by relevance score
    ranked_results.sort(key=lambda x: x[0], reverse=True)
    results = [item for score, item in ranked_results]
else:
    response = supabase.table("bookmarks").select("*").order("created_at", desc=True).limit(10).execute()
    results = response.data

st.caption(f"Found {len(results)} ranked result(s)")

# --- Display Results ---
for item in results:
    with st.container():
        st.markdown(f"### [{item['title']}]({item['url']})")
        st.caption(f"🔗 {item['url']}")
        
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
