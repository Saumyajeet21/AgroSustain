"""
AgroSustain — YOLOv8n Leaf Detection Training
Run from project root:
    python backend/ml/train_yolo.py
"""

import os, shutil, time
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────
DATASET_DIR = Path(r"f:\Minor_Project\datasets\plant_disease_detection")
SAVE_DIR    = Path(r"f:\Minor_Project\backend\models")
RUNS_DIR    = Path(r"f:\Minor_Project\backend\yolo_runs")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

SEP  = "=" * 65
SEP2 = "-" * 65

def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"

# Write data.yaml
DATA_YAML = f"""train: {(DATASET_DIR / 'train' / 'images').as_posix()}
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
  12: Healthy"""

yaml_path = DATASET_DIR / "data_yolo.yaml"
with open(yaml_path, "w") as f:
    f.write(DATA_YAML)

# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from ultralytics import YOLO
    import torch

    device = "0" if torch.cuda.is_available() else "cpu"

    print(SEP)
    print("   AgroSustain — YOLOv8n Leaf Detection Training")
    print(SEP)
    print(f"  Device  : {'GPU ✓ (RTX 4050)' if device == '0' else 'CPU'}")
    print(f"  Images  : 2,903  |  Classes: 13  |  Epochs: 15  |  Batch: 8")
    print(f"  ETA     : ~{fmt_time(90 * 15)} on GPU")
    print(SEP + "\n")

    start = time.time()

    print("[1/3] Loading YOLOv8n base weights... ", end="", flush=True)
    model = YOLO("yolov8n.pt")
    print("Done.\n")

    print("[2/3] Training...\n")
    print(SEP2)

    results = model.train(
        data     = str(yaml_path),
        epochs   = 15,
        imgsz    = 640,
        batch    = 8,
        device   = device,
        project  = str(RUNS_DIR),
        name     = "yolo_disease",
        patience = 5,
        save     = True,
        verbose  = True,
        workers  = 0,
        cache    = False,
        split    = 0.1,
        exist_ok = True,
    )

    print(f"\n{SEP2}")
    print("[3/3] Copying best weights...")
    best = RUNS_DIR / "yolo_disease" / "weights" / "best.pt"
    if best.exists():
        dest = SAVE_DIR / "yolo_leaf.pt"
        shutil.copy(best, dest)
        print(f"\n{SEP}")
        print(f"  ✅ YOLO TRAINING COMPLETE!")
        print(f"  Weights : {dest}")
        print(f"  Time    : {fmt_time(time.time() - start)}")
        print(SEP)
    else:
        print(f"  ⚠️  best.pt not found — check output above.")
