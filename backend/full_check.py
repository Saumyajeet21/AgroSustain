"""
AgroSustain - Full End-to-End Project Health Check
Tests: ML Models, Backend Endpoints, Database Read/Write, All APIs
"""
import os, sys, json, pickle, time, requests, tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

G  = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; B = "\033[94m"; W = "\033[0m"; BO = "\033[1m"

def ok(msg):   print(f"  {G}[PASS]{W} {msg}")
def fail(msg): print(f"  {R}[FAIL]{W} {msg}")
def info(msg): print(f"  {Y}[INFO]{W} {msg}")
def section(title): print(f"\n{BO}{B}--- {title} ---{W}")

results = {}
BASE = Path(__file__).parent

print(f"\n{BO}{B}{'='*58}{W}")
print(f"{BO}   AgroSustain -- Full End-to-End Health Check{W}")
print(f"{BO}{B}{'='*58}{W}")

# ── 1. ML MODELS ────────────────────────────────────────────────────────────
section("1. ML MODELS")

# ResNet50 Disease Classifier
try:
    import torch
    import torch.nn as nn
    import torchvision.models as tv_models
    m = tv_models.resnet50()
    # Exact architecture from disease_classifier.py: Dropout -> Linear(2048,512) -> ReLU -> Linear(512,38)
    m.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(2048, 512),
        nn.ReLU(),
        nn.Linear(512, 38)
    )
    state = torch.load(BASE / "models/resnet50_disease.pth", map_location="cpu", weights_only=False)
    m.load_state_dict(state)
    m.eval()
    size_mb = round((BASE / "models/resnet50_disease.pth").stat().st_size / 1e6, 1)
    ok(f"ResNet50 Disease Classifier loaded ({size_mb} MB, 38 classes, Sequential head)")
    results["resnet"] = True
except Exception as e:
    fail(f"ResNet50: {e}")
    results["resnet"] = False

# YOLOv8 Leaf Detector
try:
    from ultralytics import YOLO
    yolo = YOLO(str(BASE / "models/yolo_leaf.pt"))
    size_mb = round((BASE / "models/yolo_leaf.pt").stat().st_size / 1e6, 1)
    ok(f"YOLOv8 Leaf Detector loaded ({size_mb} MB)")
    results["yolo"] = True
except Exception as e:
    fail(f"YOLOv8: {e}")
    results["yolo"] = False

# Crop Random Forest
try:
    with open(BASE / "models/crop_model.pkl", "rb") as f:
        crop_model = pickle.load(f)
    with open(BASE / "models/crop_classes.json") as f:
        crop_classes = json.load(f)
    ok(f"Crop RF Model loaded ({len(crop_classes)} crops: {', '.join(crop_classes[:4])}...)")
    results["crop_model"] = True
except Exception as e:
    fail(f"Crop model: {e}")
    results["crop_model"] = False

# Disease Classes JSON
try:
    with open(BASE / "models/disease_classes.json") as f:
        dc = json.load(f)
    ok(f"Disease classes JSON loaded ({len(dc)} disease labels)")
    results["disease_classes"] = True
except Exception as e:
    fail(f"Disease classes: {e}")
    results["disease_classes"] = False

# ── 2. CROP PREDICTION (in-process test) ──────────────────────────────────
section("2. CROP PREDICTION (In-Process Inference)")
try:
    import numpy as np
    # Test inference with typical Pune farmland values
    sample = np.array([[90, 42, 43, 28.0, 70.0, 6.8, 202.0]])
    prediction = crop_model.predict(sample)
    if isinstance(prediction[0], (int, float)):
        predicted_crop = crop_classes[int(prediction[0])]
    else:
        predicted_crop = str(prediction[0])
    ok(f"Crop prediction working -> Predicted: '{predicted_crop}'")
    results["crop_inference"] = True
except Exception as e:
    fail(f"Crop inference: {e}")
    results["crop_inference"] = False

# ── 3. BACKEND SERVER ENDPOINTS ────────────────────────────────────────────
section("3. BACKEND SERVER (http://localhost:8001)")
backend = "http://localhost:8001"

# Health check
try:
    r = requests.get(f"{backend}/", timeout=4)
    if r.status_code == 200:
        ok(f"FastAPI root endpoint reachable: {r.json()}")
        results["backend_health"] = True
    else:
        fail(f"HTTP {r.status_code}")
        results["backend_health"] = False
except Exception as e:
    fail(f"Backend not reachable at {backend} ({e})")
    info("Tip: Run 'uvicorn main:app --reload --port 8001' in backend/")
    results["backend_health"] = False

