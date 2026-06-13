# African AI v4.1 🌍
**Built by Africans · Powered by African Knowledge**
By Anaase-Tech | Founder/CEO: Y.A B3rima

## What is African AI?
A RAG (Retrieval-Augmented Generation) chatbot built specifically for African knowledge — languages, history, philosophy, culture, music, food, leaders, spirituality, and more.

🔗 **Live Demo:** https://b3rima1-african-ai.hf.space

---

## Project Structure
```
african-ai/
├── app.py           # Gradio UI + launch (entry point)
├── config.py        # API keys, paths, model names
├── knowledge.py     # LOCAL_TERMS, PROVERBS, DATASET_TOPICS
├── language.py      # detect_language(), strict v4.1 mode
├── retrieval.py     # Wikipedia fetch, ChromaDB, BM25, hybrid search
├── respond.py       # respond() — the full chat pipeline
└── requirements.txt # Dependencies
```

## Architecture
```
User Query
    ↓
Local Dictionary (56 African terms) — instant exact match
    ↓ (if no match)
Hybrid Retrieval
    ├── BM25 keyword search (40%) — exact names, rare terms
    └── Vector search (60%) — semantic meaning
         ↓
    Reciprocal Rank Fusion — merges both rankings
         ↓
    Diversity filter — no duplicate titles
         ↓
Groq LLaMA 3.1 (streaming) — grounded answer
    ↓
Response with sources
```

## Key Features
- **4,251 knowledge chunks** across 14 African categories
- **Multilingual embeddings** — `intfloat/multilingual-e5-base` handles Twi, Swahili, Yoruba, Hausa, Zulu
- **Strict language detection** — defaults to English, only switches on explicit request
- **Historical figures** skip local dict — use rich Wikipedia chunks instead
- **Exponential backoff** on Wikipedia fetches — near-zero skipped topics
- **Mobile-first UI** — designed for Samsung A04e, Pan-African gold/green theme

## v4.1 Fixes
- Language drift fixed — "Tell me about Kenya" no longer triggers Swahili mode
- NoneType crash fixed — `message=None` safely handled
- Fusion key collision fixed — MD5 hash replaces `doc[:120]`
- Diversity filter — same title can't fill all 3 result slots
- Exponential backoff — Wikipedia rate limits handled gracefully

## Setup (HuggingFace Spaces)
1. Upload all files to your HF Space
2. Set `GROQ_API_KEY` in Space Secrets
3. The index builds automatically on first boot (~5 mins)
4. READY flag prevents rebuild on subsequent boots

## Community Contributions
Help African AI grow — submit words, proverbs, and cultural knowledge:
👉 https://docs.google.com/forms/d/e/1FAIpQLSedb5p6UaqOFYjnpNV1k2e4p8_WQoEEZB94imexe72MjKJUQg/viewform

---
Built in Ghana 🇬🇭 | Akosombo, Eastern Region
