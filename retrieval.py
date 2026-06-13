"""
=============================================================
AFRICAN AI v4.1 — RETRIEVAL PIPELINE
By Anaase-Tech Ltd | CTO: Claude | CEO: Eddy B3rima

Contains:
- fetch_wikipedia(): Full article fetch with exponential backoff
- build_index() / load_index(): ChromaDB vector index management
- build_bm25_index(): BM25 keyword index
- hybrid_retrieve(): BM25 + Vector search with RRF fusion
- detect_category(): Query-to-category mapping

Retrieval strategy:
  BM25 (40%) — exact African names, rare terms
  Vector (60%) — semantic meaning, related concepts
  RRF — merges both into one ranked result list
  Diversity filter — prevents same title filling all slots
=============================================================
"""

import re
import time
import hashlib
import requests
import numpy as np
from datetime import datetime, timezone
from rank_bm25 import BM25Okapi

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DIR, COLLECTION, READY_FILE, EMBED_MODEL
from knowledge import LOCAL_TERMS, PROVERBS, DATASET_TOPICS


# ─────────────────────────────────────────────────────────
# TEXT HELPERS
# ─────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Remove Wikipedia artifacts, citations, extra whitespace."""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[edit\]', '', text, re.IGNORECASE)
    text = re.sub(r'==.*?==', '', text)
    text = re.sub(r'This article.*', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.replace('\xa0', ' ').strip()


def chunk_text(text: str, chunk_size: int = 700) -> list:
    """
    Sentence-aware chunking — splits on sentence boundaries.
    Preserves meaning better than naive character splitting.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
            current += " " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


# ─────────────────────────────────────────────────────────
# WIKIPEDIA FETCHER
# Exponential backoff + 429 handling + summary fallback
# ─────────────────────────────────────────────────────────

def fetch_wikipedia(title: str):
    """
    Fetch Wikipedia full article via MediaWiki API.
    Falls back to REST summary if full fetch fails.

    Improvements over v4.0:
    - Exponential backoff: 1s → 2s → 4s → 8s
    - Explicit 429 rate-limit detection
    - Summary threshold lowered to 50 chars (was 200)
    - 4 main attempts + 3 summary attempts (was 3+2)
    """
    clean_title = title.replace(" ", "_")
    api_url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=query&prop=extracts&explaintext=1&exsectionformat=plain"
        f"&titles={clean_title}&format=json&redirects=1"
    )

    # Method 1: Full article
    for attempt in range(4):
        wait = 2 ** attempt
        try:
            r = requests.get(api_url, headers={"User-Agent": "AfricanAI/4.1"}, timeout=30)
            if r.status_code == 429:
                print(f"[WIKI] Rate limited on '{title}' — waiting {wait*2}s")
                time.sleep(wait * 2)
                continue
            if r.status_code == 200:
                pages = r.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    if str(page.get("pageid", -1)) == "-1":
                        break
                    text = page.get("extract", "")
                    if len(text) > 200:
                        return clean_text(text)
            else:
                print(f"[WIKI] API HTTP {r.status_code} for '{title}'")
        except Exception as e:
            print(f"[WIKI] API attempt {attempt+1} for '{title}': {e}")
        time.sleep(wait)

    # Method 2: REST summary fallback
    for attempt in range(3):
        wait = 2 ** attempt
        try:
            r = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_title}",
                headers={"User-Agent": "AfricanAI/4.1"}, timeout=25,
            )
            if r.status_code == 429:
                print(f"[WIKI] Summary rate limited '{title}' — waiting {wait*2}s")
                time.sleep(wait * 2)
                continue
            if r.status_code == 200:
                text = r.json().get("extract", "")
                if len(text) > 50:
                    print(f"[WIKI] Summary fallback used for '{title}'")
                    return clean_text(text)
            else:
                print(f"[WIKI] Summary HTTP {r.status_code} for '{title}'")
        except Exception as e:
            print(f"[WIKI] Summary attempt {attempt+1} for '{title}': {e}")
        time.sleep(wait)

    return None


# ─────────────────────────────────────────────────────────
# VECTOR INDEX
# ChromaDB persistent index — builds once, loads on boot
# READY_FILE flag prevents rebuild on every restart
# ─────────────────────────────────────────────────────────

def build_index():
    """
    Build full ChromaDB vector index from:
    1. Hand-curated proverbs
    2. Local terms dictionary
    3. Wikipedia articles (full text via MediaWiki API)
    Writes READY flag when complete.
    """
    print("=" * 50)
    print("AFRICAN AI — Building Knowledge Index")
    print("=" * 50)
    docs = []
    now  = datetime.now(timezone.utc).isoformat()

    # Proverbs
    print(f"\n[INDEX] Adding {len(PROVERBS)} proverbs...")
    for i, p in enumerate(PROVERBS):
        text = (
            f"African Proverb ({p['language']}, {p['country']}):\n"
            f"\"{p['proverb']}\"\n"
            f"Meaning: {p['meaning']}\n"
            f"Philosophy: {p['philosophy']}"
        )
        docs.append({"id": f"proverb_{i:03d}", "text": text,
                     "category": "proverbs", "title": p["proverb"][:60],
                     "source": "Anaase-Tech Curated", "ts": now})

    # Local terms
    print(f"[INDEX] Adding {len(LOCAL_TERMS)} local terms...")
    for term, info in LOCAL_TERMS.items():
        text = (
            f"Local African Term: {term.upper()} "
            f"({info['language']}, {info['country']})\n"
            f"Meaning: {info['meaning']}"
        )
        docs.append({"id": f"local_{term.replace(' ', '_')}", "text": text,
                     "category": "languages", "title": term,
                     "source": "Anaase-Tech Local Dictionary", "ts": now})

    # Wikipedia
    for category, topics in DATASET_TOPICS.items():
        print(f"[INDEX] Fetching {category} ({len(topics)} topics)...")
        for topic in topics:
            content = fetch_wikipedia(topic)
            if content:
                chunks = chunk_text(content)
                for i, chunk in enumerate(chunks):
                    docs.append({"id": f"{category}_{topic}_{i}", "text": chunk,
                                 "category": category, "title": topic.replace("_", " "),
                                 "source": "Wikipedia", "ts": now})
                print(f"  ✓ {topic} → {len(chunks)} chunks")
            else:
                print(f"  ✗ {topic} — skipped")
            time.sleep(1.5)  # Respectful rate limiting

    # Write to ChromaDB
    print(f"\n[INDEX] Indexing {len(docs)} total chunks...")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(name=COLLECTION, embedding_function=embed_fn)

    for i in range(0, len(docs), 100):
        batch = docs[i:i + 100]
        col.add(
            ids       = [d["id"]   for d in batch],
            documents = [d["text"] for d in batch],
            metadatas = [{"category": d["category"], "title": d["title"],
                          "source": d["source"], "ts": d["ts"]} for d in batch],
        )

    with open(READY_FILE, "w") as f:
        f.write("ready")

    print(f"\n[INDEX] Complete — {col.count()} chunks indexed.")
    print("=" * 50)
    return col


def load_index():
    """Load existing ChromaDB index from disk."""
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col    = client.get_collection(name=COLLECTION, embedding_function=embed_fn)
    print(f"[INDEX] Loaded — {col.count()} chunks.")
    return col


# ─────────────────────────────────────────────────────────
# BM25 KEYWORD INDEX
# ─────────────────────────────────────────────────────────

def tokenize_for_bm25(text: str) -> list:
    """Lowercase + remove punctuation + split."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [t for t in text.split() if len(t) > 1]


def build_bm25_index(col):
    """Build BM25 keyword index from all ChromaDB documents."""
    print("[BM25] Building keyword index...")
    results       = col.get(include=["documents", "metadatas"])
    all_docs      = results["documents"]
    all_metadatas = results["metadatas"]
    tokenized     = [tokenize_for_bm25(doc) for doc in all_docs]
    bm25          = BM25Okapi(tokenized)
    print(f"[BM25] Ready — {len(all_docs)} documents.")
    return bm25, all_docs, all_metadatas


# ─────────────────────────────────────────────────────────
# CATEGORY DETECTION
# Maps query keywords → ChromaDB category filter
# ─────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "languages":    ["language","pidgin","twi","yoruba","hausa","igbo","swahili",
                     "amharic","zulu","wolof","somali","oromo","lingala","dialect",
                     "speak","word","phrase","translate","grammar","meaning of","what does","what is"],
    "history":      ["history","empire","kingdom","war","colonialism","independence",
                     "ancient","dynasty","slave","trade","scramble","revolt","founded"],
    "leaders":      ["nkrumah","mandela","sankara","lumumba","selassie","musa",
                     "nyerere","garvey","biko","makeba","asantewaa","leader",
                     "president","freedom fighter","revolutionary","who was","who is"],
    "philosophy":   ["philosophy","ubuntu","ujamaa","maat","sankofa","wisdom",
                     "proverb","ethics","belief","principle","meaning","teach"],
    "music":        ["music","afrobeats","highlife","amapiano","kwaito","fela",
                     "makossa","hiplife","soukous","song","beat","genre","rhythm","dance"],
    "food":         ["food","eat","dish","jollof","fufu","ugali","injera","suya",
                     "waakye","kenkey","cook","recipe","cuisine","meal"],
    "culture":      ["culture","tradition","custom","ceremony","ritual","tribe",
                     "clan","community","akan","zulu","maasai","igbo","hausa"],
    "festivals":    ["festival","celebration","homowo","odwira","timkat",
                     "gerewol","durbar","aboakyir","ceremony","annual"],
    "fashion":      ["fashion","cloth","kente","ankara","dashiki","wear",
                     "dress","textile","boubou","style","attire","clothing"],
    "spirituality": ["religion","spiritual","god","deity","ancestor","prayer",
                     "belief","faith","shrine","sacred","worship"],
    "modern_africa":["startup","fintech","mpesa","nollywood","flutterwave",
                     "technology","innovation","app","mobile money","safaricom","tech"],
    "governance":   ["government","union","ecowas","policy","law","treaty",
                     "african union","politics","constitution","governance"],
    "agriculture":  ["farm","crop","cassava","cocoa","maize","yam","sorghum",
                     "millet","harvest","agriculture","food production","plant"],
    "proverbs":     ["proverb","saying","wisdom","adage","quote","teach","share a"],
}