# Predict endpoint
if results.get("backend_health"):
    try:
        payload = {"lat": 18.52, "lon": 73.85, "N": 90, "P": 42, "K": 43,
                   "temperature": 28.0, "humidity": 70.0, "ph": 6.8, "rainfall": 202.0}
        r = requests.post(f"{backend}/api/crop/predict", json=payload, timeout=15)
        if r.status_code == 200:
            d = r.json()
            ok(f"/api/crop/predict OK -> Crop: {d.get('crop')}, Confidence: {round(d.get('confidence',0)*100,1)}%")
            results["predict_ep"] = True
        else:
            fail(f"/api/crop/predict HTTP {r.status_code}: {r.text[:100]}")
            results["predict_ep"] = False
    except Exception as e:
        fail(f"/predict: {e}")
        results["predict_ep"] = False

    # Chat endpoint
    try:
        r = requests.post(f"{backend}/api/chat",
            json={"message": "What is a good crop for black soil in Maharashtra?", "history": []},
            timeout=20)
        if r.status_code == 200:
            reply = r.json().get("reply", "")[:80]
            ok(f"/api/chat OK -> '{reply}...'")
            results["chat_ep"] = True
        else:
            fail(f"/api/chat HTTP {r.status_code}: {r.text[:100]}")
            results["chat_ep"] = False
    except Exception as e:
        fail(f"/chat: {e}")
        results["chat_ep"] = False

    # Economics endpoint
    try:
        r = requests.post(f"{backend}/api/economics/calculate",
            json={"crop": "rice", "farm_area_hectares": 2.0}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            ok(f"/api/economics/calculate OK -> {str(d)[:80]}")
            results["econ_ep"] = True
        else:
            fail(f"/api/economics/calculate HTTP {r.status_code}: {r.text[:100]}")
            results["econ_ep"] = False
    except Exception as e:
        fail(f"/economics: {e}")
        results["econ_ep"] = False
else:
    info("Skipping endpoint tests (backend not running)")
    results["predict_ep"] = results["chat_ep"] = results["econ_ep"] = "skipped"

# ── 4. DATABASE (SUPABASE) ─────────────────────────────────────────────────
section("4. SUPABASE DATABASE")
surl = os.getenv("SUPABASE_URL")
skey = os.getenv("SUPABASE_SERVICE_KEY")

if not surl or not skey:
    fail("SUPABASE_URL or SUPABASE_SERVICE_KEY missing in .env")
    results["db_read"] = results["db_write"] = False
else:
    headers = {"apikey": skey, "Authorization": f"Bearer {skey}",
               "Content-Type": "application/json", "Prefer": "return=representation"}

    # Read
    try:
        r = requests.get(f"{surl}/rest/v1/disease_diagnoses",
            headers={**headers, "Range": "0-4"}, timeout=10)
        if r.status_code in (200, 206, 416):
            count_info = f"{len(r.json())} recent rows" if r.status_code in (200, 206) else "table empty (fresh)"
            ok(f"DB READ: disease_diagnoses accessible ({count_info})")
            results["db_read"] = True
        else:
            fail(f"DB READ HTTP {r.status_code}: {r.text[:120]}")
            results["db_read"] = False
    except Exception as e:
        fail(f"DB READ: {e}")
        results["db_read"] = False

    # Write test row then delete it
    try:
        # Write test row using correct table schema: plant, condition, is_healthy, confidence, gemini_advice, num_leaves
        test_row = {
            "plant": "HealthCheck",
            "condition": "none",
            "is_healthy": True,
            "confidence": 0.99,
            "gemini_advice": "System health check test row",
            "num_leaves": 0
        }
        r = requests.post(f"{surl}/rest/v1/disease_diagnoses",
            headers=headers, json=test_row, timeout=10)
        if r.status_code in (200, 201):
            row = r.json()
            row_id = row[0]["id"] if isinstance(row, list) else row.get("id")
            ok(f"DB WRITE: Inserted test row (id={row_id})")
            # Clean up
            requests.delete(f"{surl}/rest/v1/disease_diagnoses",
                headers={**headers, "id": f"eq.{row_id}"}, params={"id": f"eq.{row_id}"}, timeout=10)
            ok("DB DELETE: Cleaned up test row")
            results["db_write"] = True
        else:
            fail(f"DB WRITE HTTP {r.status_code}: {r.text[:150]}")
            results["db_write"] = False
    except Exception as e:
        fail(f"DB WRITE: {e}")
        results["db_write"] = False

# ── 5. EXTERNAL APIs ───────────────────────────────────────────────────────
section("5. EXTERNAL APIs")
gkey = os.getenv("GEMINI_API_KEY")
wkey = os.getenv("OPENWEATHER_API_KEY")

# Gemini
try:
    t0 = time.time()
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        params={"key": gkey},
        json={"contents": [{"parts": [{"text": "Reply with only: AGROSUSTAIN_OK"}]}]},
        timeout=20)
    elapsed = round(time.time()-t0, 2)
    if r.status_code == 200:
        reply = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        ok(f"Gemini 2.5 Flash: '{reply}' ({elapsed}s)")
        results["gemini"] = True
    else:
        fail(f"Gemini HTTP {r.status_code}"); results["gemini"] = False
