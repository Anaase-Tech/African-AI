"""
=============================================================
AFRICAN AI v4.1 — LANGUAGE DETECTION (STRICT MODE)
By Anaase-Tech Ltd | CTO: Claude | CEO: Eddy B3rima

v4.1 Root cause fix:
  Old detector triggered on context words, not just user message.
  "Tell me about Kenya" → context had Swahili → model drifted.

v4.1 Rule: DEFAULT IS ENGLISH.
  Language only switches when:
  (a) User explicitly requests: "answer in twi", "respond in swahili"
  (b) User's OWN message contains 3+ matching African language words
=============================================================
"""

# ─────────────────────────────────────────────────────────
# LANGUAGE WORD LISTS
# Used for passive detection on user message ONLY
# ─────────────────────────────────────────────────────────
TWI_WORDS     = ["akwaaba", "medaase", "ete sen", "meda wo ase", "wo ho te sen", "yɛfrɛ", "mepa wo kyɛw"]
SWAHILI_WORDS = ["habari", "karibu", "jambo", "sijambo", "nzuri", "sawa", "asante sana", "pole pole"]
YORUBA_WORDS  = ["bawo ni", "eku ile", "e kaabo", "jowo", "ese pupo", "pele o"]
HAUSA_WORDS   = ["sannu da zuwa", "yauwa", "nagode", "ina kwana", "lafiya lau", "ka zo nan"]

# Explicit request phrases — highest priority trigger
_LANG_REQUESTS = {
    "twi":     ["answer in twi", "respond in twi", "speak twi", "translate to twi",
                "reply in twi", "write in twi"],
    "swahili": ["answer in swahili", "respond in swahili", "speak swahili",
                "translate to swahili", "reply in swahili"],
    "yoruba":  ["answer in yoruba", "respond in yoruba", "translate to yoruba",
                "reply in yoruba"],
    "hausa":   ["answer in hausa", "respond in hausa", "translate to hausa",
                "reply in hausa"],
}

# Word lists mapped by language for score-based detection
_LANG_WORDS = {
    "twi":     TWI_WORDS,
    "swahili": SWAHILI_WORDS,
    "yoruba":  YORUBA_WORDS,
    "hausa":   HAUSA_WORDS,
}


def user_requested_language(text: str):
    """
    Check if user explicitly asked for a specific language.
    Returns language string or None.
    This is the PRIMARY trigger — most reliable, highest priority.

    Examples:
      "answer in twi"       → "twi"
      "translate to swahili" → "swahili"
      "tell me about Ghana"  → None
    """
    t = text.lower().strip()
    for lang, phrases in _LANG_REQUESTS.items():
        if any(p in t for p in phrases):
            return lang
    return None


def detect_language(text: str) -> str:
    """
    v4.1 STRICT language detection.
    Default is ALWAYS English.

    Switching only happens when:
    1. User explicitly requests the language (user_requested_language)
    2. User's own message contains 3+ matching words

    Threshold = 3 (raised from earlier versions) to prevent
    single-word false positives like "asante" triggering Swahili mode.

    Examples:
      "Tell me about Kenya"    → "english"  (topic ≠ language)
      "Who was Yaa Asantewaa?" → "english"  (name ≠ language)
      "Akwaaba medaase yɛfrɛ"  → "twi"      (3 Twi words)
      "Answer in Twi please"   → "twi"      (explicit request)
    """
    # Priority 1: explicit request — immediate return
    requested = user_requested_language(text)
    if requested:
        return requested

    # Priority 2: passive scoring on user message only
    t      = text.lower().strip()
    scores = {lang: sum(1 for w in wlist if w in t)
              for lang, wlist in _LANG_WORDS.items()}

    best_lang  = max(scores, key=scores.get)
    best_score = scores[best_lang]

    if best_score >= 3:
        return best_lang

    return "english"  # DEFAULT — never changes without strong evidence