def detect_category(query: str):
    """Detect most relevant category from query keywords."""
    q = f" {query.lower()} "
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if f" {kw} " in q)
        if score > 0:
            scores[cat] = score
    return max(scores, key=scores.get) if scores else None


# ─────────────────────────────────────────────────────────
# HYBRID RETRIEVAL — BM25 + VECTOR + RRF
# ─────────────────────────────────────────────────────────

def _doc_key(text: str) -> str:
    """
    Stable collision-free key using MD5 hash.
    Replaces old doc[:120] slice which could silently merge
    two different chunks sharing the same first 120 chars.
    """
    return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()


def hybrid_retrieve(query: str, collection, bm25_index, bm25_docs, bm25_metas, n: int = 3):
    """
    Hybrid BM25 + Vector retrieval with Reciprocal Rank Fusion.

    BM25 (40%) — catches exact African names, terms, rare words
    Vector (60%) — catches semantic meaning and related concepts
    RRF — merges both rankings into one best result list
    Diversity filter — prevents same title filling all slots
    Twi-char filter — removes heavy African-script chunks from English context
    """
    category = detect_category(query)
    fetch_n  = n * 4
    k        = 60
    BM25_W   = 0.4
    VEC_W    = 0.6

    print(f"[HYBRID] query='{query[:50]}' category='{category}'")

    # BM25 keyword search
    q_tokens    = tokenize_for_bm25(query)
    bm25_scores = bm25_index.get_scores(q_tokens)
    top_indices = np.argsort(bm25_scores)[::-1][:fetch_n]

    bm25_hits = {}
    for rank, idx in enumerate(top_indices):
        if bm25_scores[idx] > 0:
            doc = bm25_docs[idx]
            key = _doc_key(doc)
            bm25_hits[key] = {"rank": rank, "score": bm25_scores[idx],
                               "doc": doc, "meta": bm25_metas[idx]}
    print(f"[HYBRID] BM25: {len(bm25_hits)} candidates")

    # Vector semantic search
    vec_kwargs = {"query_texts": [query], "n_results": fetch_n,
                  "include": ["documents", "metadatas", "distances"]}
    if category:
        try:
            vec_kwargs["where"] = {"category": category}
            vec_res = collection.query(**vec_kwargs)
        except Exception:
            del vec_kwargs["where"]
            vec_res = collection.query(**vec_kwargs)
    else:
        vec_res = collection.query(**vec_kwargs)

    vec_hits = {}
    for rank, (doc, meta, dist) in enumerate(zip(
        vec_res["documents"][0], vec_res["metadatas"][0], vec_res["distances"][0]
    )):
        print(f"[HYBRID]   vec rank {rank}: dist={dist:.3f} '{meta['title']}'")
        key = _doc_key(doc)
        vec_hits[key] = {"rank": rank, "dist": dist, "doc": doc, "meta": meta}

    # Reciprocal Rank Fusion
    fusion = {}
    for key, item in bm25_hits.items():
        if key not in fusion:
            fusion[key] = {"score": 0, "doc": item["doc"], "meta": item["meta"]}
        fusion[key]["score"] += BM25_W * (1 / (k + item["rank"]))

    for key, item in vec_hits.items():
        if key not in fusion:
            fusion[key] = {"score": 0, "doc": item["doc"], "meta": item["meta"]}
        if item["dist"] < 1.5:
            fusion[key]["score"] += VEC_W * (1 / (k + item["rank"]))

    ranked = sorted(fusion.values(), key=lambda x: x["score"], reverse=True)

    # Build context with diversity + Twi-char filters
    parts, sources, seen_titles = [], set(), set()
    for item in ranked:
        if len(parts) >= n:
            break
        if item["score"] <= 0:
            continue
        m     = item["meta"]
        title = m["title"]
        if title in seen_titles:
            continue
        twi_chars = item["doc"].count("ɛ") + item["doc"].count("ɔ")
        if twi_chars > 8:
            print(f"[HYBRID]   ⚠ Skipping Twi-heavy chunk from '{title}'")
            continue
        seen_titles.add(title)
        parts.append(f"[{m['category'].upper()} — {title}]\n{item['doc']}")
        sources.add(title)
        print(f"[HYBRID]   ✓ score={item['score']:.4f} '{title}'")

    return "\n\n---\n\n".join(parts), list(sources)
