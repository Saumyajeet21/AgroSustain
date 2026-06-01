"""
AgroSustain — Groq Vision Analyzer
Uses Groq's llama-4-scout-17b vision model to identify:
  - Crop / plant species (works for ANY crop, including out-of-dataset images)
  - Plant part visible (leaf, stem, root, whole plant, fruit)
  - Visible symptoms and likely disease
  - Severity estimate
  - Whether plant appears healthy

This is the universal fallback layer that works even when the image shows
wheat, rice, sugarcane or any crop not yet in the ResNet50 training data.
"""

import os
import base64
from pathlib import Path

# ── Groq Vision Model ─────────────────────────────────────────────────────────
_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# ── Structured prompt for consistent JSON-like output ─────────────────────────
_SYSTEM_PROMPT = (
    "You are an expert plant pathologist and agronomist specializing in Indian crops. "
    "When shown a plant image, you identify the crop species, visible plant parts, "
    "and any disease symptoms with high accuracy. "
    "You are familiar with all major Indian crops: wheat, rice, sugarcane, cotton, "
    "chickpea, mustard, maize, potato, tomato, onion, banana, mango, and more. "
    "Always respond in the exact structured format requested."
)

_USER_PROMPT = (
    "Analyze this plant image carefully and respond with ONLY the following fields, "
    "each on its own line:\n\n"
    "CROP: <crop/plant name, e.g. Wheat, Rice, Tomato, Unknown>\n"
    "PART: <plant part visible, e.g. Leaf, Stem, Root, Whole plant, Fruit, Seed>\n"
    "HEALTHY: <Yes or No>\n"
    "DISEASE: <specific disease name if unhealthy, else 'None'>\n"
    "SYMPTOMS: <brief description of visible symptoms, max 30 words>\n"
    "SEVERITY: <None / Mild / Moderate / Severe>\n"
    "CONFIDENCE: <your confidence in this diagnosis: Low / Medium / High>\n\n"
    "If no plant is visible in the image, respond:\n"
    "CROP: Not a plant image\n"
    "PART: None\n"
    "HEALTHY: Unknown\n"
    "DISEASE: None\n"
    "SYMPTOMS: No plant detected\n"
    "SEVERITY: None\n"
    "CONFIDENCE: High"
)


def _encode_image(image_path: str) -> tuple[str, str]:
    """Returns (base64_data, mime_type) for the image."""
    ext = Path(image_path).suffix.lower()
    mime_map = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".webp": "image/webp",
        ".gif":  "image/gif",
    }
    mime = mime_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data, mime


def _parse_response(text: str) -> dict:
    """Parses the structured text response into a dict."""
    result = {
        "crop":       "Unknown",
        "part":       "Unknown",
        "is_healthy": False,
        "disease":    "Unknown",
        "symptoms":   "",
        "severity":   "Unknown",
        "confidence": "Low",
    }
    for line in text.strip().splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key   = key.strip().upper()
        value = value.strip()
        if key == "CROP":
            result["crop"] = value
        elif key == "PART":
            result["part"] = value
        elif key == "HEALTHY":
            result["is_healthy"] = value.lower() in ("yes", "true", "1")
        elif key == "DISEASE":
            result["disease"] = value if value.lower() != "none" else "None"
        elif key == "SYMPTOMS":
            result["symptoms"] = value
        elif key == "SEVERITY":
            result["severity"] = value
        elif key == "CONFIDENCE":
            result["confidence"] = value
    return result


def analyze_plant_image(image_path: str, groq_api_key: str | None = None) -> dict:
    """
    Analyzes a plant image using Groq Vision (llama-4-scout-17b).

    Parameters
    ----------
    image_path   : str — absolute path to the image file
    groq_api_key : str — Groq API key (falls back to GROQ_API_KEY env var)

    Returns
    -------
    dict with keys:
        success      : bool
        crop         : str   — identified crop (e.g. "Wheat", "Rice", "Tomato")
        part         : str   — plant part visible (e.g. "Leaf", "Stem", "Root")
        is_healthy   : bool
        disease      : str   — disease name or "None"
        symptoms     : str   — brief symptom description
        severity     : str   — None / Mild / Moderate / Severe
        confidence   : str   — Low / Medium / High
        raw_response : str   — full model output (for debugging)
        error        : str   — only present on failure
    """
    api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return {"success": False, "error": "GROQ_API_KEY not set"}

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        img_data, mime_type = _encode_image(image_path)

        response = client.chat.completions.create(
            model=_VISION_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{img_data}"
                            },
                        },
                        {
                            "type": "text",
                            "text": _USER_PROMPT,
                        },
                    ],
                },
            ],
            max_tokens=300,
            temperature=0.1,   # low temp for consistent structured output
        )

        raw = response.choices[0].message.content or ""
        parsed = _parse_response(raw)

        return {
            "success":      True,
            "raw_response": raw,
            **parsed,
        }

    except Exception as e:
        return {"success": False, "error": f"Groq Vision error: {str(e)}"}


# ── Quick CLI test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")

    if len(sys.argv) < 2:
        print("Usage: python vision_analyzer.py <image_path>")
        sys.exit(1)

    result = analyze_plant_image(sys.argv[1])
    print("\n-- Groq Vision Analysis -------------------------")
    for k, v in result.items():
        if k != "raw_response":
            print(f"  {k:12s}: {v}")
    if result.get("raw_response"):
        print("\n-- Raw Response ---------------------------------")
        print(result["raw_response"])
