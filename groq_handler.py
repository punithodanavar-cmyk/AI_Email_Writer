from groq import Groq
from config import Config
import time

class GroqEmailGenerator:
    def __init__(self):
        print("🚀 Initializing Groq...")
        print("API KEY:", Config.GROQ_API_KEY)

        self.client = Groq(api_key=Config.GROQ_API_KEY)

        # ✅ FINAL WORKING MODEL
        self.model = "llama-3.1-8b-instant"

    def generate_email(self, recipient, email_type, tone, context):
        try:
            prompt = f"""
Generate a professional email:

Recipient: {recipient}
Type: {email_type}
Tone: {tone}
Context: {context}

Format:
SUBJECT: ...
BODY: ...
"""

            print("📤 Sending request to Groq...")

            start_time = time.time()

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=1024
            )

            response_time = time.time() - start_time

            print("✅ Response received")

            content = chat_completion.choices[0].message.content

            return {
                "success": True,
                "subject": "Generated Email",
                "body": content,
                "tokens_used": 0,
                "response_time": response_time
            }

        except Exception as e:
            print("🔥 GROQ ERROR:", e)
            return {
                "success": False,
                "error": str(e)
            }