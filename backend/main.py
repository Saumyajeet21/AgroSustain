"""
AgroSustain — FastAPI Backend
Main application entry point with all API routes.

Run: uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
Or:  python backend/main.py
"""

import os
import uuid
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

# ── Internal module imports ──────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))   # ensure 'backend' is on path

from utils.weather_api import fetch_live_weather
from utils.soil_api import fetch_live_soil_data
from ml.crop_predictor import predict_crop
from ml.economics import calculate_economics
from utils.supabase_db import (
    log_crop_prediction, log_disease_diagnosis, log_chat_message, get_recent_predictions
)

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgroSustain API",
    description="AI-driven crop recommendation and plant disease diagnosis engine.",
    version="1.0.0",
    docs_url="/docs",
)

# ── CORS (allow React frontend from localhost) ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Upload directory for disease images ───────────────────────────────────────
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ── Groq advice cache (plant+condition → advice text) ────────────────────────
# Prevents redundant API calls for the same diagnosis (e.g. same disease seen twice).
_GROQ_ADVICE_CACHE: dict[str, str] = {}

# ── Static healthy-plant responses (no API call needed) ───────────────────────
_HEALTHY_TIPS = (
    "Your plant looks healthy! 🌱 Here are 3 tips to keep it that way:\n"
    "1. **Water consistently** — avoid both over- and under-watering; check soil moisture before watering.\n"
    "2. **Monitor regularly** — inspect leaves weekly for early signs of spots, discolouration, or pests.\n"
    "3. **Feed appropriately** — apply a balanced fertiliser once a month during the growing season."
)

# ── Pre-warm ML models at startup (avoids cold-load delay on first request) ───
@app.on_event("startup")
async def warmup_models():
    import asyncio, threading
    def _warmup():
        try:
            print("[Startup] Pre-warming YOLO leaf detector...")
            from ml.leaf_detector import _ensure_loaded as yolo_load
            yolo_load()
            print("[Startup] YOLO ready.")
        except Exception as e:
            print(f"[Startup] YOLO warmup skipped: {e}")
        try:
            print("[Startup] Pre-warming ResNet50 disease classifier...")
            from ml.disease_classifier import _ensure_loaded as resnet_load
            resnet_load()
            print("[Startup] ResNet50 ready.")
        except Exception as e:
            print(f"[Startup] ResNet50 warmup skipped: {e}")
    thread = threading.Thread(target=_warmup, daemon=True)
    thread.start()


# ─────────────────────────────────────────────────────────────────────────────
# REQUEST / RESPONSE SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class CropPredictRequest(BaseModel):
    lat: float
    lon: float
    N: float | None = None
    P: float | None = None
    K: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    ph: float | None = None
    rainfall: float | None = None

class EconomicsRequest(BaseModel):
    crop: str
    farm_area_hectares: float

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    history: list = []  # [{"role": "user"|"model", "parts": [{"text": "..."}]}]


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "AgroSustain API is running", "version": "1.0.0"}


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ── ROUTE 1: Live Environment Data ────────────────────────────────────────────
@app.get("/api/environment/live", tags=["Environment"])
def get_live_environment(lat: float, lon: float):
    """
    Fetches live weather + soil data for a given GPS location.
    Used by the frontend 'Auto-Fetch' button.
    """
    weather = fetch_live_weather(lat, lon)
    soil    = fetch_live_soil_data(lat, lon)

    if not weather["success"]:
        raise HTTPException(status_code=502, detail=f"Weather API: {weather['error']}")

    # Soil pH is optional — use a typical default if unavailable
    soil_ph = soil.get("soil_ph", 6.5) if soil.get("success") else 6.5

    # Approximate NPK from soil (rough global averages — SoilGrids extended fetch coming later)
    return {
        "success":     True,
        "location":    weather.get("location", "Unknown"),
        "lat":         lat,
        "lon":         lon,
        "temperature": weather["temperature"],
        "humidity":    weather["humidity"],
        "rainfall":    weather["rainfall"],
        "ph":          soil_ph,
        "N":           50,   # kg/ha — placeholder until SoilGrids NPK integration
        "P":           30,
        "K":           40,
        "soil_source": soil.get("source", "default"),
    }


