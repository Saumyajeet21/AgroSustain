"""
AgroSustain — Crop Prediction Inference Module
Uses pre-trained XGBoost model to recommend the best crop based on environmental inputs.
"""

import os
import pickle
import json
import numpy as np

# ── Resolve absolute paths relative to this file ────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
_MODELS_DIR = os.path.join(_BASE_DIR, "models")

_MODEL_PATH = os.path.join(_MODELS_DIR, "crop_model.pkl")
_ENCODER_PATH = os.path.join(_MODELS_DIR, "label_encoder.pkl")
_CLASSES_PATH = os.path.join(_MODELS_DIR, "crop_classes.json")

# ── Load once at module import (cached in memory) ────────────────────────────
with open(_MODEL_PATH, "rb") as f:
    _model = pickle.load(f)

with open(_ENCODER_PATH, "rb") as f:
    _label_encoder = pickle.load(f)

with open(_CLASSES_PATH, "r") as f:
    _crop_classes = json.load(f)


def predict_crop(
    N: float,
    P: float,
    K: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> dict:
    """
    Predicts the optimal crop for the given environmental parameters.

    Parameters
    ----------
    N           : Nitrogen content in soil (kg/ha)
    P           : Phosphorus content in soil (kg/ha)
    K           : Potassium content in soil (kg/ha)
    temperature : Average temperature in °C
    humidity    : Relative humidity in %
    ph          : Soil pH (0–14)
    rainfall    : Annual rainfall in mm

    Returns
    -------
    dict with keys:
        - success       : bool
        - crop          : str  (predicted crop name)
        - confidence    : float (0–100 %)
        - top3          : list of {crop, confidence} for top-3 predictions
        - error         : str  (only when success=False)
    """
    try:
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]], dtype=float)

        # Raw class probabilities from XGBoost
        proba = _model.predict_proba(features)[0]

        # Top prediction
        top_idx = int(np.argmax(proba))
        top_crop = _label_encoder.inverse_transform([top_idx])[0]
        top_conf = round(float(proba[top_idx]) * 100, 2)

        # Top-3 predictions
        top3_indices = np.argsort(proba)[::-1][:3]
        top3 = [
            {
                "crop": _label_encoder.inverse_transform([int(i)])[0],
                "confidence": round(float(proba[i]) * 100, 2),
            }
            for i in top3_indices
        ]

        return {
            "success": True,
            "crop": top_crop,
            "confidence": top_conf,
            "top3": top3,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Quick self-test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Typical rice-growing conditions
    result = predict_crop(
        N=90, P=42, K=43,
        temperature=20.9,
        humidity=82.0,
        ph=6.5,
        rainfall=202.9
    )
    print("[OK] Prediction:", result)
