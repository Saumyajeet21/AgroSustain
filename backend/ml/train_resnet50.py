"""
AgroSustain - ResNet50 Plant Disease Classifier Training
Run from project root:
    python backend/ml/train_resnet50.py
"""

import os, json, time, copy, math
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

# -- Config -----------------------------------------------------------------
DATA_BASE  = r"f:\Minor_Project\datasets\plant_disease_classification"
TRAIN_DIR  = os.path.join(DATA_BASE, "train")
VAL_DIR    = os.path.join(DATA_BASE, "valid")
SAVE_DIR   = r"f:\Minor_Project\backend\models"
os.makedirs(SAVE_DIR, exist_ok=True)

BATCH_SIZE    = 64
NUM_EPOCHS    = 8
LEARNING_RATE = 0.001
NUM_WORKERS   = 0    # Windows-safe (avoids shared memory error 1455)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -- Helpers -----------------------------------------------------------------
SEP  = "=" * 65
SEP2 = "-" * 65

def fmt_time(seconds):
    """Convert seconds to h:mm:ss string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"

def progress_bar(current, total, width=30):
    """Inline ASCII progress bar using # and . characters."""
    done = int(width * current / total)
    bar  = "#" * done + "." * (width - done)
    pct  = 100 * current / total
    return f"[{bar}] {pct:5.1f}%"

# -- Transforms --------------------------------------------------------------
train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
val_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# -- Main --------------------------------------------------------------------
def main():
    print(SEP)
    print("   AgroSustain - ResNet50 Disease Classifier Training")
    print(SEP)
    print(f"  Device  : {DEVICE} {'(GPU - CUDA OK)' if DEVICE.type == 'cuda' else '(CPU - may be slow)'}")
    print(f"  Epochs  : {NUM_EPOCHS}")
    print(f"  Batch   : {BATCH_SIZE}")
    print(f"  Workers : {NUM_WORKERS}")
    print(SEP)

    # -- Datasets ----------------------------------------------------------
    print("\n[1/4] Loading datasets... ", end="", flush=True)
    train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=train_transforms)
    val_dataset   = datasets.ImageFolder(VAL_DIR,   transform=val_transforms)
    print("Done.")

    train_loader  = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,  num_workers=NUM_WORKERS)
    val_loader    = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)

    num_classes = len(train_dataset.classes)
    with open(os.path.join(SAVE_DIR, "disease_classes.json"), "w") as f:
        json.dump(train_dataset.classes, f, indent=2)

    print(f"      Classes : {num_classes}")
    print(f"      Train   : {len(train_dataset):,} images  ({len(train_loader)} batches)")
    print(f"      Val     : {len(val_dataset):,} images  ({len(val_loader)} batches)")

    # -- ETA estimate ------------------------------------------------------
    print(f"\n  ETA estimate:")
    if DEVICE.type == "cuda":
        sec_per_epoch = len(train_loader) * 0.12 + len(val_loader) * 0.08
    else:
        sec_per_epoch = len(train_loader) * 1.0  + len(val_loader) * 0.6
    total_est = sec_per_epoch * NUM_EPOCHS
    print(f"  ETA ~{fmt_time(sec_per_epoch)} per epoch  x  {NUM_EPOCHS} epochs")
    print(f"  ETA ~{fmt_time(total_est)} total\n")

    # -- Model -------------------------------------------------------------
    print("[2/4] Loading pretrained ResNet50... ", end="", flush=True)
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Linear(512, num_classes),
    )
    model = model.to(DEVICE)
    print("Done.\n")

    # -- Optimizer ---------------------------------------------------------
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

    print("[3/4] Starting training loop...\n")
    print(SEP)

    best_val_acc   = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())
    training_start = time.time()

    for epoch in range(NUM_EPOCHS):
        epoch_start = time.time()
        print(f"\n  EPOCH {epoch+1}/{NUM_EPOCHS}")
        print(SEP2)

        for phase in ["train", "val"]:
            model.train() if phase == "train" else model.eval()
            loader        = train_loader if phase == "train" else val_loader
            dataset_size  = len(train_dataset) if phase == "train" else len(val_dataset)
            total_batches = len(loader)

            running_loss    = 0.0
            running_correct = 0
            phase_start     = time.time()

            for batch_idx, (inputs, labels) in enumerate(loader):
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    loss    = criterion(outputs, labels)
                    preds   = outputs.argmax(dim=1)
                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss    += loss.item() * inputs.size(0)
                running_correct += (preds == labels).sum().item()

                # -- Live progress line ---------------------------------
                if (batch_idx + 1) % 20 == 0 or (batch_idx + 1) == total_batches:
                    elapsed    = time.time() - phase_start
                    speed      = (batch_idx + 1) / elapsed if elapsed > 0 else 0
                    eta_sec    = (total_batches - batch_idx - 1) / speed if speed > 0 else 0
                    curr_acc   = running_correct / ((batch_idx + 1) * BATCH_SIZE) * 100
                    bar        = progress_bar(batch_idx + 1, total_batches)
                    phase_tag  = "TRAIN" if phase == "train" else " VAL "
                    print(
                        f"  [{phase_tag}] {bar}  "
                        f"Batch {batch_idx+1:4d}/{total_batches}  "
                        f"Loss: {loss.item():.4f}  "
                        f"Acc: {curr_acc:5.1f}%  "
                        f"ETA: {fmt_time(eta_sec)}",
                        end="\r", flush=True
                    )

            print()  # newline after \r

            epoch_loss = running_loss / dataset_size
            epoch_acc  = running_correct / dataset_size * 100
            phase_time = time.time() - phase_start
            phase_tag  = "TRAIN" if phase == "train" else "  VAL"
            marker     = ""

            if phase == "val":
                scheduler.step()
                if epoch_acc > best_val_acc:
                    best_val_acc   = epoch_acc
                    best_model_wts = copy.deepcopy(model.state_dict())
                    ckpt = os.path.join(SAVE_DIR, "resnet50_disease.pth")
                    torch.save(model.state_dict(), ckpt)
                    marker = "  << NEW BEST - checkpoint saved!"

            elapsed_total = time.time() - training_start
            epochs_done   = epoch + (1 if phase == "val" else 0.5)
            eta_total     = (elapsed_total / epochs_done) * (NUM_EPOCHS - epochs_done) if epochs_done else 0

            print(f"\n  >> [{phase_tag}] Epoch {epoch+1:02d}  "
                  f"Loss: {epoch_loss:.4f}  "
                  f"Acc: {epoch_acc:.2f}%  "
                  f"({fmt_time(phase_time)}){marker}")

            if phase == "val":
                print(f"  ETA | Elapsed: {fmt_time(elapsed_total)}  |  "
                      f"Remaining: {fmt_time(eta_total)}  |  "
                      f"Best val acc: {best_val_acc:.2f}%")
                print(SEP2)

    # -- Done --------------------------------------------------------------
    total_time = time.time() - training_start
    model.load_state_dict(best_model_wts)
    print(f"\n{SEP}")
    print(f"  TRAINING COMPLETE")
    print(f"  Best Val Accuracy : {best_val_acc:.2f}%")
    print(f"  Total Time        : {fmt_time(total_time)}")
    print(f"  Model saved to    : {os.path.join(SAVE_DIR, 'resnet50_disease.pth')}")
    print(SEP)

if __name__ == "__main__":
    main()
