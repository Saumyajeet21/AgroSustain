"""
AgroSustain — Indian Crop Disease Dataset Downloader
Downloads, extracts, and merges datasets for Indian crops into the existing
PlantVillage training directory so ResNet50 can be retrained with 60+ classes.

Datasets added:
  1. Rice Disease Image Dataset       (Rice Blast, Brown Spot, BLB, Sheath Blight)
  2. Wheat Disease Classification     (Yellow Rust, Brown Rust, Powdery Mildew)
  3. Sugarcane Disease Dataset        (Red Rot, Smut, Healthy)
  4. Cotton Disease Dataset           (Leaf Curl, Bollworm, Healthy)
  5. Chickpea Disease Dataset         (Blight, Wilt, Healthy)

Usage:
  1. Install Kaggle API: pip install kaggle
  2. Place kaggle.json in C:/Users/<you>/.kaggle/kaggle.json
     (Download from: https://www.kaggle.com/settings -> API -> Create New Token)
  3. Run: python backend/ml/download_datasets.py
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent          # f:/Minor_Project
TRAIN_DIR    = PROJECT_ROOT / "datasets" / "plant_disease_classification" / "train"
VALID_DIR    = PROJECT_ROOT / "datasets" / "plant_disease_classification" / "valid"
DOWNLOAD_DIR = PROJECT_ROOT / "datasets" / "_downloads"     # temp extract location

TRAIN_DIR.mkdir(parents=True, exist_ok=True)
VALID_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── Kaggle dataset definitions ────────────────────────────────────────────────
# Format: (kaggle_dataset_slug, subfolder_after_extract_or_None, class_rename_map)
# class_rename_map: {folder_name_in_zip -> standard_ClassName___Disease}
DATASETS = [
    {
        "name":    "Rice Disease Image Dataset",
        "slug":    "minhhuy1209/rice-diseases-image-dataset",
        "classes": {
            "Bacterial Blight":  "Rice___Bacterial_Leaf_Blight",
            "Brown Spot":        "Rice___Brown_Spot",
            "Leaf Blast":        "Rice___Leaf_Blast",
            "Neck Blast":        "Rice___Neck_Blast",
            "Sheath Blight":     "Rice___Sheath_Blight",
            "Healthy":           "Rice___healthy",
            # alt folder names
            "bacterial_blight":  "Rice___Bacterial_Leaf_Blight",
            "brown_spot":        "Rice___Brown_Spot",
            "leaf_blast":        "Rice___Leaf_Blast",
            "neck_blast":        "Rice___Neck_Blast",
            "sheath_blight":     "Rice___Sheath_Blight",
            "healthy":           "Rice___healthy",
        },
    },
    {
        "name":    "Wheat Disease Classification",
        "slug":    "kushagra0301/wheat-disease-dataset",
        "classes": {
            "Yellow Rust":       "Wheat___Yellow_Rust",
            "Brown Rust":        "Wheat___Brown_Rust",
            "Loose Smut":        "Wheat___Loose_Smut",
            "Powdery Mildew":    "Wheat___Powdery_Mildew",
            "Healthy":           "Wheat___healthy",
            "yellow_rust":       "Wheat___Yellow_Rust",
            "brown_rust":        "Wheat___Brown_Rust",
            "loose_smut":        "Wheat___Loose_Smut",
            "powdery_mildew":    "Wheat___Powdery_Mildew",
            "healthy":           "Wheat___healthy",
        },
    },
    {
        "name":    "Sugarcane Disease Dataset",
        "slug":    "nirmalsankalana/sugarcane-disease-dataset",
        "classes": {
            "Red Rot":           "Sugarcane___Red_Rot",
            "Rust":              "Sugarcane___Rust",
            "Smut":              "Sugarcane___Smut",
            "Bacterial Blight":  "Sugarcane___Bacterial_Blight",
            "Healthy":           "Sugarcane___healthy",
            "red_rot":           "Sugarcane___Red_Rot",
            "rust":              "Sugarcane___Rust",
            "smut":              "Sugarcane___Smut",
            "healthy":           "Sugarcane___healthy",
        },
    },
    {
        "name":    "Cotton Disease Dataset",
        "slug":    "janmejaybhoi/cotton-disease-dataset",
        "classes": {
            "diseased cotton leaf":   "Cotton___Leaf_Curl_Virus",
            "diseased cotton plant":  "Cotton___Disease_Other",
            "fresh cotton leaf":      "Cotton___healthy",
            "fresh cotton plant":     "Cotton___healthy",
            "Diseased":               "Cotton___Disease_Other",
            "Fresh":                  "Cotton___healthy",
        },
    },
    {
        "name":    "Chickpea Disease Dataset",
        "slug":    "saket009/chickpea-disease-dataset",
        "classes": {
            "Ascochyta Blight":  "Chickpea___Ascochyta_Blight",
            "Botrytis Gray Mold":"Chickpea___Botrytis_Gray_Mold",
            "Dry Root Rot":      "Chickpea___Dry_Root_Rot",
            "Fusarium Wilt":     "Chickpea___Fusarium_Wilt",
            "Healthy":           "Chickpea___healthy",
            "healthy":           "Chickpea___healthy",
        },
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✓{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}⚠{RESET}  {msg}")
def fail(msg): print(f"  {RED}✗{RESET}  {msg}")
def info(msg): print(f"  {CYAN}→{RESET}  {msg}")


def check_kaggle():
    """Verify kaggle package + credentials are available."""
    try:
        import kaggle
        return True
    except ImportError:
        fail("kaggle package not installed. Run: pip install kaggle")
        return False
    except Exception as e:
        fail(f"Kaggle error: {e}")
        fail("Place kaggle.json at: C:/Users/<you>/.kaggle/kaggle.json")
        fail("Download from: https://www.kaggle.com/settings -> API -> Create New Token")
        return False


def download_dataset(slug: str, dest_dir: Path) -> Path | None:
    """Download and extract a Kaggle dataset, returns extract path."""
    import kaggle
    dataset_dir = dest_dir / slug.replace("/", "_")
    if dataset_dir.exists() and any(dataset_dir.iterdir()):
        warn(f"Already downloaded: {slug} → skipping")
        return dataset_dir

    dataset_dir.mkdir(parents=True, exist_ok=True)
    info(f"Downloading: {slug}")
    try:
        kaggle.api.dataset_download_files(slug, path=str(dataset_dir), unzip=True)
        ok(f"Downloaded & extracted: {slug}")
        return dataset_dir
    except Exception as e:
        fail(f"Failed to download {slug}: {e}")
        return None


def count_images(folder: Path) -> int:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    return sum(1 for f in folder.rglob("*") if f.suffix.lower() in exts)


def merge_dataset(extract_dir: Path, class_map: dict, split_ratio: float = 0.85) -> dict:
    """
    Walk extracted directory, map folder names to standard class names,
    and copy images to train/ and valid/ directories.

    Returns a count dict: {class_name: {"train": N, "valid": N}}
    """
    import random
    random.seed(42)

    counts = {}

    for subdir in sorted(extract_dir.rglob("*")):
        if not subdir.is_dir():
            continue
        folder_name = subdir.name

        # Try exact match then case-insensitive match
        std_name = class_map.get(folder_name) or class_map.get(folder_name.lower())
        if not std_name:
            continue

        images = [
            f for f in subdir.iterdir()
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        if not images:
            continue

        random.shuffle(images)
        n_train = int(len(images) * split_ratio)
        train_imgs = images[:n_train]
        valid_imgs = images[n_train:]

        # Create class folders
        train_class_dir = TRAIN_DIR / std_name
        valid_class_dir = VALID_DIR / std_name
        train_class_dir.mkdir(parents=True, exist_ok=True)
        valid_class_dir.mkdir(parents=True, exist_ok=True)

        # Copy images (skip if already exists)
        copied_train = 0
        for img in train_imgs:
            dst = train_class_dir / img.name
            if not dst.exists():
                shutil.copy2(img, dst)
                copied_train += 1

        copied_valid = 0
        for img in valid_imgs:
            dst = valid_class_dir / img.name
            if not dst.exists():
                shutil.copy2(img, dst)
                copied_valid += 1

        if std_name not in counts:
            counts[std_name] = {"train": 0, "valid": 0}
        counts[std_name]["train"] += copied_train
        counts[std_name]["valid"] += copied_valid

    return counts


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  AgroSustain — Indian Crop Dataset Downloader{RESET}")
    print(f"{'='*60}")
    print(f"  Train dir : {TRAIN_DIR}")
    print(f"  Valid dir : {VALID_DIR}")
    print(f"{'='*60}\n")

    if not check_kaggle():
        print("\nSetup instructions:")
        print("  1. pip install kaggle")
        print("  2. Go to https://www.kaggle.com/settings -> API -> Create New Token")
        print("  3. Save kaggle.json to C:/Users/<you>/.kaggle/kaggle.json")
        sys.exit(1)

    total_new_images = 0
    all_counts = {}

    for ds in DATASETS:
        print(f"\n{BOLD}[Dataset] {ds['name']}{RESET}")
        print(f"  Slug: {ds['slug']}")

        extract_path = download_dataset(ds["slug"], DOWNLOAD_DIR)
        if extract_path is None:
            continue

        counts = merge_dataset(extract_path, ds["classes"])
        all_counts.update(counts)

        if counts:
            for cls, c in sorted(counts.items()):
                print(f"    {CYAN}{cls}{RESET}: +{c['train']} train / +{c['valid']} valid")
                total_new_images += c["train"] + c["valid"]
        else:
            warn("No matching class folders found — check class_map for this dataset")

    # ── Summary ────────────────────────────────────────────────────────────────
    total_train = count_images(TRAIN_DIR)
    total_valid = count_images(VALID_DIR)
    n_classes   = len(list(TRAIN_DIR.iterdir()))

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  DOWNLOAD COMPLETE{RESET}")
    print(f"{'='*60}")
    print(f"  New images added : {total_new_images:,}")
    print(f"  Total train      : {total_train:,}")
    print(f"  Total valid      : {total_valid:,}")
    print(f"  Total classes    : {n_classes}")
    print(f"\n  {GREEN}Next step:{RESET} Run the retraining script:")
    print(f"  python backend/ml/train_resnet50.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
