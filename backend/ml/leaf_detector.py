"""
AgroSustain — YOLOv8 Leaf Detector Module
Detects leaf regions in a farm photo, crops them out with OpenCV,
and returns bounding boxes + cropped image paths for the ResNet50 pipeline.
"""

import os
import cv2
import numpy as np
from PIL import Image

# ── Config ───────────────────────────────────────────────────────────────────
_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
_MODELS_DIR = os.path.join(_BASE_DIR, "models")
_YOLO_PATH  = os.path.join(_MODELS_DIR, "yolo_leaf.pt")

# Pretrained COCO YOLOv8n as fallback (uses whole image if no custom model)
_YOLO_PRETRAINED = "yolov8n.pt"

_model = None


def _ensure_loaded():
    global _model
    if _model is None:
        from ultralytics import YOLO
        if os.path.exists(_YOLO_PATH):
            _model = YOLO(_YOLO_PATH)
            print(f"[LeafDetector] Loaded custom YOLO model: {_YOLO_PATH}")
        else:
            # Fallback: load pretrained YOLOv8n and use as-is
            # (For leaf detection we'll just do whole-image analysis)
            _model = YOLO(_YOLO_PRETRAINED)
            print("[LeafDetector] Custom YOLO not found. Using pretrained YOLOv8n (whole-image fallback).")


def detect_and_crop_leaves(image_path: str, output_dir: str, conf_threshold: float = 0.25) -> dict:
    """
    Detects leaf bounding boxes in an image and crops each leaf out.

    Parameters
    ----------
    image_path      : str — path to the uploaded farm image
    output_dir      : str — directory to save cropped leaf images
    conf_threshold  : float — minimum confidence to accept a detection

    Returns
    -------
    dict with keys:
        - success       : bool
        - boxes         : list of [x1, y1, x2, y2, confidence]
        - cropped_paths : list of str (file paths to cropped leaf images)
        - annotated_path: str (path to original image with bounding boxes drawn)
        - num_leaves    : int
        - used_fallback : bool (True if whole-image was used instead of YOLO boxes)
        - error         : str (only when success=False)
    """
    try:
        _ensure_loaded()
        os.makedirs(output_dir, exist_ok=True)

        # Read image
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return {"success": False, "error": f"Cannot read image: {image_path}"}

        h, w = img_bgr.shape[:2]
        annotated = img_bgr.copy()

        # ── Run YOLO inference ────────────────────────────────────────────────
        results = _model.predict(image_path, conf=conf_threshold, verbose=False)[0]
        boxes_raw = results.boxes

        cropped_paths = []
        boxes_out     = []
        used_fallback = False

        if boxes_raw is not None and len(boxes_raw) > 0:
            for i, box in enumerate(boxes_raw.xyxy):
                x1, y1, x2, y2 = map(int, box.tolist())
                conf = float(boxes_raw.conf[i])

                # Draw bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 50), 3)
                label = f"Leaf {i+1}: {conf:.0%}"
                cv2.putText(annotated, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 50), 2)

                # Crop leaf region (with small padding)
                pad = 10
                cx1, cy1 = max(0, x1 - pad), max(0, y1 - pad)
                cx2, cy2 = min(w, x2 + pad), min(h, y2 + pad)
                crop_bgr = img_bgr[cy1:cy2, cx1:cx2]

                crop_path = os.path.join(output_dir, f"leaf_{i+1}.jpg")
                cv2.imwrite(crop_path, crop_bgr)
                cropped_paths.append(crop_path)
                boxes_out.append([x1, y1, x2, y2, round(conf, 3)])

        else:
            # Fallback: use entire image as one "leaf"
            used_fallback = True
            fallback_path = os.path.join(output_dir, "leaf_1.jpg")
            cv2.imwrite(fallback_path, img_bgr)
            cropped_paths = [fallback_path]
            boxes_out     = [[0, 0, w, h, 1.0]]
            cv2.rectangle(annotated, (5, 5), (w - 5, h - 5), (100, 100, 255), 3)
            cv2.putText(annotated, "Full image (no leaf detected)", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 255), 2)

        # Save annotated image
        annotated_path = os.path.join(output_dir, "annotated.jpg")
        cv2.imwrite(annotated_path, annotated)

        return {
            "success":        True,
            "boxes":          boxes_out,
            "cropped_paths":  cropped_paths,
            "annotated_path": annotated_path,
            "num_leaves":     len(cropped_paths),
            "used_fallback":  used_fallback,
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
