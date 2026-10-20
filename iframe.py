from collections import Counter, defaultdict
import math
import re


class SearchEngine:

  def __init__(self):
    self.documents = {}  # doc_id -> raw document details
    self.inverted_index = defaultdict(
        list
    )  # word -> list of (doc_id, term_frequency)
    self.doc_lengths = {}  # doc_id -> token count
    self.doc_vectors = {}  # doc_id -> {word: tfidf_score}
    self.idf = {}  # word -> idf_score

  def tokenize(self, text):
    """Clean text, convert to lowercase, and split into words."""
    words = re.findall(r"\b\w+\b", text.lower())

    # Stop words to filter out common noisy words
    stop_words = {
        "the",
        "is",
        "at",
        "which",
        "on",
        "a",
        "an",
        "and",
        "or",
        "in",
        "to",
        "for",
        "of",
        "with",
        "it",
        "that",
        "this",
        "by",
        "from",
        "be",
        "are",
        "was",
    }
    return [w for w in words if w not in stop_words and not w.isdigit()]

  def add_document(self, doc_id, title, content):
    """Add a document to the search database."""
    self.documents[doc_id] = {"title": title, "content": content}

    # Combine title and content (giving extra weight to title)
    full_text = f"{title} {title} {content}"
    tokens = self.tokenize(full_text)
    self.doc_lengths[doc_id] = len(tokens)

    # Record term counts for inverted index
    term_counts = Counter(tokens)
    for term, count in term_counts.items():
      self.inverted_index[term].append((doc_id, count))

  def build_index(self):
    """Compute IDF weights and document vectors for search scoring."""
    num_docs = len(self.documents)
    if num_docs == 0:
      return

    # 1. Compute Inverse Document Frequency (IDF)
    for term, postings in self.inverted_index.items():
      doc_count = len(postings)
      self.idf[term] = math.log((num_docs + 1) / (doc_count + 1)) + 1

    # 2. Compute TF-IDF vectors for documents
    for term, postings in self.inverted_index.items():
      for doc_id, count in postings:
        tf = count / self.doc_lengths[doc_id]
        tfidf = tf * self.idf[term]

        if doc_id not in self.doc_vectors:
          self.doc_vectors[doc_id] = {}
        self.doc_vectors[doc_id][term] = tfidf

  def search(self, query, top_k=5):
    """Search for a query and return top ranked results."""
    query_tokens = self.tokenize(query)
    if not query_tokens:
      return []

    # Calculate query vector (TF-IDF)
    query_counts = Counter(query_tokens)
    query_len = len(query_tokens)
    query_vector = {}

    for term, count in query_counts.items():
      if term in self.idf:
        tf = count / query_len
        query_vector[term] = tf * self.idf[term]

    if not query_vector:
      return []

    # Cosine similarity scoring against indexed documents
    scores = defaultdict(float)
    query_norm = math.sqrt(sum(val**2 for val in query_vector.values()))

    for term, q_tfidf in query_vector.items():
      for doc_id, _ in self.inverted_index.get(term, []):
        doc_tfidf = self.doc_vectors[doc_id].get(term, 0)
        scores[doc_id] += q_tfidf * doc_tfidf

    # Normalize by document magnitude
    results = []
    for doc_id, raw_score in scores.items():
      doc_norm = math.sqrt(
          sum(val**2 for val in self.doc_vectors[doc_id].values())
      )
      if doc_norm > 0 and query_norm > 0:
        similarity = raw_score / (doc_norm * query_norm)
        results.append((doc_id, similarity))

    # Sort results by similarity score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


# ==========================================
# Example Usage / Interactive CLI Setup
# ==========================================
if __name__ == "__main__":
  engine = SearchEngine()

  # Sample document index
  sample_docs = [
      (
          1,
          "Python Programming Language",
          "Python is an interpreted, high-level, general-purpose programming"
          " language. It is widely used in data science, web development, and"
          " AI.",
      ),
      (
          2,
          "CSS Shadow and Box Styling",
          "In CSS, box-shadow and drop-shadow are properties used to add shadow"
          " effects around an element's frame or content.",
      ),
      (
          3,
          "Artificial Intelligence and Machine Learning",
          "Machine learning is a branch of artificial intelligence focused on"
          " building applications that learn from data and improve accuracy"
          " over time.",
      ),
      (
          4,
          "Web Crawling and Search Engines",
          "Search engines use web crawlers to discover content, build indexes"
          " with TF-IDF algorithms, and return relevant web pages.",
      ),
      (
          5,
          "Shadows in 3D Computer Graphics",
          "3D rendering engines calculate ray tracing and shadow maps to simulate"
          " realistic light, dark shadows, and reflection effects.",
      ),
  ]

  print("Indexing sample documents...")
  for doc_id, title, content in sample_docs:
    engine.add_document(doc_id, title, content)

  # Finalize internal calculations
  engine.build_index()
  print("Indexing complete!\n")

  print("=== Mini Python Search Engine ===")
  print("Type a search query (or type 'exit' to quit):\n")

  while True:
    query = input("Search > ").strip()
    if query.lower() in ("exit", "quit", "q"):
      break
    if not query:
      continue

    results = engine.search(query)

    if not results:
      print("No matching documents found.\n")
      continue

    print(f"\nTop results for '{query}':")
    print("-" * 50)
    for rank, (doc_id, score) in enumerate(results, start=1):
      doc = engine.documents[doc_id]
      percentage = round(score * 100, 1)
      print(f"[{rank}] {doc['title']} (Relevance Score: {percentage}%)")
      print(f"    Snippet: {doc['content'][:110]}...")
      print("-" * 50)
    print()
