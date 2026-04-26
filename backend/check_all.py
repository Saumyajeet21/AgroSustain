"""
AgroSustain - Full API Health Check
Tests: Gemini 2.5 Flash, OpenWeather, ISRIC SoilGrids, Supabase
"""
import os, sys, time, requests
from dotenv import load_dotenv
load_dotenv()

W  = "\033[0m"
G  = "\033[92m"
R  = "\033[91m"
Y  = "\033[93m"
B  = "\033[94m"
BO = "\033[1m"

def ok(msg):  print(f"  {G}[PASS]{W} {msg}")
def fail(msg):print(f"  {R}[FAIL]{W} {msg}")
def info(msg):print(f"  {Y}[INFO]{W} {msg}")

print(f"\n{BO}{B}{'='*55}{W}")
print(f"{BO}   AgroSustain — Full API Health Check{W}")
print(f"{BO}{B}{'='*55}{W}\n")

results = {}

# ── 1. Gemini 2.5 Flash ────────────────────────────────────────────────────
print(f"{BO}[1] Google Gemini 2.5 Flash{W}")
key = os.getenv("GEMINI_API_KEY")
if not key:
    fail("GEMINI_API_KEY not found in .env"); results["gemini"] = False
else:
    try:
        t0 = time.time()
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        r = requests.post(url, params={"key": key},
            json={"contents": [{"parts": [{"text": "Reply with only: OK"}]}]}, timeout=20)
        elapsed = round(time.time() - t0, 2)
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            ok(f"Response: '{text}' ({elapsed}s)")
            results["gemini"] = True
        else:
            fail(f"HTTP {r.status_code}: {r.text[:120]}")
            results["gemini"] = False
    except Exception as e:
        fail(str(e)); results["gemini"] = False

# ── 2. OpenWeatherMap ─────────────────────────────────────────────────────
print(f"\n{BO}[2] OpenWeatherMap API{W}")
wkey = os.getenv("OPENWEATHER_API_KEY")
if not wkey:
    fail("OPENWEATHER_API_KEY not found in .env"); results["weather"] = False
else:
    try:
        t0 = time.time()
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
            params={"lat": 18.5204, "lon": 73.8567, "appid": wkey, "units": "metric"}, timeout=10)
        elapsed = round(time.time() - t0, 2)
        if r.status_code == 200:
            d = r.json()
            ok(f"City: {d['name']} | Temp: {d['main']['temp']}°C | Humidity: {d['main']['humidity']}% ({elapsed}s)")
            results["weather"] = True
        else:
            fail(f"HTTP {r.status_code}: {r.json().get('message', r.text[:80])}")
            results["weather"] = False
    except Exception as e:
        fail(str(e)); results["weather"] = False

# ── 3. ISRIC SoilGrids (using rural Pune farmland coords) ───────────────
print(f"\n{BO}[3] ISRIC SoilGrids API (rural Pune farmland){W}")
try:
    t0 = time.time()
    # Using rural farmland near Pune (NOT city center) to guarantee non-null pH
    r = requests.get("https://rest.isric.org/soilgrids/v2.0/properties/query",
        params={"lat": 18.3, "lon": 74.1, "property": "phh2o", "depth": "0-5cm", "value": "mean"},
        timeout=25)
    elapsed = round(time.time() - t0, 2)
    if r.status_code == 200:
        data = r.json()
        raw_ph = data["properties"]["layers"][0]["depths"][0]["values"]["mean"]
        if raw_ph is not None:
            ok(f"Topsoil pH: {raw_ph / 10.0} | Source: ISRIC SoilGrids API ({elapsed}s)")
            results["soil"] = True
        else:
            info(f"API responded 200 but returned null pH for this coord ({elapsed}s)")
            info("This is normal for some locations — backend fallback will activate")
            results["soil"] = "fallback"
    else:
        fail(f"HTTP {r.status_code}")
        results["soil"] = False
except Exception as e:
    fail(str(e)); results["soil"] = False

# ── 4. Nominatim Geocoding (OpenStreetMap) ───────────────────────────────
print(f"\n{BO}[4] Nominatim Geocoding (OpenStreetMap){W}")
try:
    t0 = time.time()
    r = requests.get("https://nominatim.openstreetmap.org/search",
        params={"q": "Nagpur, India", "format": "json", "limit": 3, "countrycodes": "in"},
        headers={"User-Agent": "AgroSustain-HealthCheck/1.0"}, timeout=10)
    elapsed = round(time.time() - t0, 2)
    if r.status_code == 200 and r.json():
        top = r.json()[0]
        ok(f"Found: {top['display_name'][:60]}... | Lat: {float(top['lat']):.4f}, Lon: {float(top['lon']):.4f} ({elapsed}s)")
        results["geocoding"] = True
    else:
        fail("No results returned"); results["geocoding"] = False
except Exception as e:
    fail(str(e)); results["geocoding"] = False

# ── 5. Supabase connection ───────────────────────────────────────────────
print(f"\n{BO}[5] Supabase Database{W}")
surl = os.getenv("SUPABASE_URL")
skey = os.getenv("SUPABASE_SERVICE_KEY")
if not surl or not skey:
    fail("SUPABASE_URL or SUPABASE_SERVICE_KEY not in .env"); results["supabase"] = False
else:
    try:
        t0 = time.time()
        r = requests.get(f"{surl}/rest/v1/disease_diagnoses",
            headers={"apikey": skey, "Authorization": f"Bearer {skey}",
                     "Range": "0-0"}, timeout=10)
        elapsed = round(time.time() - t0, 2)
        if r.status_code in (200, 206, 416):  # 416 = empty table (range not satisfiable)
            ok(f"Supabase REST reachable | Table 'diagnoses' exists ({elapsed}s)")
            results["supabase"] = True
        else:
            fail(f"HTTP {r.status_code}: {r.text[:120]}")
            results["supabase"] = False
    except Exception as e:
        fail(str(e)); results["supabase"] = False

# ── Summary ───────────────────────────────────────────────────────────────
print(f"\n{BO}{B}{'='*55}{W}")
print(f"{BO}   Summary{W}")
print(f"{BO}{B}{'='*55}{W}")
labels = {
    "gemini":    "Gemini 2.5 Flash",
    "weather":   "OpenWeatherMap",
    "soil":      "ISRIC SoilGrids",
    "geocoding": "Nominatim Geocoding",
    "supabase":  "Supabase Database",
}
all_ok = True
for k, label in labels.items():
    v = results.get(k, False)
    if v is True:
        print(f"  {G}✔ {label}{W}")
    elif v == "fallback":
        print(f"  {Y}~ {label} (API up, fallback values used for urban areas){W}")
    else:
        print(f"  {R}✘ {label}{W}")
        all_ok = False

print()
if all_ok:
    print(f"  {G}{BO}All systems operational! AgroSustain is ready.{W}")
else:
    print(f"  {Y}{BO}Some checks failed — review output above.{W}")
print()
