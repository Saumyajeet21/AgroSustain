import os
import sys
import requests
from dotenv import load_dotenv

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# -- Test 1: Google Gemini ----------------------------------------------------
print("\n[Gemini] Testing Google Gemini API...")
key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
payload = {"contents": [{"parts": [{"text": "Reply with exactly: AGROSUSTAIN OK"}]}]}
try:
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code == 200:
        reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"   [OK] SUCCESS! Gemini replied: {reply.strip()}")
    else:
        err = r.json().get("error", {}).get("message", r.text)
        print(f"   [FAIL] {r.status_code} -- {err}")
except Exception as e:
    print(f"   [ERROR] {e}")

# -- Test 2: OpenWeatherMap ---------------------------------------------------
print("\n[Weather] Testing OpenWeatherMap API...")
key = os.getenv("OPENWEATHER_API_KEY")
url = "https://api.openweathermap.org/data/2.5/weather"
params = {"lat": 28.6139, "lon": 77.2090, "appid": key, "units": "metric"}
try:
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        d = r.json()
        print(f"   [OK] SUCCESS! City: {d['name']}, Temp: {d['main']['temp']}C, Humidity: {d['main']['humidity']}%")
    elif r.status_code == 401:
        print("   [FAIL] Key is invalid or not activated yet. New keys take up to 10 mins to activate.")
    else:
        print(f"   [FAIL] {r.status_code} -- {r.text}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\nDone.")
