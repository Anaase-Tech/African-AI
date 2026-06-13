"""
=============================================================
AFRICAN AI v4.1 — CHAT RESPONSE PIPELINE
By Anaase-Tech Ltd | CTO: Claude | CEO: Eddy B3rima

The respond() generator is the core chat pipeline:
1. Sanitise input (guards against None crash)
2. Skip local knowledge for historical figures
3. Check local dictionary OR run hybrid retrieval
4. Detect language (strict v4.1 mode)
5. Build Groq message list with language lock
6. Stream response token by token
7. Append sources
=============================================================
"""

from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL, MAX_TOKENS, TEMPERATURE
from knowledge import check_local_terms
from language import detect_language
from retrieval import hybrid_retrieve

# ─────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are African AI — an intelligent assistant built specifically for and by Africans.

Your knowledge spans African languages, history, philosophy, culture, music, food, fashion, spirituality, governance, agriculture, and modern innovation.

You were created by Y.A B3rima (Anaase-Tech Ltd, Ghana, West Africa).

LANGUAGE RULE — CRITICAL:
Always respond in English unless the user explicitly requests another language
(e.g. "answer in Twi", "respond in Swahili") or their message is clearly written
in that language.

Do NOT switch to Twi, Swahili, Yoruba, Hausa, or any other language simply because:
- The topic is African (Ghana, Kenya, Nigeria, Tanzania, etc.)
- The context contains African words (Akan, Ashanti, Ubuntu, Sankofa, etc.)
- A person's name sounds African (Nkrumah, Asantewaa, Mandela, etc.)
- The question mentions a language (e.g. "tell me about Twi" → answer IN ENGLISH about Twi)

STRICT RULES:
- Use ONLY information from the CONTEXT provided below
- NEVER invent connections between unrelated African cultures, languages, or topics
- If LOCAL KNOWLEDGE is in the context, use it as the primary and definitive answer
- If context does not match the question, say honestly:
  "I don't have precise information on that yet — African AI is still growing.
   Help us improve: https://docs.google.com/forms/d/e/1FAIpQLSedb5p6UaqOFYjnpNV1k2e4p8_WQoEEZB94imexe72MjKJUQg/viewform"
- Do NOT fabricate local words, proverbs, or cultural facts

Your personality:
- Warm, proud, deeply knowledgeable about Africa
- Culturally respectful and authentic
- NOT ChatGPT, Claude, or any other AI — you are African AI

Speak with African pride — but always with accuracy. 🌍"""


# ─────────────────────────────────────────────────────────
# HISTORICAL FIGURES
# Local dictionary skipped for these — Wikipedia gives richer,
# language-safe answers and avoids Twi-drift on English queries
# ─────────────────────────────────────────────────────────
HISTORICAL_FIGURES = {
    "yaa asantewaa", "asantewaa", "kwame nkrumah", "nkrumah",
    "thomas sankara", "sankara", "nelson mandela", "mandela",
    "patrice lumumba", "lumumba", "julius nyerere", "nyerere",
    "haile selassie", "selassie", "mansa musa", "shaka zulu",
    "wangari maathai", "maathai", "steve biko", "biko",
    "miriam makeba", "makeba", "marcus garvey", "garvey",
    "chinua achebe", "achebe", "fela kuti", "fela",
}


def respond(message: str, history: list, collection, bm25_index, bm25_docs, bm25_metas):
    """
    Main response generator — yields streaming chunks to Gradio.

    Parameters:
        message     — user input string
        history     — Gradio chat history list
        collection  — ChromaDB collection
        bm25_index  — BM25Okapi index
        bm25_docs   — all documents from ChromaDB
        bm25_metas  — all metadatas from ChromaDB
    """

    # ── Step 0: Input sanitisation ────────────────────
    # Guards against NoneType crash when Gradio passes message=None
    message = str(message or "").strip()

    if not message:
        yield "", history
        return

    if len(message) > 2000:
        yield "", history + [
            {"role": "user",      "content": message},
            {"role": "assistant", "content": "Please keep your question under 2000 characters."},
        ]
        return

    # ── Step 1: Local dictionary lookup ──────────────
    # Historical figures skip local dict — use Wikipedia instead
    query_lower   = message.lower()
    is_historical = any(fig in query_lower for fig in HISTORICAL_FIGURES)

    local_hit = None if is_historical else check_local_terms(message)

    if local_hit:
        context = local_hit
        sources = []
        print(f"[LOCAL] Hit: {local_hit[:60]}")
    else:
        context, sources = hybrid_retrieve(
            message, collection, bm25_index, bm25_docs, bm25_metas
        )

    # ── Step 2: Detect language ───────────────────────
    lang = detect_language(message)
    print(f"[LANG] detected='{lang}' message='{message[:40]}'")

    # ── Step 3: Build Groq message list ───────────────
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Per-turn language lock — reinforces SYSTEM_PROMPT
    if lang == "english":
        messages.append({
            "role": "system",
            "content": (
                "LANGUAGE LOCK: This user's message is in English. "
                "You MUST respond in English only. "
                "Do NOT use Twi, Swahili, Yoruba, Hausa, or any other language "
                "regardless of what words appear in the context."
            ),
        })
    else:
        messages.append({
            "role": "system",
            "content": (
                f"LANGUAGE LOCK: The user has requested {lang.upper()}. "
                f"Respond in {lang.upper()} only."
            ),
        })

    # Last 2 turns of history — role+content only (Groq rejects extra fields)
    for turn in history[-2:]:
        if isinstance(turn, dict):
            role    = turn.get("role", "")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": str(content)})
        elif isinstance(turn, (list, tuple)) and len(turn) == 2:
            if turn[0]: messages.append({"role": "user",      "content": str(turn[0])})
            if turn[1]: messages.append({"role": "assistant", "content": str(turn[1])})

    # Safe context — never None or empty
    safe_context = str(context or "No specific context retrieved.").strip() or "No specific context retrieved."

    messages.append({
        "role": "user",
        "content": (
            f"Context from African knowledge base:\n{safe_context}\n\n"
            f"---\n\n"
            f"Question: {message}\n\n"
            f"Answer grounded in the African knowledge above."
        ),
    })

    # ── Step 4: Stream from Groq ──────────────────────
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)  # Fresh client per request

        stream = groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            stream=True,
        )

        partial     = ""
        new_history = list(history) + [
            {"role": "user",      "content": str(message)},
            {"role": "assistant", "content": ""},
        ]

        for chunk in stream:
            try:
                content = chunk.choices[0].delta.content
                if content and isinstance(content, str):
                    partial += content
                    new_history[-1]["content"] = partial
                    yield "", new_history
            except Exception:
                continue

        if sources:
            src = ", ".join(str(s) for s in sources[:3])
            new_history[-1]["content"] = partial + f"\n\n*📚 Sources: {src}*"
            yield "", new_history

    except Exception as e:
        print(f"[ERROR] Groq: {e}")
        yield "", list(history) + [
            {"role": "user",      "content": str(message)},
            {"role": "assistant", "content": "African AI is reconnecting. Please try again."},
        ]
