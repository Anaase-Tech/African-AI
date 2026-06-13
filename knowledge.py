"""
=============================================================
AFRICAN AI v4.1 — KNOWLEDGE BASE
By Anaase-Tech Ltd | CTO: Claude | CEO: Eddy B3rima

Contains:
- LOCAL_TERMS: African words/phrases dictionary (checked before RAG)
- PROVERBS: Hand-curated African proverbs
- DATASET_TOPICS: Wikipedia topics to fetch on first boot
- check_local_terms(): Fast dictionary lookup function
=============================================================
"""

import re

# ─────────────────────────────────────────────────────────
# LOCAL AFRICAN TERMS DICTIONARY
# Checked BEFORE vector retrieval — guarantees accuracy on
# culturally specific words that embeddings don't handle well
# ─────────────────────────────────────────────────────────
LOCAL_TERMS = {
    # ── Ghanaian / Twi (Akan) ──
    "akonta":    {"language": "Twi (Akan)", "meaning": "brother-in-law", "country": "Ghana"},
    "maame":     {"language": "Twi (Akan)", "meaning": "mother or woman", "country": "Ghana"},
    "papa":      {"language": "Twi (Akan)", "meaning": "father", "country": "Ghana"},
    "akwaaba":   {"language": "Twi (Akan)", "meaning": "welcome", "country": "Ghana"},
    "medaase":   {"language": "Twi (Akan)", "meaning": "thank you", "country": "Ghana"},
    "ete sen":   {"language": "Twi (Akan)", "meaning": "how are you", "country": "Ghana"},
    "eye":       {"language": "Twi (Akan)", "meaning": "it is well / fine", "country": "Ghana"},
    "obroni":    {"language": "Twi (Akan)", "meaning": "foreigner / white person", "country": "Ghana"},
    "abrantie":  {"language": "Twi (Akan)", "meaning": "gentleman / young man", "country": "Ghana"},
    "obaa":      {"language": "Twi (Akan)", "meaning": "woman / lady", "country": "Ghana"},
    "obrempon":  {"language": "Twi (Akan)", "meaning": "great person / chief / person of high status", "country": "Ghana"},
    "sankofa":   {"language": "Twi (Akan)", "meaning": "go back and fetch it — learn from the past", "country": "Ghana"},
    "adinkra":   {"language": "Twi (Akan)", "meaning": "Akan symbols representing concepts and aphorisms", "country": "Ghana"},
    "kente":     {"language": "Twi (Akan)", "meaning": "hand-woven cloth of the Akan people", "country": "Ghana"},
    "damirifa":  {"language": "Twi (Akan)", "meaning": "condolences / rest in peace", "country": "Ghana"},
    "nkrumah":   {"language": "Akan", "meaning": "ninth-born child", "country": "Ghana"},

    # ── Ghanaian everyday words ──
    "kelewele":  {"language": "Ghanaian", "meaning": "spiced fried plantain snack", "country": "Ghana"},
    "trotro":    {"language": "Ghanaian", "meaning": "shared minibus public transport", "country": "Ghana"},
    "chale":     {"language": "Ghanaian Pidgin", "meaning": "friend / buddy (casual address)", "country": "Ghana"},
    "waakye":    {"language": "Hausa/Ghanaian", "meaning": "rice and beans dish popular in Ghana", "country": "Ghana"},
    "fufu":      {"language": "Twi (Akan)", "meaning": "pounded cassava/plantain staple food", "country": "Ghana/West Africa"},

    # ── Swahili (East Africa) ──
    "jamaa":     {"language": "Swahili", "meaning": "community / family / people", "country": "East Africa"},
    "pole":      {"language": "Swahili", "meaning": "sorry / slowly / take it easy", "country": "East Africa"},
    "asante":    {"language": "Swahili", "meaning": "thank you", "country": "East Africa"},
    "karibu":    {"language": "Swahili", "meaning": "welcome / you are welcome", "country": "East Africa"},
    "harambee":  {"language": "Swahili", "meaning": "let us all pull together — spirit of community", "country": "Kenya"},

    # ── Zulu / Southern Africa ──
    "ubuntu":    {"language": "Zulu/Nguni", "meaning": "I am because we are — human connectedness", "country": "South Africa"},
    "sawubona":  {"language": "Zulu", "meaning": "I see you (deep greeting acknowledging a person's humanity)", "country": "South Africa"},

    # ── Pan-African / West Africa ──
    "jollof":    {"language": "Wolof", "meaning": "one-pot rice dish beloved across West Africa", "country": "West Africa"},
    "dashiki":   {"language": "Yoruba/West African", "meaning": "colorful African shirt/garment", "country": "West Africa"},

    # ── Key African figures (hardcoded for reliability) ──
    "yaa asantewaa": {
        "language": "Historical figure",
        "meaning": (
            "Yaa Asantewaa (c.1840-1921) was the Queen Mother of Ejisu in the Ashanti Empire, Ghana. "
            "She led the War of the Golden Stool (Anglo-Ashanti War of 1900) against British colonialism — "
            "the last major Ashanti resistance. When male chiefs hesitated, she famously declared: "
            "'If you the men of Ashanti will not go forward, then we will. We the women will.' "
            "She was captured and exiled to the Seychelles where she died. "
            "She is one of Africa's greatest female warriors and freedom fighters."
        ),
        "country": "Ghana"
    },
    "asantewaa": {
        "language": "Historical figure",
        "meaning": (
            "Yaa Asantewaa was the Queen Mother of Ejisu who led the War of the Golden Stool in 1900 "
            "against British colonialism in Ghana. A symbol of African resistance and women's courage."
        ),
        "country": "Ghana"
    },

    # ── More Twi phrases ──
    "wo ho ye":      {"language": "Twi (Akan)", "meaning": "you are fine / you are well (response to ete sen)", "country": "Ghana"},
    "wo ho te sen":  {"language": "Twi (Akan)", "meaning": "how are you (formal)", "country": "Ghana"},
    "me ho ye":      {"language": "Twi (Akan)", "meaning": "I am fine / I am well", "country": "Ghana"},
    "asem aba":      {"language": "Twi (Akan)", "meaning": "something has happened / there is news / there is a matter", "country": "Ghana"},
    "asem":          {"language": "Twi (Akan)", "meaning": "matter / issue / word / case", "country": "Ghana"},
    "yoo":           {"language": "Twi (Akan)", "meaning": "okay / alright / yes (casual agreement)", "country": "Ghana"},
    "yɛ":            {"language": "Twi (Akan)", "meaning": "we / it is (verb to be)", "country": "Ghana"},
    "ɛyɛ":           {"language": "Twi (Akan)", "meaning": "it is good / it is fine", "country": "Ghana"},
    "daabi":         {"language": "Twi (Akan)", "meaning": "no", "country": "Ghana"},
    "aane":          {"language": "Twi (Akan)", "meaning": "yes", "country": "Ghana"},
    "wo firi he":    {"language": "Twi (Akan)", "meaning": "where are you from", "country": "Ghana"},
    "me firi ghana": {"language": "Twi (Akan)", "meaning": "I am from Ghana", "country": "Ghana"},
    "dabi dabi":     {"language": "Twi (Akan)", "meaning": "sometimes", "country": "Ghana"},
    "wiase":         {"language": "Twi (Akan)", "meaning": "world / earth", "country": "Ghana"},
    "onipa":         {"language": "Twi (Akan)", "meaning": "person / human being", "country": "Ghana"},
    "onyame":        {"language": "Twi (Akan)", "meaning": "God (the Supreme Being in Akan belief)", "country": "Ghana"},
    "nyame":         {"language": "Twi (Akan)", "meaning": "God / the Supreme Being", "country": "Ghana"},
    "obiara":        {"language": "Twi (Akan)", "meaning": "everyone / everybody", "country": "Ghana"},
    "wɔ":            {"language": "Twi (Akan)", "meaning": "they / there is", "country": "Ghana"},
    "efie":          {"language": "Twi (Akan)", "meaning": "home / house", "country": "Ghana"},
    "kɔ":            {"language": "Twi (Akan)", "meaning": "go", "country": "Ghana"},
    "ba":            {"language": "Twi (Akan)", "meaning": "come / child", "country": "Ghana"},
    "abofra":        {"language": "Twi (Akan)", "meaning": "child / young person", "country": "Ghana"},
    "panyin":        {"language": "Twi (Akan)", "meaning": "elder / older person", "country": "Ghana"},
}


