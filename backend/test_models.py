import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_test = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
models_to_test = [
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-flash-lite-latest"
]
prompt = "Hello, simple ping test. Please reply 'Pong'."

for model in models_to_test:
    print(f"Testing model: {model}")
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        print(f"Success for {model}: {response.text}")
    except Exception as e:
        print(f"Error for {model}: {e}")