# ── ROUTE 2: Crop Prediction ──────────────────────────────────────────────────
@app.post("/api/crop/predict", tags=["Crop"])
def predict_crop_route(body: CropPredictRequest):
    """
    Predicts the best crop to grow.
    If lat/lon provided without overrides, auto-fetches live data first.
    """
    # Step 1: Get live data for auto-fetch
    env = get_live_environment(body.lat, body.lon)

    # Step 2: Use manual overrides where provided, else live data
    N           = body.N           if body.N           is not None else env["N"]
    P           = body.P           if body.P           is not None else env["P"]
    K           = body.K           if body.K           is not None else env["K"]
    temperature = body.temperature if body.temperature is not None else env["temperature"]
    humidity    = body.humidity    if body.humidity    is not None else env["humidity"]
    ph          = body.ph          if body.ph          is not None else env["ph"]
    rainfall    = body.rainfall    if body.rainfall    is not None else env["rainfall"]

    # Step 3: Run XGBoost inference
    result = predict_crop(N, P, K, temperature, humidity, ph, rainfall)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    # Log to Supabase (non-blocking silent failure)
    log_crop_prediction(
        lat=body.lat, lon=body.lon,
        location=env.get("location", ""),
        crop=result["crop"], confidence=result["confidence"],
        N=N, P=P, K=K,
        temperature=temperature, humidity=humidity,
        ph=ph, rainfall=rainfall,
        top3=result["top3"],
    )

    return {
        **result,
        "inputs_used": {
            "N": N, "P": P, "K": K,
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph,
            "rainfall": rainfall,
        },
        "location": env.get("location"),
    }


# ── ROUTE 3: Economics Calculator ─────────────────────────────────────────────
@app.post("/api/economics/calculate", tags=["Economics"])
def calculate_economics_route(body: EconomicsRequest):
    """
    Calculates financial projection for a crop on a given farm size.
    """
    result = calculate_economics(body.crop, body.farm_area_hectares)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Calculation failed"))
    return result


