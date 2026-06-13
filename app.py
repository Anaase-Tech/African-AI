"""
=============================================================
AFRICAN AI v4.1 — MAIN ENTRY POINT
By Anaase-Tech Ltd | CTO: Claude | CEO: Eddy B3rima

This file contains only the Gradio UI and launch config.
All logic lives in separate modules:

  config.py    — API keys, paths, model names
  knowledge.py — LOCAL_TERMS, PROVERBS, DATASET_TOPICS
  language.py  — detect_language(), user_requested_language()
  retrieval.py — Wikipedia fetch, ChromaDB index, hybrid search
  respond.py   — respond() chat pipeline
=============================================================
"""

import os
import gradio as gr

from config   import LOGO_URL, VERSION, READY_FILE
from retrieval import build_index, load_index, build_bm25_index
from respond   import respond as _respond

# ─────────────────────────────────────────────────────────
# BOOT — Load or build the knowledge index
# ─────────────────────────────────────────────────────────
if os.path.exists(READY_FILE):
    collection = load_index()
else:
    collection = build_index()

bm25_index, bm25_docs, bm25_metas = build_bm25_index(collection)


# Wrap respond() to inject index objects (Gradio can't pass them as inputs)
def respond(message, history):
    yield from _respond(message, history, collection, bm25_index, bm25_docs, bm25_metas)


