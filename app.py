import gradio as gr
from groq import Groq
import os

AFRICAN_KNOWLEDGE = """
=== AFRICAN PROVERBS ===
Swahili: "Haraka haraka haina baraka" - Hurry hurry has no blessing
Yoruba: "Agbájọ ọwọ́ la fi ń sọ̀rọ̀ di múmú" - We cook corn together to make it tasty
Akan: "Obi nnim a, obi kyere" - One person does not know everything, we learn from each other

=== AFRICAN HISTORY ===
Ghana: March 6, 1957 - First independent African country (Kwame Nkrumah)
Nigeria: October 1, 1960 - Most populous (220M+), largest economy
Kenya: M-Pesa revolution, Silicon Savannah
South Africa: Nelson Mandela, Ubuntu philosophy

=== AFRICAN LANGUAGES ===
Swahili: Jambo, Asante sana, Karibu, Hakuna matata
Yoruba: Ẹ káàárọ̀, Báwo ni?, O ṣeun
Pidgin: How far?, I dey kampe, No wahala
Igbo: Kedu, Daalụ
Twi: Akwaaba, Meda ase

=== INNOVATIONS ===
M-Pesa: 50M+ users, mobile banking revolution
Nollywood: $6.4B industry, 2nd largest globally
African Unicorns: Flutterwave, Jumia, Paystack
AfCFTA: 1.3B people, $3.4T GDP
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
                messages = [{"role": "system", "content": f"You are African AI. Use this knowledge: {self.knowledge[:1000]}"}]
                for msg in self.history[-6:]:
                    messages.append({"role": msg["role"], "content": msg["message"]})
                messages.append({"role": "user", "content": message})

                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=800
                )
                reply = response.choices[0].message.content
            except:
                reply = f"{self.knowledge[:500]}\n\nWant to know more about Africa?"
        else:
            reply = "🌍 Jambo! Welcome to African AI! What would you like to know about Africa?"

        self.history.append({"role": "assistant", "message": reply})
        return reply

ai = AfricanAI()

demo = gr.ChatInterface(
    fn=lambda msg, hist: ai.chat(msg),
    title="🌍 African AI v2.0 ⚡",
    description="**The First AI Built For Africa By Africans**\n\n⚡ Powered by Groq | Built in Ghana/Nigeria 🇬🇭🇳🇬",
    examples=["Tell me about Jollof!", "Teach me Swahili", "What is Ubuntu?", "Who was Kwame Nkrumah?"],
    theme="soft"
)

demo.launch()
