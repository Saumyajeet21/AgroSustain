"""
AgroSustain — Disease Classifier Inference Module
Loads the fine-tuned ResNet50 model and classifies plant disease from a leaf image.
"""

import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ── Config ───────────────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
_MODELS_DIR  = os.path.join(_BASE_DIR, "models")
_MODEL_PATH  = os.path.join(_MODELS_DIR, "resnet50_disease.pth")
_CLASSES_PATH = os.path.join(_MODELS_DIR, "disease_classes.json")

_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Image Preprocessing Pipeline ─────────────────────────────────────────────
_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _load_model(num_classes: int) -> nn.Module:
    """Builds the ResNet50 architecture and loads saved weights."""
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Linear(512, num_classes),
    )
    model.load_state_dict(torch.load(_MODEL_PATH, map_location=_DEVICE))
    model.eval()
    return model.to(_DEVICE)


# ── Lazy-load at first call (avoids import-time failures before training) ─────
_model       = None
_class_names = None


def _ensure_loaded():
    global _model, _class_names
    if _model is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {_MODEL_PATH}. "
                "Run backend/ml/train_resnet50.py first."
            )
        with open(_CLASSES_PATH, "r") as f:
            _class_names = json.load(f)
        _model = _load_model(len(_class_names))


def classify_disease(image_path: str) -> dict:
    """
    Classifies plant disease from an image file path.

    Parameters
    ----------
    image_path : str — absolute path to the leaf image (JPG/PNG)

    Returns
    -------
    dict with keys:
        - success       : bool
        - disease       : str  (predicted class name, e.g. 'Tomato___Early_blight')
        - plant         : str  (parsed plant name, e.g. 'Tomato')
        - condition     : str  (parsed condition, e.g. 'Early blight')
        - is_healthy    : bool
        - confidence    : float (0–100 %)
        - top3          : list of {disease, confidence}
        - error         : str  (only when success=False)
    """
    try:
        _ensure_loaded()

        img = Image.open(image_path).convert("RGB")
        tensor = _transform(img).unsqueeze(0).to(_DEVICE)

        with torch.no_grad():
            logits = _model(tensor)
            probs  = torch.softmax(logits, dim=1)[0]

        top3_vals, top3_idxs = torch.topk(probs, 3)

        top_class = _class_names[top3_idxs[0].item()]
        top_conf  = round(top3_vals[0].item() * 100, 2)

        # Parse class name like "Tomato___Early_blight" -> plant + condition
        parts = top_class.split("___")
        plant     = parts[0].replace("_", " ") if len(parts) > 0 else top_class
        condition = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
        is_healthy = "healthy" in condition.lower()

        top3 = [
            {
                "disease": _class_names[top3_idxs[i].item()],
                "confidence": round(top3_vals[i].item() * 100, 2),
            }
            for i in range(3)
        ]

        return {
            "success":    True,
            "disease":    top_class,
            "plant":      plant,
            "condition":  condition,
            "is_healthy": is_healthy,
            "confidence": top_conf,
            "top3":       top3,
        }

    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Inference error: {str(e)}"}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python disease_classifier.py <path_to_image>")
    else:
        result = classify_disease(sys.argv[1])
        print("[Result]", result)