# ── ROUTE 4: Plant Disease Diagnosis ──────────────────────────────────────────
@app.post("/api/disease/diagnose", tags=["Disease"])
async def diagnose_disease(file: UploadFile = File(...)):
    """
    4-stage Plant Doctor pipeline:
    Stage A │ YOLO   — detects plant regions (leaf / stem / root / whole plant)
    Stage B │ Groq Vision — identifies crop + disease for ANY image (universal)
    Stage C │ ResNet50   — precise disease classification for known crops
    Stage D │ Groq LLM   — generates natural-language treatment advice

    Works for wheat, rice, and any crop even if not in ResNet50 training data.
    """
    # Save uploaded image
    job_id    = str(uuid.uuid4())[:8]
    job_dir   = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    img_path  = job_dir / f"input{Path(file.filename).suffix}"
    with open(img_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # ── Stage A: YOLO Leaf Detection ──────────────────────────────────────────
    from ml.leaf_detector import detect_and_crop_leaves
    detection = detect_and_crop_leaves(str(img_path), output_dir=str(job_dir))

    if not detection["success"]:
        raise HTTPException(status_code=500, detail=f"Leaf detection failed: {detection['error']}")

    # ── Stage B: ResNet50 Classification ─────────────────────────────────────
    from ml.disease_classifier import classify_disease

    classifications = []
    for crop_path in detection["cropped_paths"]:
        cls = classify_disease(crop_path)
        classifications.append(cls)

    if not classifications:
        raise HTTPException(status_code=500, detail="No classifications produced")

    # Use the first (highest-confidence) region result as primary for ResNet
    # ALSO run ResNet on the full input image (often gives higher confidence than small crops)
    resnet_primary = classifications[0] if classifications else {"success": False}
    try:
        full_cls = classify_disease(str(img_path))
        if full_cls.get("success") and full_cls.get("confidence", 0) > resnet_primary.get("confidence", 0):
            print(f"[ResNet] Full-image result better ({full_cls['confidence']:.1f}% vs "
                  f"{resnet_primary.get('confidence', 0):.1f}%) — using full-image classification")
            resnet_primary = full_cls
        else:
            print(f"[ResNet] Crop result used ({resnet_primary.get('confidence', 0):.1f}%)")
    except Exception as re:
        print(f"[ResNet] Full-image classification error: {re}")

    # ── Stage B: Groq Vision — universal crop + disease identification ─────────
    # Works for ANY crop/plant part including wheat, rice, stems, roots.
    # Runs independently of ResNet50 — does not require crop to be in training data.
    vision_result = {"success": False, "crop": "Unknown", "disease": "Unknown",
                     "is_healthy": False, "symptoms": "", "part": "Unknown",
                     "severity": "Unknown", "confidence": "Low"}
    try:
        from ml.vision_analyzer import analyze_plant_image
        print(f"[Stage B] Running Groq Vision on: {img_path}")
        vision_result = analyze_plant_image(str(img_path), groq_api_key=os.getenv("GROQ_API_KEY"))
        if vision_result.get("success"):
            print(f"[Vision] Crop={vision_result['crop']} | Part={vision_result['part']} | "
                  f"Disease={vision_result['disease']} | Confidence={vision_result['confidence']}")
        else:
            print(f"[Vision] Failed: {vision_result.get('error', 'unknown')}")
    except Exception as ve:
        print(f"[Stage B] Groq Vision error: {ve}")

    # ── Stage C: Merge ResNet + Vision results ────────────────────────────────
    # THREE signals guide the decision:
    #   1. crops_agree       → both models agree → use ResNet for precise disease label
    #   2. yolo_found_regions → YOLO found actual plant parts (not full-image fallback)
    #                           ResNet was trained on plant-part crops → more reliable here
    #   3. resnet_in_domain  → ResNet was specifically trained on this crop type
    #
    # WHY this fixes Apple vs Mango:
    #   Apple image  → YOLO finds 3 leaf regions (not fallback)
    #                  ResNet correctly identifies Apple (domain crop)
    #                  Vision wrongly says Mango (non-domain) → ResNet wins ✓
    #   Mango image  → YOLO finds nothing → uses full-image fallback
    #                  ResNet wrongly says Strawberry (domain)
    #                  Vision correctly says Mango (non-domain) → Vision wins ✓
    resnet_conf  = resnet_primary.get("confidence", 0) if resnet_primary.get("success") else 0
    resnet_crop  = resnet_primary.get("plant", "").lower() if resnet_primary.get("success") else ""
    vision_crop  = vision_result.get("crop", "Unknown").lower()
    vision_ok    = vision_result.get("success", False)

    # Crops ResNet was specifically trained on (PlantVillage)
    _RESNET_DOMAIN = {
        "apple", "blueberry", "cherry", "corn", "maize", "grape", "orange",
        "peach", "pepper", "potato", "raspberry", "soybean", "squash",
        "strawberry", "tomato",
    }

    def _crops_match(a: str, b: str) -> bool:
        """True if either crop name contains the other (handles partial matches)."""
        a, b = a.strip().lower(), b.strip().lower()
        return bool(a and b and (a in b or b in a))

    crops_agree        = _crops_match(resnet_crop, vision_crop)
    resnet_in_domain   = any(_crops_match(resnet_crop, d) for d in _RESNET_DOMAIN)
    vision_in_domain   = any(_crops_match(vision_crop, d) for d in _RESNET_DOMAIN)
    yolo_found_regions = not detection.get("used_fallback", True)

    # ResNet wins when:
    #  Case 1: Both models agree on crop (ResNet gives precise disease label)
    #  Case 2: YOLO found real plant regions + ResNet confident on domain crop
    #          + Vision predicts non-domain crop (Vision confused by fruit/hand context)
    #  Case 3: Vision completely failed (ResNet is only signal)
    use_resnet = (
        resnet_primary.get("success") and resnet_conf >= 50.0
        and resnet_in_domain
        and (
            crops_agree                                          # Case 1: both agree
            or not vision_ok                                     # Case 3: vision failed
            or (yolo_found_regions and not vision_in_domain)    # Case 2: YOLO found leaves, Vision sees non-domain crop
        )
    )

    if use_resnet:
        final_plant     = resnet_primary["plant"]
        final_condition = resnet_primary["condition"]
        final_healthy   = resnet_primary["is_healthy"]
        final_conf      = resnet_conf
        diagnosis_source = "resnet50"
    elif vision_ok:
        final_plant     = vision_result["crop"]
        final_condition = vision_result["disease"] if not vision_result["is_healthy"] else "Healthy"
        final_healthy   = vision_result["is_healthy"]
        final_conf      = {"High": 85.0, "Medium": 65.0, "Low": 40.0}.get(vision_result["confidence"], 50.0)
        diagnosis_source = "groq_vision"
    else:
        final_plant     = "Unknown"
        final_condition = "Unknown"
        final_healthy   = False
        final_conf      = 0.0
        diagnosis_source = "none"

    print(f"[Stage C] yolo_regions={yolo_found_regions} | crops_agree={crops_agree} | "
          f"resnet_domain={resnet_in_domain} | vision_domain={vision_in_domain} | "
          f"resnet_conf={resnet_conf:.1f}% | use_resnet={use_resnet}")

    # ── Build merged diagnosis object ─────────────────────────────────────────
    merged_diagnosis = {
        "success":          True,
        "plant":            final_plant,
        "condition":        final_condition,
        "is_healthy":       final_healthy,
        "confidence":       final_conf,
        "diagnosis_source": diagnosis_source,
        # Vision extras
        "plant_part":       vision_result.get("part", detection.get("detected_parts", ["Unknown"])[0]),
        "symptoms":         vision_result.get("symptoms", ""),
        "severity":         vision_result.get("severity", "Unknown"),
        # ResNet extras (may be empty if vision was used)
        "resnet_disease":   resnet_primary.get("disease", "") if resnet_primary.get("success") else "",
        "resnet_confidence": resnet_conf,
        "top3":             resnet_primary.get("top3", []),
    }

    # ── Stage D: Groq LLM Treatment Advice ───────────────────────────────────
    ai_advice = ""
    try:
        if final_plant.lower() in ("not a plant image", "unknown") and not vision_ok:
            ai_advice = "Could not identify a plant in this image. Please upload a clear photo of a plant."

        elif final_healthy:
            ai_advice = _HEALTHY_TIPS

        else:
            cache_key = f"{final_plant.lower()}::{final_condition.lower()}"
            if cache_key in _GROQ_ADVICE_CACHE:
                print(f"[Groq Cache HIT] {cache_key}")
                ai_advice = _GROQ_ADVICE_CACHE[cache_key]
            else:
                print(f"[Groq Cache MISS] Calling Groq API for: {cache_key}")
                from groq import Groq
                groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

                # Build a rich prompt using both vision and ResNet info
                symptoms_text = vision_result.get("symptoms", "")
                severity_text = vision_result.get("severity", "")
                part_text     = vision_result.get("part", "")

                prompt = (
                    f"A {final_plant} plant has been diagnosed with '{final_condition}' "
                    f"(confidence: {final_conf:.0f}%). "
                )
                if symptoms_text:
                    prompt += f"Visible symptoms: {symptoms_text}. "
                if severity_text and severity_text != "None":
                    prompt += f"Severity: {severity_text}. "
                if part_text:
                    prompt += f"Affected part: {part_text}. "
                prompt += (
                    "Give the Indian farmer: "
                    "1) What this disease is, "
                    "2) Immediate actions to take today, "
                    "3) Recommended treatment (include common Indian pesticide/fungicide names). "
                    "Be concise, practical, under 200 words."
                )

                chat_completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=350,
                )
                ai_advice = chat_completion.choices[0].message.content
                _GROQ_ADVICE_CACHE[cache_key] = ai_advice

    except Exception as e:
        ai_advice = f"AI advice unavailable: {str(e)}"

    # ── Build Response ────────────────────────────────────────────────────────
    return {
        "success":             True,
        "job_id":              job_id,
        "num_leaves_found":    detection["num_leaves"],
        "used_fallback":       detection["used_fallback"],
        "detected_parts":      detection.get("detected_parts", []),
        "diagnosis":           merged_diagnosis,
        "vision_analysis":     {
            "crop":       vision_result.get("crop"),
            "part":       vision_result.get("part"),
            "disease":    vision_result.get("disease"),
            "symptoms":   vision_result.get("symptoms"),
            "severity":   vision_result.get("severity"),
            "confidence": vision_result.get("confidence"),
        },
        "all_leaves":          classifications,
        "gemini_advice":       ai_advice,   # key kept for frontend compatibility
        "annotated_image_url": f"/api/disease/result/{job_id}/annotated",
    }