def check_local_terms(query: str):
    """
    Check if the query contains a known local African term.
    Uses regex word boundaries — 'papa' won't match 'papaya'.
    Returns formatted string if found, or None.
    """
    q = query.lower()
    for term, info in LOCAL_TERMS.items():
        if re.search(rf"\b{re.escape(term)}\b", q):
            return (
                f"LOCAL KNOWLEDGE — {term.upper()} "
                f"({info['language']}, {info['country']}):\n"
                f"Meaning: {info['meaning']}"
            )
    return None


# ─────────────────────────────────────────────────────────
# HAND-CURATED PROVERBS
# Wikipedia can't give you these — curated by Anaase-Tech
# ─────────────────────────────────────────────────────────
PROVERBS = [
    {"proverb": "Ubuntu ngumuntu ngabantu",
     "language": "Zulu", "country": "South Africa",
     "meaning": "A person is a person through other people.",
     "philosophy": "Communal identity — we exist in relationship."},

    {"proverb": "Obi nnim obrempon ahyease",
     "language": "Twi (Akan)", "country": "Ghana",
     "meaning": "No one knows the beginning of a great person.",
     "philosophy": "Humble beginnings and patience."},

    {"proverb": "Haraka haraka haina baraka",
     "language": "Swahili", "country": "East Africa",
     "meaning": "Hurry hurry has no blessings.",
     "philosophy": "Patience produces better outcomes."},

    {"proverb": "Mtu ni watu",
     "language": "Swahili", "country": "East Africa",
     "meaning": "A person is people.",
     "philosophy": "Communal African identity."},

    {"proverb": "Nit nitay garabam",
     "language": "Wolof", "country": "Senegal",
     "meaning": "A person is the remedy of another person.",
     "philosophy": "Community is medicine."},

    {"proverb": "If you want to go fast, go alone. If you want to go far, go together.",
     "language": "Pan-African", "country": "Pan-Africa",
     "meaning": "Collective effort achieves more than individual speed.",
     "philosophy": "Communalism over individualism."},

    {"proverb": "The child who is not embraced by the village will burn it down to feel its warmth.",
     "language": "Pan-African", "country": "Pan-Africa",
     "meaning": "Communities must care for all members.",
     "philosophy": "Social responsibility and inclusion."},

    {"proverb": "Onye wetara oji wetara ndu",
     "language": "Igbo", "country": "Nigeria",
     "meaning": "He who brings kola brings life.",
     "philosophy": "Hospitality and generosity are sacred."},

    {"proverb": "Sankofa: Se wo were fi na wosankofa a yenkyi",
     "language": "Twi (Akan)", "country": "Ghana",
     "meaning": "It is not wrong to go back for what you forgot.",
     "philosophy": "Learn from the past to build the future."},

    {"proverb": "Kutana kwa maji, hukumba wapi chanzo",
     "language": "Swahili", "country": "East Africa",
     "meaning": "When waters meet, you cannot tell where each began.",
     "philosophy": "Unity transcends origins."},

    {"proverb": "Agya na ohwe n'akyiri",
     "language": "Twi (Akan)", "country": "Ghana",
     "meaning": "It is the father who watches what is behind.",
     "philosophy": "Leadership means protecting those who follow."},

    {"proverb": "Msafara hauna bwana",
     "language": "Swahili", "country": "East Africa",
     "meaning": "A journey has no master.",
     "philosophy": "Life's path belongs to no single person."},

    {"proverb": "Ile ti a ba fi owo gbe, a fi owo gbe",
     "language": "Yoruba", "country": "Nigeria",
     "meaning": "What is planted with the hand, is harvested with the hand.",
     "philosophy": "Actions have consequences — cause and effect."},

    {"proverb": "Biribi wo soro na ema yɛn ho",
     "language": "Twi (Akan)", "country": "Ghana",
     "meaning": "There is something in the heavens that gives us hope.",
     "philosophy": "Faith and hope carry the African spirit forward."},

    {"proverb": "Onipa na ohyɛ onipa bo",
     "language": "Twi (Akan)", "country": "Ghana",
     "meaning": "It is a person who gives another person value.",
     "philosophy": "Human dignity comes through community recognition."},

    {"proverb": "Wo ani so a na wo hun",
     "language": "Twi (Akan)", "country": "Ghana",
     "meaning": "When your eyes are open, you see.",
     "philosophy": "Awareness and consciousness are the beginning of wisdom."},
]


