"""
AgroSustain — YOLOv8 Leaf/Disease Detection Training Script
Trains YOLOv8n on the plant disease detection dataset (13 classes).

Run from project root:
    python backend/ml/train_yolo.py
"""

import os
import shutil
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────
DATASET_DIR = Path(r"f:\Minor_Project\datasets\plant_disease_detection")
SAVE_DIR    = Path(r"f:\Minor_Project\backend\models")
RUNS_DIR    = Path(r"f:\Minor_Project\backend\yolo_runs")

# ── Fix data.yaml — create one with valid split from train ─────────────────
# The dataset has no 'valid' folder, so we'll use YOLOv8's split parameter

DATA_YAML_CONTENT = f"""
train: {(DATASET_DIR / 'train' / 'images').as_posix()}
val:   {(DATASET_DIR / 'train' / 'images').as_posix()}

nc: 13
names:
  0: Aphids
  1: Armyworm
  2: Bacterial_Blight
  3: Powdery_Mildew
  4: Leaf_Blight
  5: Leaf_Miner
  6: Leaf_Spot
  7: Mosaic_Virus
  8: Rust
  9: Stem_Borer
  10: Whiteflies
  11: Yellow_Virus
  12: Healthy
"""

yaml_path = DATASET_DIR / "data_yolo.yaml"
with open(yaml_path, "w") as f:
    f.write(DATA_YAML_CONTENT.strip())

print(f"[INFO] Written YAML: {yaml_path}")
print(f"[INFO] Save dir:     {SAVE_DIR}")

# ── Run training ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from ultralytics import YOLO

    print("[INFO] Loading YOLOv8n pretrained weights...")
    model = YOLO("yolov8n.pt")  # Nano — fast, good for laptop GPU

    print("[INFO] Starting YOLOv8 training on RTX 4050...")
    results = model.train(
        data      = str(yaml_path),
        epochs    = 15,           # Less epochs for speed
        imgsz     = 640,
        batch     = 8,            # extremely safe for VRAM
        device    = 0,            # GPU 0
        project   = str(RUNS_DIR),
        name      = "yolo_disease",
        patience  = 5,            
        save      = True,
        verbose   = True,
        workers   = 0,            # Windows error 1455 fix
        cache     = False,        
        split     = 0.1,          
    )

    # Copy best weights to models/
    best_weights = RUNS_DIR / "yolo_disease" / "weights" / "best.pt"
    if best_weights.exists():
        shutil.copy(best_weights, SAVE_DIR / "yolo_leaf.pt")
        print(f"[DONE] Best weights saved to: {SAVE_DIR / 'yolo_leaf.pt'}")
    else:
        print("[WARN] best.pt not found — check training output")
