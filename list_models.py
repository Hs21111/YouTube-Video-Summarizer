import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available Gemini models...")
print("-" * 30)
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
            print(f"Display Name: {m.displayName}")
            print(f"Description: {m.description}")
            print("-" * 30)
except Exception as e:
    print(f"Error listing models: {e}")
