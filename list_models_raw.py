import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Available Gemini Models:")
        print("-" * 30)
        models = data.get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"Name: {m.get('name')}")
                print(f"Display Name: {m.get('displayName')}")
                print(f"Description: {m.get('description')}")
                print("-" * 30)
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