# ─────────────────────────────────────────────────────────
# CSS — Mobile-first African dark theme
# Gold + Green Pan-African identity
# Designed for Samsung A04e and similar Android phones
# ─────────────────────────────────────────────────────────
CSS = """
/* ════════════════════════════════════════
   SPLASH SCREEN
════════════════════════════════════════ */
#splash {
    position: fixed; inset: 0; z-index: 9999;
    background: #060606;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    animation: splashFade 0.8s ease 2.8s forwards;
}
@keyframes splashFade {
    to { opacity: 0; pointer-events: none; visibility: hidden; }
}
#splash img {
    width: 130px; height: 130px; border-radius: 50%;
    border: 2px solid rgba(255,200,0,0.4);
    animation: splashPulse 1.4s ease-in-out infinite alternate;
    margin-bottom: 24px;
}
@keyframes splashPulse {
    from { box-shadow: 0 0 30px rgba(255,180,0,0.25); }
    to   { box-shadow: 0 0 60px rgba(255,180,0,0.55), 0 0 100px rgba(0,200,80,0.20); }
}
#splash-title {
    font-size: 2.2rem; font-weight: 900; letter-spacing: 6px;
    background: linear-gradient(90deg, #FFD54A, #59D66F, #FFD54A);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 8px;
}
#splash-sub  { color: #888; font-size: 0.85rem; letter-spacing: 2px; }
#splash-dots { display: flex; gap: 8px; margin-top: 24px; }
#splash-dots span {
    width: 8px; height: 8px; border-radius: 50%; background: #D4A017;
    animation: dotPulse 1.2s ease-in-out infinite;
}
#splash-dots span:nth-child(2) { animation-delay: 0.2s; }
#splash-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotPulse {
    0%,100% { opacity: 0.3; transform: scale(0.8); }
    50%     { opacity: 1;   transform: scale(1.2); }
}

/* ════════════════════════════════════════
   BASE LAYOUT
════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box !important; }
html, body {
    background: #060606 !important; color: #f0f0f0 !important;
    font-family: 'Inter', sans-serif;
    width: 100% !important; max-width: 100vw !important;
    overflow-x: hidden !important; margin: 0 !important; padding: 0 !important;
}
.gradio-container {
    background: #060606 !important; width: 100% !important;
    max-width: 100vw !important; min-width: 0 !important;
    padding: 0 !important; margin: 0 !important; overflow-x: hidden !important;
}

/* ════════════════════════════════════════
   HERO SECTION
════════════════════════════════════════ */
.hero {
    position: relative; overflow: hidden; text-align: center;
    background: linear-gradient(135deg, #111008 0%, #070707 50%, #060d07 100%);
    border-bottom: 1px solid rgba(255,200,50,0.20);
    padding: 24px 16px 20px; margin-bottom: 8px; width: 100%;
}
.hero::before {
    content: ""; position: absolute; inset: 0;
    background:
        radial-gradient(circle at 15% 20%, rgba(255,190,0,0.10), transparent 35%),
        radial-gradient(circle at 85% 80%, rgba(0,220,90,0.09), transparent 35%);
    pointer-events: none;
}
.logo-wrap { display: flex; justify-content: center; margin-bottom: 10px; }
.logo-wrap img {
    width: 76px; height: 76px; object-fit: contain; border-radius: 50%;
    padding: 6px; background: rgba(255,255,255,0.03);
    border: 1.5px solid rgba(255,200,0,0.30);
    animation: logoPulse 4s ease-in-out infinite alternate;
}
@keyframes logoPulse {
    from { box-shadow: 0 0 20px rgba(255,180,0,0.15); }
    to   { box-shadow: 0 0 36px rgba(255,180,0,0.35), 0 0 72px rgba(0,200,80,0.15); }
}
.hero-title {
    font-size: 2.2rem; font-weight: 900; letter-spacing: 5px; margin-bottom: 8px;
    background: linear-gradient(90deg, #FFD54A 0%, #F6C343 35%, #59D66F 65%, #FFD54A 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; animation: glowPulse 4s ease-in-out infinite alternate;
}
@keyframes glowPulse {
    from { filter: drop-shadow(0 0 6px rgba(255,200,0,0.22)); }
    to   { filter: drop-shadow(0 0 20px rgba(0,255,100,0.24)); }
}
.hero-sub { color: #c0c0c0; font-size: 0.85rem; line-height: 1.6; margin: 0 auto 14px; }
.pills { display: flex; justify-content: center; flex-wrap: wrap; gap: 6px; }
.pill {
    padding: 5px 12px; border-radius: 999px;
    background: rgba(255,200,0,0.07); border: 1px solid rgba(255,200,0,0.20);
    color: #f0c84b; font-size: 0.75rem; font-weight: 600;
}

/* ════════════════════════════════════════
   KILL ALL WHITE BOXES
════════════════════════════════════════ */
.gradio-container > .main > .wrap, .gradio-container .wrap,
.gap, .block, [data-testid="chatbot"] > div {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important; margin: 0 !important;
}

/* ════════════════════════════════════════
   CHAT WINDOW
════════════════════════════════════════ */
[data-testid="chatbot"] {
    background: #080808 !important; border: none !important;
    border-radius: 0 !important; width: 100% !important;
    max-width: 100vw !important; overflow-x: hidden !important;
}

/* ════════════════════════════════════════
   USER BUBBLE
════════════════════════════════════════ */
[data-testid="user"] {
    background: rgba(140,90,0,0.60) !important;
    border: 1px solid rgba(255,200,0,0.30) !important;
    border-radius: 18px 18px 4px 18px !important;
    color: #ffffff !important; padding: 14px 18px !important;
    box-shadow: none !important; width: auto !important;
    max-width: 88% !important; margin-left: auto !important;
    word-break: normal !important; overflow-wrap: anywhere !important;
    white-space: normal !important; line-height: 1.7 !important; font-size: 1rem !important;
}

/* ════════════════════════════════════════
   BOT BUBBLE
════════════════════════════════════════ */
[data-testid="bot"] {
    background: #161616 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 18px 18px 18px 4px !important;
    color: #f5f5f5 !important; padding: 14px 18px !important;
    width: auto !important; max-width: 92% !important;
    word-break: normal !important; white-space: normal !important;
    line-height: 1.8 !important; font-size: 16px !important;
}
[data-testid="bot"] * { color: #f5f5f5 !important; opacity: 1 !important; }
[data-testid="bot"] p { margin-bottom: 12px !important; line-height: 1.8 !important; }
[data-testid="bot"] > div, [data-testid="user"] > div,
[data-testid="bot"] > div > div, [data-testid="user"] > div > div {
    background: transparent !important; border: none !important;
    padding: 0 !important; box-shadow: none !important;
    width: 100% !important; color: inherit !important;
}

/* ════════════════════════════════════════
   INPUT AREA
════════════════════════════════════════ */
textarea {
    background: #111 !important; color: #fff !important;
    border-radius: 16px !important; border: 1px solid rgba(255,200,0,0.25) !important;
    font-size: 1rem !important; padding: 14px !important; width: 100% !important;
}
textarea:focus {
    border: 1px solid rgba(255,200,0,0.55) !important;
    box-shadow: 0 0 12px rgba(255,180,0,0.18) !important; outline: none !important;
}

/* ════════════════════════════════════════
   BUTTONS
════════════════════════════════════════ */
button { border-radius: 14px !important; transition: 0.2s ease !important; }
button:hover { transform: translateY(-1px); }
.primary {
    background: linear-gradient(90deg, #C8960F, #F0C030) !important;
    border: none !important; color: #000 !important; font-weight: 800 !important;
}
.secondary {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #bbb !important; font-size: 0.78em !important;
}
.secondary:hover { border-color: rgba(255,200,0,0.4) !important; color: #FFD54A !important; }

/* ════════════════════════════════════════
   MISC
════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }
footer { display: none !important; }
"""

