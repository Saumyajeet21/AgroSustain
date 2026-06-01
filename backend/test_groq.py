"""
Quick test — verifies the Groq API key works and the model responds.
Run: python backend/test_groq.py   (from project root)
  or: python test_groq.py           (from backend/ folder)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same folder as this script
load_dotenv(Path(__file__).parent / ".env")

from groq import Groq

BOLD  = "\033[1m"
GREEN = "\033[92m"
RED   = "\033[91m"
CYAN  = "\033[96m"
RESET = "\033[0m"

def test_groq():
    key = os.getenv("GROQ_API_KEY", "")
    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}  Groq API — Connection Test{RESET}")
    print(f"{'='*55}")

    if not key or key == "your_groq_api_key_here":
        print(f"{RED}[FAIL]{RESET} GROQ_API_KEY is missing or not set in .env")
        return

    masked = key[:8] + "..." + key[-4:]
    print(f"  Key detected : {CYAN}{masked}{RESET}")

    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": "Say exactly: 'Groq is working!'"},
            ],
            max_tokens=20,
        )
        reply = response.choices[0].message.content.strip()
        model = response.model
        tokens_used = response.usage.total_tokens

        print(f"\n{GREEN}[OK]{RESET}  Groq responded successfully!")
        print(f"  Model        : {CYAN}{model}{RESET}")
        print(f"  Reply        : {CYAN}{reply}{RESET}")
        print(f"  Tokens used  : {tokens_used}")

    except Exception as e:
        print(f"\n{RED}[FAIL]{RESET} Groq API call failed:")
        print(f"  Error: {e}")

    print(f"\n{'='*55}\n")

if __name__ == "__main__":
    test_groq()
