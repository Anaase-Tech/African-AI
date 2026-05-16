"""
African AI v2.0 - Vercel Deployment
The First AI That Truly Understands Africa
"""

import os
import gradio as gr
from groq import Groq

# ============================================================
# AFRICAN KNOWLEDGE BASE
# ============================================================

AFRICAN_KNOWLEDGE = """
=== AFRICAN PROVERBS ===

Swahili: "Haraka haraka haina baraka" - Hurry hurry has no blessing
Yoruba: "Agbájọ ọwọ́ la fi ń sọ̀rọ̀ di múmú" - We cook corn together to make it tasty
Igbo: "Ọnwụ ewu na-azọ, ndị ọzọ na-ata ahịhịa" - While one goat is dying, others are eating grass
Akan: "Obi nnim a, obi kyere" - One person does not know everything, we learn from each other
Hausa: "Kowa ya san inda akuyansa" - Everyone knows where their shoe pinches
Zulu: "Ubuntu ungamntu ngabanye abantu" - A person is a person through other people

=== AFRICAN HISTORY ===

Ghana Independence: March 6, 1957 - First African country to gain independence
Leader: Kwame Nkrumah - "The Black Star of Africa", Pan-Africanist visionary

Nigeria Independence: October 1, 1960
Most populous African country: 220+ million people
Economic powerhouse of West Africa

Kenya: Independence December 12, 1963
M-Pesa revolution: Changed mobile banking worldwide
Swahili: Most spoken African language

South Africa: Apartheid ended 1994
Nelson Mandela - 27 years in prison, became president
Ubuntu philosophy: "I am because we are"

=== AFRICAN LANGUAGES ===

Swahili: Jambo (Hello), Asante sana (Thank you), Karibu (Welcome)
Yoruba: Ẹ káàárọ̀ (Good morning), Báwo ni? (How are you?)
Pidgin: How far? (How are you?), I dey kampe (I'm fine), No wahala (No problem)
Igbo: Kedu (Hello), Daalụ (Thank you)
Akan/Twi: Akwaaba (Welcome), Meda ase (Thank you)

=== MORE NIGERIAN CONTENT ===

Lagos: Economic capital, 20+ million people
Nollywood: $6.4 billion industry, 2,500+ films/year
Nigerian Innovation: Flutterwave, Paystack, Andela
Nigerian Music: Afrobeats global phenomenon

=== MORE GHANAIAN CONTENT ===

Accra: Capital city, vibrant tech scene
Akan proverbs: Rich philosophical tradition
Highlife music: Originated in Ghana
Ghanaian Leaders: Kwame Nkrumah, Kofi Annan

=== MORE KENYAN CONTENT ===

Nairobi: Silicon Savannah, tech hub
M-Pesa: Revolutionary mobile money (2007)
Kenyan Athletics: Marathon dominance
Safari: Maasai Mara, Amboseli, Tsavo

=== AFRICAN INNOVATIONS ===

M-Pesa: 50M+ users, banking the unbanked
Nollywood: 2nd largest film industry globally
African Unicorns: Flutterwave, Jumia, Interswitch, Wave
AfCFTA: Largest free trade area since WTO
Tech Hubs: Lagos, Nairobi, Cape Town, Accra
"""

# ============================================================
# AFRICAN AI CLASS
# ============================================================

class AfricanAI:
    """African AI with Groq intelligence"""
    
    def __init__(self):
        self.knowledge_base = AFRICAN_KNOWLEDGE
        self.conversation_history = []
        
        # Get Groq API key from environment
        groq_api_key = os.environ.get("GROQ_API_KEY")
        
        if groq_api_key:
            self.groq_client = Groq(api_key=groq_api_key)
            self.use_ai = True
            print("✅ Groq AI enabled!")
        else:
            self.use_ai = False
            print("⚠️ No API key - basic mode")
    
    def search_knowledge(self, query: str) -> str:
        """Search African knowledge base"""
        query_lower = query.lower()
        relevant = []
        
        for section in self.knowledge_base.split('==='):
            if any(word in section.lower() for word in query_lower.split()):
                relevant.append(section.strip())
        
        return "\n\n".join(relevant[:5]) if relevant else self.knowledge_base[:2000]
    
    def respond_with_groq(self, message: str) -> str:
        """Smart response using Groq"""
        context = self.search_knowledge(message)
        
        system_prompt = f"""You are African AI, built for Africa by Africans.

AFRICAN KNOWLEDGE:
{context}

Mission:
- Share African knowledge, languages, culture
- Use African examples and proverbs
- Be warm, welcoming, proud
- Celebrate African achievements

Guidelines:
- Use African context always
- Include proverbs when relevant
- Teach languages naturally
- Correct stereotypes with facts"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history
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
            return f"⚠️ Using basic mode...\n\n{self.respond_basic(message)}"
    
    def respond_basic(self, message: str) -> str:
        """Basic fallback response"""
        knowledge = self.search_knowledge(message)
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ['hello', 'hi', 'jambo']):
            return "🌍 Jambo! Welcome to African AI! What would you like to know about Africa?"
        
        return f"Here's what I know:\n\n{knowledge}\n\nWant to know more about Africa?"
    
    def chat(self, message: str) -> str:
        """Main chat function"""
        self.conversation_history.append({"role": "user", "message": message})
        
        if self.use_ai:
            response = self.respond_with_groq(message)
        else:
            response = self.respond_basic(message)
        
        self.conversation_history.append({"role": "assistant", "message": response})
        return response

# Initialize AI
african_ai = AfricanAI()

# ============================================================
# GRADIO INTERFACE
# ============================================================

def chat_interface(message, history):
    """Gradio chat interface"""
    return african_ai.chat(message)

# Create interface
demo = gr.ChatInterface(
    fn=chat_interface,
    title="🌍 African AI v2.0 ⚡",
    description="""
    **The First AI That Truly Understands Africa**
    
    ⚡ Powered by Groq AI + African Knowledge
    
    Ask about:
    • 🗣️ African languages (Swahili, Yoruba, Pidgin...)
    • 📚 African proverbs & wisdom
    • 🏛️ African history & leaders
    • 🍲 African cuisine (Jollof wars! 😄)
    • 💡 African innovations & tech
    
    Built by Africans, for Africans 🌍
    
    **Feedback:** [Google Form Link Here]
    
    *Created by Eddy & Claude (CTO) | Built on a phone! 📱*
    """,
    examples=[
        "Tell me about the Jollof rice rivalry!",
        "What is Ubuntu philosophy?",
        "Teach me Nigerian Pidgin basics",
        "Who was Kwame Nkrumah?",
        "What is M-Pesa?",
        "How do you say hello in Swahili?",
    ],
    theme="soft",
    chatbot=gr.Chatbot(height=500)
)

# Launch for Vercel
if __name__ == "__main__":
    demo.launch()
