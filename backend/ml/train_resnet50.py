"""
AgroSustain — ResNet50 Plant Disease Classifier Training Script
Fine-tunes a pretrained ResNet50 on the PlantVillage dataset (38 classes).

Run from project root:
    python backend/ml/train_resnet50.py
"""

import os
import json
import time
import copy

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

# ── Config ─────────────────────────────────────────────────────────────────
DATA_BASE = r"f:\Minor_Project\datasets\plant_disease_classification"
TRAIN_DIR = os.path.join(DATA_BASE, "train")
VAL_DIR   = os.path.join(DATA_BASE, "valid")

SAVE_DIR  = r"f:\Minor_Project\backend\models"
os.makedirs(SAVE_DIR, exist_ok=True)

BATCH_SIZE   = 64         # Lowered to prevent VRAM allocation crashes
NUM_EPOCHS   = 8
LEARNING_RATE = 0.001
NUM_WORKERS  = 0          # Windows-safe: disable shared memory mapping to fix error 1455
SEED         = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {DEVICE}")

# ── Transforms ─────────────────────────────────────────────────────────────
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

def main():
    # ── Datasets & Loaders ─────────────────────────────────────────────────────
    print("[INFO] Loading datasets...")
    train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=train_transforms)
    val_dataset   = datasets.ImageFolder(VAL_DIR,   transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=NUM_WORKERS)
    val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS)

    class_names = train_dataset.classes
    num_classes = len(class_names)
    print(f"[INFO] Classes: {num_classes} | Train: {len(train_dataset)} | Val: {len(val_dataset)}")

    # Save class names
    with open(os.path.join(SAVE_DIR, "disease_classes.json"), "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"[INFO] Class names saved.")

    # ── Model: ResNet50 (transfer learning) ────────────────────────────────────
    print("[INFO] Loading pretrained ResNet50...")
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

    # Freeze all layers except the final classification head
    for param in model.parameters():
        param.requires_grad = False

    # Replace the final fully-connected layer
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Linear(512, num_classes)
    )

    model = model.to(DEVICE)

    # ── Loss & Optimizer ────────────────────────────────────────────────────────
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

    # ── Training Loop ───────────────────────────────────────────────────────────
    best_model_wts = copy.deepcopy(model.state_dict())
    best_val_acc   = 0.0

    print("\n[INFO] Starting training...\n")
    for epoch in range(NUM_EPOCHS):
        epoch_start = time.time()

        for phase in ["train", "val"]:
            if phase == "train":
                model.train()
                loader = train_loader
                dataset_size = len(train_dataset)
            else:
                model.eval()
                loader = val_loader
                dataset_size = len(val_dataset)

            running_loss    = 0.0
            running_correct = 0

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

                if phase == "train" and (batch_idx + 1) % 50 == 0:
                    print(f"  Epoch {epoch+1}/{NUM_EPOCHS} | Batch {batch_idx+1}/{len(train_loader)} | "
                          f"Loss: {loss.item():.4f}")

            epoch_loss = running_loss / dataset_size
            epoch_acc  = running_correct / dataset_size * 100

            elapsed = time.time() - epoch_start
            print(f"[Epoch {epoch+1:02d}/{NUM_EPOCHS}] {phase.upper():5s} | "
                  f"Loss: {epoch_loss:.4f} | Acc: {epoch_acc:.2f}% | Time: {elapsed:.0f}s")

            if phase == "val":
                scheduler.step()
                if epoch_acc > best_val_acc:
                    best_val_acc = epoch_acc
                    best_model_wts = copy.deepcopy(model.state_dict())
                    ckpt_path = os.path.join(SAVE_DIR, "resnet50_disease.pth")
                    torch.save(model.state_dict(), ckpt_path)
                    print(f"  [SAVED] New best val acc: {best_val_acc:.2f}% -> {ckpt_path}")

        print()

    # ── Final Save ──────────────────────────────────────────────────────────────
    model.load_state_dict(best_model_wts)
    print(f"\n[DONE] Best validation accuracy: {best_val_acc:.2f}%")
    print(f"[DONE] Model saved to: {os.path.join(SAVE_DIR, 'resnet50_disease.pth')}")

if __name__ == '__main__':
    main()