@app.get("/api/disease/result/{job_id}/annotated", tags=["Disease"])
def get_annotated_image(job_id: str):
    """Serves the annotated image with bounding boxes back to the frontend."""
    img_path = UPLOAD_DIR / job_id / "annotated.jpg"
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Result image not found")
    return FileResponse(str(img_path), media_type="image/jpeg")


# ── ROUTE 5: AgroBot Chatbot (powered by Groq) ────────────────────────────
@app.post("/api/chat", tags=["Chatbot"])
async def chat_with_groq(body: ChatRequest):
    """
    Conversational AI chatbot powered by Groq (Llama 3.3 70B Versatile).
    Maintains conversation history for multi-turn dialogue.
    Specialized as an agricultural advisor.
    """
    from groq import Groq

    # ── Guard: reject trivially short or empty messages ───────────────────────
    if not body.message or len(body.message.strip()) < 3:
        return {
            "success": False,
            "reply": "Please enter a meaningful question so AgroBot can help you.",
            "session_id": body.session_id,
        }

    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        system_instruction = (
            "You are AgroBot, an expert agricultural advisor for Indian farmers. "
            "You specialize in: crop selection, soil health, pest management, plant diseases, "
            "farming techniques, weather impacts on crops, fertilizer recommendations, "
            "and sustainable farming practices. "
            "Keep responses concise, practical, and farmer-friendly. "
            "Use simple language. When discussing diseases or pests, always mention treatment options. "
            "If a question is unrelated to agriculture, gently redirect to farming topics."
        )

        # Build messages list from history + new user message
        # Groq uses the OpenAI-compatible format: [{"role": ..., "content": ...}]
        messages = [{"role": "system", "content": system_instruction}]
        for h in body.history:
            role = h.get("role", "user")
            if role == "model":          # Gemini used "model"; Groq uses "assistant"
                role = "assistant"
            text = h.get("parts", [{}])[0].get("text", "") if h.get("parts") else h.get("content", "")
            if text:
                messages.append({"role": role, "content": text})
        # Append the new user message
        messages.append({"role": "user", "content": body.message})

        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
        )
        reply = chat_completion.choices[0].message.content

        # Log to Supabase
        log_chat_message(body.session_id, "user", body.message)
        log_chat_message(body.session_id, "assistant", reply)

        return {
            "success": True,
            "reply": reply,
            "session_id": body.session_id,
        }

    except Exception as e:
        return {"success": False, "reply": f"AgroBot is temporarily unavailable: {str(e)}", "session_id": body.session_id}


# ── ROUTE 6: Recent Predictions History ───────────────────────────────────
@app.get("/api/history/predictions", tags=["History"])
def get_prediction_history(limit: int = 10):
    """Returns recent crop predictions from Supabase."""
    return {"predictions": get_recent_predictions(limit)}


# ─────────────────────────────────────────────────────────────────────────────
# DEV ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)

