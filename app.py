"""
African AI v2.0 - Vercel Deployment
"""

import os
from groq import Groq
import gradio as gr

# African Knowledge Base
AFRICAN_KNOWLEDGE = """
=== AFRICAN PROVERBS ===
Swahili: "Haraka haraka haina baraka" - Hurry hurry has no blessing
Yoruba: "Agbájọ ọwọ́ la fi ń sọ̀rọ̀ di múmú" - We cook corn together to make it tasty
Igbo: "Ọnwụ ewu na-azọ, ndị ọzọ na-ata ahịhịa" - While one goat is dying, others are eating grass
Akan: "Obi nnim a, obi kyere" - One person does not know everything
Hausa: "Kowa ya san inda akuyansa" - Everyone knows where their shoe pinches
Zulu: "Ubuntu ungamntu ngabanye abantu" - A person is a person through other people

=== AFRICAN HISTORY ===
Ghana Independence: March 6, 1957 - First African country to gain independence
Leader: Kwame Nkrumah - "The Black Star of Africa"
Nigeria Independence: October 1, 1960 - Most populous African country: 220+ million
Kenya: M-Pesa revolution changed mobile banking worldwide
South Africa: Nelson Mandela, Ubuntu philosophy

=== AFRICAN LANGUAGES ===
Swahili: Jambo (Hello), Asante sana (Thank you), Karibu (Welcome), Hakuna matata (No worries)
Yoruba: Ẹ káàárọ̀ (Good morning), Báwo ni? (How are you?), O ṣeun (Thank you)
Pidgin: How far? (How are you?), I dey kampe (I'm fine), No wahala (No problem)
Igbo: Kedu (Hello), Daalụ (Thank you), Nnọọ (Welcome)
Twi: Akwaaba (Welcome), Meda ase (Thank you), Ɛte sɛn? (How are you?)

=== NIGERIAN CONTENT ===
Lagos: Economic capital, 20+ million people
Nollywood: $6.4 billion industry, 2,500+ films/year
Nigerian Innovation: Flutterwave ($3B), Paystack (acquired by Stripe), Andela
Nigerian Music: Afrobeats global phenomenon (Burna Boy, Wizkid, Davido)

=== GHANAIAN CONTENT ===
Accra: Capital city, vibrant tech scene
Akan proverbs: Rich philosophical tradition
Highlife music: Originated in Ghana
Leaders: Kwame Nkrumah, Kofi Annan (UN Secretary-General, Nobel Peace Prize)

=== KENYAN CONTENT ===
Nairobi: Silicon Savannah, tech hub of East Africa
M-Pesa: Revolutionary mobile money (2007), 50M+ users
Kenyan Athletics: Marathon dominance (Kipchoge)
Safari: Maasai Mara, Amboseli, Tsavo

=== AFRICAN INNOVATIONS ===
M-Pesa: 50M+ users, banking the unbanked
Nollywood: 2nd largest film industry globally
African Unicorns: Flutterwave, Jumia, Interswitch, Wave
AfCFTA: African Continental Free Trade Area - 1.3B people, $3.4T GDP
Tech Hubs: Lagos (Yabacon Valley), Nairobi (Silicon Savannah), Cape Town, Accra
"""

class AfricanAI:
    def __init__(self):
        self.knowledge_base = AFRICAN_KNOWLEDGE
        self.conversation_history = []
        
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if groq_api_key:
            self.groq_client = Groq(api_key=groq_api_key)
            self.use_ai = True
        else:
            self.use_ai = False
    
    def search_knowledge(self, query):
        relevant = []
        for section in self.knowledge_base.split('==='):
            if any(word in section.lower() for word in query.lower().split()):
                relevant.append(section.strip())
        return "\n\n".join(relevant[:5]) if relevant else self.knowledge_base[:2000]
    
    def respond_with_groq(self, message):
        context = self.search_knowledge(message)
        
        system_prompt = f"""You are African AI, built for Africa by Africans.

AFRICAN KNOWLEDGE:
{context}

Mission: Share African knowledge, languages, culture. Use African proverbs and examples. Be warm and welcoming."""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["message"]})
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return self.respond_basic(message)
    
    def respond_basic(self, message):
        knowledge = self.search_knowledge(message)
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ['hello', 'hi', 'jambo', 'hey']):
            return "🌍 Jambo! Welcome to African AI! I'm here to share African knowledge, languages, and culture. What would you like to know?"
        
        if knowledge and len(knowledge) > 100:
            return f"{knowledge}\n\nWant to know more about Africa? Just ask!"
        
        return "I'm African AI! Ask me about African languages, proverbs, history, culture, innovations, and more! 🌍"
    
    def chat(self, message):
        self.conversation_history.append({"role": "user", "message": message})
        response = self.respond_with_groq(message) if self.use_ai else self.respond_basic(message)
        self.conversation_history.append({"role": "assistant", "message": response})
        return response

# Initialize AI
african_ai = AfricanAI()

def chat_interface(message, history):
    return african_ai.chat(message)

# Create Gradio interface
demo = gr.ChatInterface(
    fn=chat_interface,
    title="🌍 African AI v2.0 ⚡",
    description="""**The First AI That Truly Understands Africa**

⚡ Powered by Groq AI + 9KB of African Knowledge

Ask about:
• 🗣️ African languages (Swahili, Yoruba, Pidgin, Igbo, Akan...)
• 📚 African proverbs & wisdom  
• 🏛️ African history & leaders
• 🎭 African culture & traditions
• 🍲 African cuisine (Jollof wars welcome! 😄)
• 💡 African innovations & tech

*Built by Eddy & Claude (CTO) | Made in Ghana/Nigeria 🇬🇭🇳🇬 | Built on a phone! 📱*
    """,
    examples=[
        "Tell me about the Jollof rice rivalry!",
        "What is Ubuntu philosophy?",
        "Teach me Nigerian Pidgin basics",
        "Who was Kwame Nkrumah?",
        "What is M-Pesa and how did it change Africa?",
        "How do you say hello in Swahili?",
    ],
    theme="soft",
    chatbot=gr.Chatbot(height=500)
)

# Vercel needs this
app = demo
