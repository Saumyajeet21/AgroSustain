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
load_dotenv()

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
    Full two-stage vision pipeline:
    1. YOLO detects and crops leaf regions
    2. ResNet50 classifies each leaf for disease
    3. Gemini generates natural language treatment advice
    Returns annotated image + diagnosis + Gemini advice
    """
    import google.generativeai as genai

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

    # Use the first (highest-confidence) leaf result as primary
    primary = classifications[0]

    # ── Stage C: Gemini Treatment Advice ──────────────────────────────────────
    gemini_advice = ""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")

        if primary["success"]:
            plant     = primary.get("plant",    "Unknown plant")
            condition = primary.get("condition","Unknown condition")
            conf      = primary.get("confidence", 0)

            if primary.get("is_healthy"):
                prompt = (
                    f"The {plant} plant appears healthy (confidence: {conf:.0f}%). "
                    "Give the farmer 3 brief tips to maintain this healthy condition. "
                    "Keep it friendly, plain English, under 150 words."
                )
            else:
                prompt = (
                    f"A {plant} plant has been diagnosed with {condition} "
                    f"(confidence: {conf:.0f}%). "
                    "Give the farmer: 1) What this disease is in simple terms, "
                    "2) Immediate actions to take, "
                    "3) Recommended treatment or fungicide/pesticide. "
                    "Be concise, practical, under 200 words."
                )

            response = gemini_model.generate_content(prompt)
            gemini_advice = response.text
        else:
            gemini_advice = "Could not classify the plant. Please upload a clearer image of the leaf."

    except Exception as e:
        gemini_advice = f"AI advice unavailable: {str(e)}"

    # ── Build Response ────────────────────────────────────────────────────────
    return {
        "success":          True,
        "job_id":           job_id,
        "num_leaves_found": detection["num_leaves"],
        "used_fallback":    detection["used_fallback"],
        "diagnosis":        primary if primary["success"] else {"error": "Classification failed"},
        "all_leaves":       classifications,
        "gemini_advice":    gemini_advice,
        "annotated_image_url": f"/api/disease/result/{job_id}/annotated",
    }


@app.get("/api/disease/result/{job_id}/annotated", tags=["Disease"])
def get_annotated_image(job_id: str):
    """Serves the annotated image with bounding boxes back to the frontend."""
    img_path = UPLOAD_DIR / job_id / "annotated.jpg"
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Result image not found")
    return FileResponse(str(img_path), media_type="image/jpeg")


# ── ROUTE 5: Gemini Agriculture Chatbot ───────────────────────────────────
@app.post("/api/chat", tags=["Chatbot"])
async def chat_with_gemini(body: ChatRequest):
    """
    Conversational AI chatbot powered by Google Gemini.
    Maintains conversation history for multi-turn dialogue.
    Specialized as an agricultural advisor.
    """
    import google.generativeai as genai

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        system_instruction = (
            "You are AgroBot, an expert agricultural advisor for Indian farmers. "
            "You specialize in: crop selection, soil health, pest management, plant diseases, "
            "farming techniques, weather impacts on crops, fertilizer recommendations, "
            "and sustainable farming practices. "
            "Keep responses concise, practical, and farmer-friendly. "
            "Use simple language. When discussing diseases or pests, always mention treatment options. "
            "If a question is unrelated to agriculture, gently redirect to farming topics."
        )

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
        )

        # Build conversation history for multi-turn support
        chat = model.start_chat(history=body.history)
        response = chat.send_message(body.message)
        reply = response.text

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