except Exception as e:
    fail(f"Gemini: {e}"); results["gemini"] = False

# OpenWeather
try:
    t0 = time.time()
    r = requests.get("https://api.openweathermap.org/data/2.5/weather",
        params={"lat": 19.0760, "lon": 72.8777, "appid": wkey, "units": "metric"}, timeout=10)
    elapsed = round(time.time()-t0, 2)
    if r.status_code == 200:
        d = r.json()
        ok(f"OpenWeather: {d['name']} {d['main']['temp']}C, Humidity {d['main']['humidity']}% ({elapsed}s)")
        results["weather"] = True
    else:
        fail(f"OpenWeather HTTP {r.status_code}: {r.json().get('message')}"); results["weather"] = False
except Exception as e:
    fail(f"OpenWeather: {e}"); results["weather"] = False

# ISRIC SoilGrids
try:
    t0 = time.time()
    r = requests.get("https://rest.isric.org/soilgrids/v2.0/properties/query",
        params={"lat": 17.5, "lon": 78.5, "property": "phh2o", "depth": "0-5cm", "value": "mean"},
        timeout=25)
    elapsed = round(time.time()-t0, 2)
    if r.status_code == 200:
        raw = r.json()["properties"]["layers"][0]["depths"][0]["values"]["mean"]
        ph = raw / 10.0 if raw else "null (urban area)"
        ok(f"ISRIC SoilGrids: pH={ph} for Hyderabad farmland ({elapsed}s)")
        results["soil"] = True
    else:
        fail(f"ISRIC HTTP {r.status_code}"); results["soil"] = False
except Exception as e:
    fail(f"ISRIC: {e}"); results["soil"] = False

# Nominatim
try:
    t0 = time.time()
    r = requests.get("https://nominatim.openstreetmap.org/search",
        params={"q": "Mumbai, India", "format": "json", "limit": 1},
        headers={"User-Agent": "AgroSustain/1.0"}, timeout=10)
    elapsed = round(time.time()-t0, 2)
    if r.status_code == 200 and r.json():
        d = r.json()[0]
        ok(f"Nominatim: lat={float(d['lat']):.3f}, lon={float(d['lon']):.3f} for Mumbai ({elapsed}s)")
        results["nominatim"] = True
    else:
        fail("Nominatim: no results"); results["nominatim"] = False
except Exception as e:
    fail(f"Nominatim: {e}"); results["nominatim"] = False

# ── SUMMARY ─────────────────────────────────────────────────────────────────
print(f"\n{BO}{B}{'='*58}{W}")
print(f"{BO}   SUMMARY{W}")
print(f"{BO}{B}{'='*58}{W}")

categories = {
    "ML Models": {
        "ResNet50 Disease Classifier": results.get("resnet"),
        "YOLOv8 Leaf Detector":        results.get("yolo"),
        "Crop RF Model":               results.get("crop_model"),
        "Disease Classes JSON":        results.get("disease_classes"),
        "Crop Inference Test":         results.get("crop_inference"),
    },
    "Backend Endpoints": {
        "FastAPI Health":   results.get("backend_health"),
        "/predict":         results.get("predict_ep"),
        "/chat (Gemini)":   results.get("chat_ep"),
        "/economics":       results.get("econ_ep"),
    },
    "Database (Supabase)": {
        "DB Read":  results.get("db_read"),
        "DB Write": results.get("db_write"),
    },
    "External APIs": {
        "Gemini 2.5 Flash":    results.get("gemini"),
        "OpenWeatherMap":      results.get("weather"),
        "ISRIC SoilGrids":     results.get("soil"),
        "Nominatim Geocoding": results.get("nominatim"),
    }
}

total_pass = total_fail = total_skip = 0
for cat, items in categories.items():
    print(f"\n  {BO}{cat}{W}")
    for name, status in items.items():
        if status is True:
            print(f"    {G}[✔]{W} {name}")
            total_pass += 1
        elif status == "skipped":
            print(f"    {Y}[~]{W} {name} (skipped — backend offline)")
            total_skip += 1
        else:
            print(f"    {R}[✘]{W} {name}")
            total_fail += 1

print(f"\n{BO}{B}{'='*58}{W}")
print(f"  Result: {G}{total_pass} passed{W}, {R}{total_fail} failed{W}, {Y}{total_skip} skipped{W}")
if total_fail == 0:
    print(f"  {G}{BO}All systems operational! AgroSustain is fully ready.{W}")
elif total_fail <= 2:
    print(f"  {Y}{BO}Minor issues detected — see above for details.{W}")
else:
    print(f"  {R}{BO}Multiple failures — fix above before production.{W}")
print(f"{BO}{B}{'='*58}{W}\n")
