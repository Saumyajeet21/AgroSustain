import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── TEST 1: OPENWEATHERMAP ────────────────────────────────────────────────────
def test_openweather():
    print("\n🌦️  Testing OpenWeatherMap API...")
    key = os.getenv("OPENWEATHER_API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": 28.6139, "lon": 77.2090, "appid": key, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        d = r.json()
        print(f"   ✅ SUCCESS! Location: {d['name']}, Temp: {d['main']['temp']}°C, Humidity: {d['main']['humidity']}%")
    elif r.status_code == 401:
        print("   ❌ FAIL: Key is invalid or hasn't activated yet (wait 15 mins and retry).")
    else:
        print(f"   ❌ FAIL: Error {r.status_code} - {r.text}")

# ─── TEST 2: GOOGLE GEMINI ────────────────────────────────────────────────────
def test_gemini():
    print("\n🤖 Testing Google Gemini API...")
    key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": "Reply with exactly: AGROSUSTAIN OK"}]}]}
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code == 200:
        reply = r.json()['candidates'][0]['content']['parts'][0]['text']
        print(f"   ✅ SUCCESS! Gemini replied: {reply.strip()}")
    else:
        print(f"   ❌ FAIL: Error {r.status_code} - {r.json().get('error', {}).get('message', r.text)}")

# ─── TEST 3: ISRIC SOILGRIDS (no key needed) ──────────────────────────────────
def test_soilgrids():
    print("\n🌱 Testing ISRIC SoilGrids API (no key needed)...")
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {"lon": 77.2090, "lat": 28.6139, "property": "phh2o", "depth": "0-5cm", "value": "mean"}
    r = requests.get(url, params=params, timeout=15)
    if r.status_code == 200:
        raw_ph = r.json()['properties']['layers'][0]['depths'][0]['values']['mean']
        print(f"   ✅ SUCCESS! Topsoil pH for Delhi: {raw_ph / 10.0}")
    else:
        print(f"   ❌ FAIL: Error {r.status_code}")

# ─── RUN ALL TESTS ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  🌱 AgroSustain — API Connection Test")
    print("=" * 50)
    test_openweather()
    test_gemini()
    test_soilgrids()
    print("\n" + "=" * 50)
    print("  Test Complete!")
    print("=" * 50)