# ─────────────────────────────────────────────────────────
# GRADIO UI
# ─────────────────────────────────────────────────────────
EXAMPLES = [
    "Tell me about the Mali Empire",
    "What does Ubuntu mean?",
    "What is akwaaba in Twi?",
    "History of Afrobeats music",
    "Who was Thomas Sankara?",
    "Tell me about Kente cloth",
    "Who was Yaa Asantewaa?",
    "What is akonta in Akan?",
    "Share an African proverb",
    "Tell me about the Ashanti Empire",
]

with gr.Blocks(title=f"African AI {VERSION}") as demo:

    # Splash screen
    gr.HTML(f"""
    <div id="splash">
        <img src="https://raw.githubusercontent.com/Anaase-Tech/African-AI/main/logo.png" alt="African AI"
             onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/8/80/Africa_icon.svg'"/>
        <div id="splash-title">AFRICAN AI</div>
        <div id="splash-sub">BY AFRICA · FOR AFRICA</div>
        <div id="splash-dots"><span></span><span></span><span></span></div>
    </div>
    """)

    # Hero section
    gr.HTML(f"""
    <div class="hero">
        <div class="logo-wrap">
            <img src="https://raw.githubusercontent.com/Anaase-Tech/African-AI/main/logo.png" alt="African AI"
                 onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/8/80/Africa_icon.svg'"/>
        </div>
        <div class="hero-title">AFRICAN AI</div>
        <div class="hero-sub">
            Built by Africans &bull; Powered by African Knowledge<br>
            Preserving culture, wisdom, languages, history and innovation 🌍
        </div>
        <div class="pills">
            <span class="pill">🌍 African Knowledge Base</span>
            <span class="pill">🗂 14 Categories</span>
            <span class="pill">🌐 African Languages</span>
            <span class="pill">🇬🇭 Anaase-Tech</span>
            <span class="pill">⚡ RAG {VERSION}</span>
        </div>
    </div>
    """)

    # Chat window
    chatbot = gr.Chatbot(
        height="72vh",
        show_label=False,
        avatar_images=(None, "https://raw.githubusercontent.com/Anaase-Tech/African-AI/main/logo.png"
        ),
    )

    # Input row
    with gr.Row():
        msg  = gr.Textbox(
            placeholder="Ask about African history, culture, proverbs, music, leaders...",
            show_label=False, scale=5, lines=1,
        )
        send = gr.Button("Ask →", variant="primary", scale=1)

    clear = gr.Button("Clear chat", size="sm")

    gr.HTML("<div style='color:#444;font-size:0.72em;text-align:center;padding:6px 0 2px;'>— Try asking —</div>")

    with gr.Row():
        for ex in EXAMPLES[:5]:
            gr.Button(ex, size="sm").click(lambda e=ex: e, outputs=msg)
    with gr.Row():
        for ex in EXAMPLES[5:]:
            gr.Button(ex, size="sm").click(lambda e=ex: e, outputs=msg)

    # Community contribution panel
    gr.HTML("""
    <div style="background:linear-gradient(135deg,#0d0d00,#001a0a);
                border:1px solid rgba(255,200,0,0.20);border-radius:16px;
                padding:18px 16px;margin:12px 8px 4px;text-align:center;">
        <div style="font-size:1.1rem;font-weight:700;color:#FFD54A;margin-bottom:6px;">
            🌍 Help Build African AI
        </div>
        <div style="font-size:0.82rem;color:#aaa;margin-bottom:12px;line-height:1.5;">
            African AI learns from Africans.<br>
            Share a word, proverb, or cultural knowledge from your language.
        </div>
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSedb5p6UaqOFYjnpNV1k2e4p8_WQoEEZB94imexe72MjKJUQg/viewform"
           target="_blank"
           style="display:inline-block;background:linear-gradient(90deg,#C8960F,#F0C030);
                  color:#000;font-weight:800;font-size:0.88rem;padding:10px 24px;
                  border-radius:999px;text-decoration:none;margin-bottom:8px;">
            ✍️ Submit Knowledge
        </a>
        <div style="font-size:0.72rem;color:#555;margin-top:6px;">
            Every submission reviewed and added to the knowledge base
        </div>
    </div>
    """)

    gr.HTML(f"""
    <div style="text-align:center;padding:14px 0 4px;font-size:0.72rem;color:#444;">
        African AI {VERSION} &bull; Built in Ghana 🇬🇭 by Anaase-Tech
    </div>
    """)

    # Event handlers
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], outputs=chatbot)


# ─────────────────────────────────────────────────────────
# LAUNCH
# ─────────────────────────────────────────────────────────
demo.queue().launch(
    server_name="0.0.0.0",
    server_port=7860,
    show_error=True,
    css=CSS,
    theme=gr.themes.Base(primary_hue="yellow", neutral_hue="slate"),
)