# ─────────────────────────────────────────────────────────
# WIKIPEDIA DATASET TOPICS
# Fetched on first boot — organized by category
# Each category maps to ChromaDB metadata for filtered retrieval
# ─────────────────────────────────────────────────────────
DATASET_TOPICS = {
    "history": [
        "History_of_Africa", "Ashanti_Empire", "Mali_Empire", "Songhai_Empire",
        "Kingdom_of_Kush", "Great_Zimbabwe", "Kingdom_of_Dahomey",
        "Trans-Saharan_trade", "Scramble_for_Africa",
        "African_independence_movements", "Pan-Africanism",
    ],
    "philosophy": [
        "Ubuntu_philosophy", "African_philosophy", "Maat", "Ujamaa", "Oral_tradition",
    ],
    "culture": [
        "Akan_people", "Yoruba_culture", "Swahili_culture", "Zulu_people",
        "Maasai_people", "Igbo_culture", "Hausa_people", "Adinkra_symbols", "Kente_cloth",
    ],
    "languages": [
        "Swahili_language", "Yoruba_language", "Hausa_language", "Igbo_language",
        "Zulu_language", "Twi", "Amharic_language", "Wolof_language",
        "Somali_language", "Oromo_language", "Lingala",
    ],
    "leaders": [
        "Kwame_Nkrumah", "Nelson_Mandela", "Thomas_Sankara", "Patrice_Lumumba",
        "Haile_Selassie", "Mansa_Musa", "Shaka_Zulu", "Yaa_Asantewaa",
        "Julius_Nyerere", "Wangari_Maathai", "Chinua_Achebe", "Marcus_Garvey",
        "Steve_Biko", "Miriam_Makeba",
    ],
    "food": [
        "Jollof_rice", "Fufu", "Ugali", "Injera", "Suya",
        "Waakye", "Egusi_soup", "Biltong", "Tagine", "Kenkey",
    ],
    "music": [
        "Afrobeats", "Highlife", "Amapiano", "Fuji_music", "Kwaito",
        "Fela_Kuti", "Afrobeat", "Makossa", "Mbalax", "Hiplife", "Soukous",
    ],
    "festivals": [
        "Homowo", "Odwira", "Durbar_festival", "Timkat", "Gerewol", "Aboakyir",
    ],
    "fashion": [
        "Kente_cloth", "Ankara_fabric", "Dashiki", "African_fashion", "Boubou_(clothing)",
    ],
    "governance": [
        "African_Union", "ECOWAS", "African_Continental_Free_Trade_Area", "Customary_law",
    ],
    "agriculture": [
        "Cassava", "Cocoa_bean", "Maize", "Agriculture_in_Africa",
        "Sorghum", "Millet", "Yam_(vegetable)",
    ],
    "modern_africa": [
        "Nollywood", "M-Pesa", "Science_and_technology_in_Africa",
        "Education_in_Africa", "Flutterwave", "African_Development_Bank", "Safaricom",
    ],
    "spirituality": [
        "African_traditional_religion", "Akan_religion", "Yoruba_religion",
    ],
}
