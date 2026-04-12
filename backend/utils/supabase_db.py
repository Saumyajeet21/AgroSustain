"""
AgroSustain — Supabase Database Integration
Handles logging predictions, diagnoses, and chat history to Supabase.

Tables needed (run setup_tables.sql in Supabase SQL editor):
    - crop_predictions
    - disease_diagnoses
    - chat_history
"""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

_supabase_client = None


def _get_client():
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_KEY")
            if not url or not key:
                return None
            _supabase_client = create_client(url, key)
        except Exception as e:
            print(f"[Supabase] Connection failed: {e}")
            return None
    return _supabase_client


def log_crop_prediction(
    lat: float, lon: float, location: str,
    crop: str, confidence: float,
    N: float, P: float, K: float,
    temperature: float, humidity: float,
    ph: float, rainfall: float,
    top3: list
) -> str | None:
    """Logs a crop prediction to Supabase. Returns the inserted row id."""
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.table("crop_predictions").insert({
            "lat":         lat,
            "lon":         lon,
            "location":    location,
            "crop":        crop,
            "confidence":  confidence,
            "N": N, "P": P, "K": K,
            "temperature": temperature,
            "humidity":    humidity,
            "ph":          ph,
            "rainfall":    rainfall,
            "top3":        top3,
            "created_at":  datetime.now(timezone.utc).isoformat(),
        }).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        print(f"[Supabase] log_crop_prediction error: {e}")
        return None


def log_disease_diagnosis(
    plant: str, condition: str,
    is_healthy: bool, confidence: float,
    gemini_advice: str, num_leaves: int
) -> str | None:
    """Logs a disease diagnosis to Supabase."""
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.table("disease_diagnoses").insert({
            "plant":         plant,
            "condition":     condition,
            "is_healthy":    is_healthy,
            "confidence":    confidence,
            "gemini_advice": gemini_advice,
            "num_leaves":    num_leaves,
            "created_at":    datetime.now(timezone.utc).isoformat(),
        }).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        print(f"[Supabase] log_disease_diagnosis error: {e}")
        return None


def log_chat_message(session_id: str, role: str, message: str) -> None:
    """Logs a chatbot message to Supabase."""
    client = _get_client()
    if not client:
        return
    try:
        client.table("chat_history").insert({
            "session_id": session_id,
            "role":       role,
            "message":    message,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        print(f"[Supabase] log_chat_message error: {e}")


def get_recent_predictions(limit: int = 10) -> list:
    """Fetches recent crop predictions from Supabase."""
    client = _get_client()
    if not client:
        return []
    try:
        resp = client.table("crop_predictions") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"[Supabase] get_recent_predictions error: {e}")
        return []
