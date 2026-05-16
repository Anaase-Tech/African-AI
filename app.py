import gradio as gr
from groq import Groq
import os

AFRICAN_KNOWLEDGE = """
=== AFRICAN PROVERBS ===
Swahili: "Haraka haraka haina baraka" - Hurry hurry has no blessing
Yoruba: "Agbájọ ọwọ́ la fi ń sọ̀rọ̀ di múmú" - We cook corn together to make it tasty
Akan: "Obi nnim a, obi kyere" - One person does not know everything
Hausa: "Kowa ya san inda akuyansa" - Everyone knows where their shoe pinches
Zulu: "Ubuntu ungamntu ngabanye abantu" - A person is a person through other people

=== AFRICAN HISTORY ===
Ghana: March 6, 1957 - First independent (Kwame Nkrumah "Black Star of Africa")
Nigeria: October 1, 1960 - Most populous 220M+, largest economy, Nollywood $6.4B
Kenya: M-Pesa revolution 2007, 50M+ users, Silicon Savannah tech hub
South Africa: Apartheid ended 1994, Nelson Mandela, Ubuntu philosophy

=== AFRICAN LANGUAGES ===
Swahili: Jambo (Hello), Asante sana (Thank you), Karibu (Welcome), Hakuna matata
Yoruba: Ẹ káàárọ̀ (Good morning), Báwo ni? (How are you?), O ṣeun (Thank you)
Pidgin: How far? (How are you?), I dey kampe (I'm fine), No wahala (No problem)
Igbo: Kedu (Hello), Daalụ (Thank you), Nnọọ (Welcome)
Twi: Akwaaba (Welcome), Meda ase (Thank you), Ɛte sɛn? (How are you?)

=== NIGERIAN CONTENT ===
Lagos: Economic capital 20M+ people, Yabacon Valley tech hub
Nollywood: 2,500+ films/year, 2nd largest industry globally
Innovations: Flutterwave $3B, Paystack (Stripe acquisition), Andela
Music: Afrobeats global (Burna Boy, Wizkid, Davido)

=== GHANAIAN CONTENT ===
Accra: Capital, vibrant tech scene, iSpace hub
Akan proverbs: Rich philosophical tradition
Highlife music: Originated in Ghana, influenced West Africa
Leaders: Kwame Nkrumah (Pan-Africanism), Kofi Annan (UN, Nobel Peace Prize)

=== KENYAN CONTENT ===
Nairobi: Silicon Savannah, M-Pesa birthplace
M-Pesa: Revolutionary mobile money, banking the unbanked
Athletics: Marathon dominance (Eliud Kipchoge)
Safari: Maasai Mara, Amboseli National Park

=== AFRICAN INNOVATIONS ===
M-Pesa: 50M+ users across Africa, model for global mobile banking
Nollywood: $6.4B industry, cultural export to world
African Unicorns: Flutterwave, Jumia, Interswitch, Wave ($1B+ valuations)
AfCFTA: African Continental Free Trade Area - 1.3B people, $3.4T GDP
Tech Hubs: Lagos, Nairobi, Cape Town, Accra, Kigali
"""

class AfricanAI:
    def __init__(self):
        self.knowledge = AFRICAN_KNOWLEDGE
        self.history = []
        api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
    
    def chat(self, message):
        self.history.append({"role": "user", "message": message})
        
        if self.client:
            try:
                system_msg = f"You are African AI, built for Africa by Africans. Use this knowledge: {self.knowledge[:1500]}. Be warm, use African proverbs naturally, celebrate African culture."
                
                messages = [{"role": "system", "content": system_msg}]
                for msg in self.history[-6:]:
                    messages.append({"role": msg["role"], "content": msg["message"]})
                messages.append({"role": "user", "content": message})
                
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                reply = response.choices[0].message.content
            except Exception as e:
                # Fallback to basic mode
                reply = self._basic_response(message)
        else:
            reply = self._basic_response(message)
        
        self.history.append({"role": "assistant", "message": reply})
        return reply
    
    def _basic_response(self, message):
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ['hello', 'hi', 'jambo', 'hey']):
            return "🌍 Jambo! Welcome to African AI! I'm here to share African knowledge, languages, and culture. What would you like to know?"
        
        # Search knowledge for relevant content
        relevant = []
        for section in self.knowledge.split('==='):
            if any(word in section.lower() for word in msg_lower.split()):
                relevant.append(section.strip())
        
        if relevant:
            return f"{chr(10).join(relevant[:3])}\n\nWant to know more about Africa? Just ask!"
        
        return f"I'm African AI! Ask me about:\n• African languages & proverbs\n• African history & leaders\n• African culture & traditions\n• African innovations\n\nWhat interests you? 🌍"

ai = AfricanAI()

demo = gr.ChatInterface(
    fn=lambda msg, hist: ai.chat(msg),
    title="🌍 African AI v2.0 ⚡",
    description="""**The First AI Built For Africa By Africans**
 
    9KB of African Knowledge

Ask about: African languages • Proverbs • History • Culture • Innovations

*Built in Ghana 🇬🇭 | By Y.A B3rima & Claude (CTO) | On a phone! 📱*""",
    examples=[
        "Tell me about Jollof rice!",
        "What is Ubuntu philosophy?",
        "Teach me Swahili basics",
        "Who was Kwame Nkrumah?",
        "What is M-Pesa?"
    ],
    theme="soft",
    chatbot=gr.Chatbot(height=500)
)

# CRITICAL: This is what Vercel needs!
app = demo
