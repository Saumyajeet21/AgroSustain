"""
AgroSustain — YOLOv8 Plant Region Detector
Detects plant parts (leaves, stems, roots, whole plants, fruits) in an image,
crops each detected region, and returns paths for the ResNet50 pipeline.

Supports:
  - Custom trained YOLO model (yolo_leaf.pt) if present
  - Pretrained YOLOv8n as fallback (detects general objects)
  - Full-image fallback when no plant regions are detected
  - NO restriction to leaves — stems, roots, whole plants all accepted
"""

import os
import cv2
import numpy as np
from PIL import Image

# ── Config ───────────────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
_MODELS_DIR  = os.path.join(_BASE_DIR, "models")
_YOLO_PATH   = os.path.join(_MODELS_DIR, "yolo_leaf.pt")

# Pretrained YOLOv8n fallback (COCO 80 classes — no leaf, but detects objects)
_YOLO_PRETRAINED = "yolov8n.pt"

# COCO class IDs that represent plant-like / organic objects
# 58=potted plant, 55=orange, 56=broccoli, 57=carrot, 53=apple, 54=sandwich,
# 52=banana, 47=cup  — used loosely to detect "organic matter" in fallback mode
_PLANT_COCO_IDS = {47, 52, 53, 54, 55, 56, 57, 58}

# Color palette for bounding boxes by detected class label
_BOX_COLORS = {
    "leaf":       (0,  200,  50),    # green
    "stem":       (200, 150,  0),    # amber
    "root":       (139,  69,  19),   # brown
    "fruit":      (255,  80,  20),   # orange
    "whole":      (50,  150, 255),   # blue
    "plant":      (50,  150, 255),   # blue alias
    "default":    (100, 100, 255),   # purple (fallback)
}

_model = None
_using_custom = False


def _ensure_loaded():
    global _model, _using_custom
    if _model is None:
        from ultralytics import YOLO
        if os.path.exists(_YOLO_PATH):
            _model = YOLO(_YOLO_PATH)
            _using_custom = True
            print(f"[PlantDetector] Loaded custom YOLO: {_YOLO_PATH}")
        else:
            _model = YOLO(_YOLO_PRETRAINED)
            _using_custom = False
            print("[PlantDetector] Custom YOLO not found — using pretrained YOLOv8n fallback.")


def _get_box_color(label: str) -> tuple:
    label_lower = label.lower()
    for key, color in _BOX_COLORS.items():
        if key in label_lower:
            return color
    return _BOX_COLORS["default"]


def detect_and_crop_leaves(image_path: str, output_dir: str, conf_threshold: float = 0.20) -> dict:
    """
    Detects plant regions (leaves, stems, roots, fruits, whole plants) in an
    image and crops each region out for the disease classifier.

    Behaviour:
      1. If custom YOLO model present → use its detections (any class label)
      2. If pretrained YOLOv8n → filter to plant-related COCO classes
      3. If nothing detected above conf_threshold → use full image as one region

    Parameters
    ----------
    image_path      : str   — path to the uploaded farm/plant image
    output_dir      : str   — directory to save cropped regions
    conf_threshold  : float — minimum confidence to accept a YOLO detection

    Returns
    -------
    dict with keys:
        success            : bool
        boxes              : list of [x1, y1, x2, y2, confidence, label]
        cropped_paths      : list of str (file paths to cropped regions)
        annotated_path     : str (path to annotated image)
        num_leaves         : int (total regions found; name kept for API compat.)
        used_fallback      : bool (True when full-image was used)
        detected_parts     : list[str] (e.g. ["leaf", "stem"])
        error              : str (only when success=False)
    """
    try:
        _ensure_loaded()
        os.makedirs(output_dir, exist_ok=True)

        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return {"success": False, "error": f"Cannot read image: {image_path}"}

        h, w = img_bgr.shape[:2]
        annotated    = img_bgr.copy()
        cropped_paths = []
        boxes_out    = []
        detected_parts = []
        used_fallback  = False

        # ── Run YOLO inference ────────────────────────────────────────────────
        results = _model.predict(image_path, conf=conf_threshold, verbose=False)[0]
        boxes_raw = results.boxes
        names     = _model.names  # class id → name mapping

        # ── Filter & crop detections ──────────────────────────────────────────
        valid_boxes = []
        if boxes_raw is not None and len(boxes_raw) > 0:
            for i, box in enumerate(boxes_raw.xyxy):
                cls_id = int(boxes_raw.cls[i].item())
                conf   = float(boxes_raw.conf[i].item())
                label  = names.get(cls_id, f"region_{cls_id}") if isinstance(names, dict) else str(cls_id)

                # If using pretrained COCO model, only keep plant-adjacent classes
                if not _using_custom and cls_id not in _PLANT_COCO_IDS:
                    continue

                valid_boxes.append((box, conf, label))

        if valid_boxes:
            for i, (box, conf, label) in enumerate(valid_boxes):
                x1, y1, x2, y2 = map(int, box.tolist())
                color = _get_box_color(label)

                # Draw bounding box + label
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
                display_label = f"{label.capitalize()} {i+1}: {conf:.0%}"
                cv2.putText(annotated, display_label, (x1, max(y1 - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                # Crop region (with small padding)
                pad = 10
                cx1, cy1 = max(0, x1 - pad), max(0, y1 - pad)
                cx2, cy2 = min(w, x2 + pad), min(h, y2 + pad)
                crop = img_bgr[cy1:cy2, cx1:cx2]

                crop_path = os.path.join(output_dir, f"region_{i+1}.jpg")
                cv2.imwrite(crop_path, crop)
                cropped_paths.append(crop_path)
                boxes_out.append([x1, y1, x2, y2, round(conf, 3), label])
                detected_parts.append(label.lower())

        # ── Full-image fallback ───────────────────────────────────────────────
        if not cropped_paths:
            used_fallback = True
            fallback_path = os.path.join(output_dir, "region_1.jpg")
            cv2.imwrite(fallback_path, img_bgr)
            cropped_paths = [fallback_path]
            boxes_out     = [[0, 0, w, h, 1.0, "full_image"]]
            detected_parts = ["full_image"]
            # Draw a soft border on the annotated image
            cv2.rectangle(annotated, (5, 5), (w - 5, h - 5), (100, 100, 255), 3)
            cv2.putText(annotated, "Full image analysis", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 255), 2)

        # ── Save annotated image ──────────────────────────────────────────────
        annotated_path = os.path.join(output_dir, "annotated.jpg")
        cv2.imwrite(annotated_path, annotated)

        return {
            "success":         True,
            "boxes":           boxes_out,
            "cropped_paths":   cropped_paths,
            "annotated_path":  annotated_path,
            "num_leaves":      len(cropped_paths),   # kept for API compatibility
            "used_fallback":   used_fallback,
            "detected_parts":  list(set(detected_parts)),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python leaf_detector.py <image_path>")
    else:
        result = detect_and_crop_leaves(sys.argv[1], output_dir="tmp_crops")
        print("[Detector Result]")
        for k, v in result.items():
            print(f"  {k}: {v}")
