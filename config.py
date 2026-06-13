"""
=============================================================
AFRICAN AI v4.1 — CONFIGURATION
By Anaase-Tech Ltd | CTO: Claude | CEO: Eddy B3rima

All constants in one place. Edit here, applies everywhere.
=============================================================
"""

import os

# ── API Keys ──────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")   # Set in HF Space Secrets

# ── ChromaDB ──────────────────────────────────────────────
CHROMA_DIR  = "african_chroma_db"                    # Persistent vector DB folder
COLLECTION  = "african_knowledge"                    # ChromaDB collection name
READY_FILE  = os.path.join(CHROMA_DIR, "READY")     # Flag — prevents index rebuild on boot

# ── Embedding Model ───────────────────────────────────────
EMBED_MODEL = "intfloat/multilingual-e5-base"        # v4.1 multilingual — handles Twi, Swahili, Yoruba, Hausa

# ── LLM ───────────────────────────────────────────────────
LLM_MODEL   = "llama-3.1-8b-instant"                # Groq model — fast + stable
MAX_TOKENS  = 500                                    # Keep responses focused
TEMPERATURE = 0.7                                    # Balanced creativity

# ── Branding ──────────────────────────────────────────────
LOGO_URL = "https://raw.githubusercontent.com/Anaase-Tech/African-AI/main/logo.png"
VERSION  = "v4.1"

# ── Create folders ────────────────────────────────────────
os.makedirs(CHROMA_DIR, exist_ok=True)
