# ≡ƒî▒ AgroSustain ΓÇö AI-Powered Smart Farming Platform

<div align="center">

![AgroSustain Banner](https://img.shields.io/badge/AgroSustain-Smart%20Farming-38bd6c?style=for-the-badge&logo=leaf&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**An AI-driven agricultural platform empowering Indian farmers with data-driven, climate-resilient decisions.**

*Aligned with **UN SDG 2** (Zero Hunger) ┬╖ **SDG 13** (Climate Action)*

</div>

---

## ≡ƒôï Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [AI Models & Pipeline](#-ai-models--pipeline)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Economic Dashboard](#-economic-dashboard)

---

## ≡ƒî╛ Overview

AgroSustain is a full-stack web application that helps Indian farmers make smarter agricultural decisions by combining:

- **Real-time environmental data** fetched automatically from GPS coordinates (no IoT hardware needed)
- **Machine learning** for crop recommendation (XGBoost) and plant disease diagnosis (YOLOv8 + ResNet50)
- **Groq Vision AI** (Llama 4 Scout) for universal crop identification ΓÇö works on wheat, rice, mango, and any crop even if not in the training dataset
- **Groq LLM** (Llama 3.3 70B) for conversational treatment advice and farming chatbot

> **Hardware-Free**: Operates 100% in software by leveraging geospatial and meteorological APIs ΓÇö no physical IoT sensors required.

---

## Γ£¿ Key Features

### 1. ≡ƒî┐ Smart Crop Advisor
- Auto-fetches live weather (temperature, humidity, rainfall) and soil data (pH, NPK, bulk density) from the user's GPS location
- Runs the environmental parameters through a trained **XGBoost classifier** to recommend the optimal crop
- Shows confidence scores and alternative crop suggestions
- Supports 22 major Indian crops

### 2. ≡ƒö¼ AI Plant Doctor (4-Stage Vision Pipeline)
- Upload any photo of a plant ΓÇö leaf, stem, root, fruit, or whole plant
- **Stage A**: YOLOv8 detects and crops all plant regions with bounding boxes
- **Stage B**: Groq Vision (Llama 4 Scout) universally identifies the crop and disease ΓÇö works even for wheat, rice, mango, orange not in the training data
- **Stage C**: ResNet50 provides precise disease classification for its 38 known classes (PlantVillage dataset)
- **Stage D**: Groq LLM (Llama 3.3 70B) generates actionable treatment advice with Indian pesticide recommendations
- Smart arbitration: uses YOLO region detection to decide whether to trust ResNet or Groq Vision

### 3. ≡ƒôè Economic Dashboard
- Select any crop and enter your farm area (in hectares)
- Calculates projected yield, total investment, gross revenue, net profit, ROI, and profit margin
- Based on Indian agricultural averages (ICAR / Ministry of Agriculture data)
- Interactive bar chart and donut chart breakdowns (Recharts)

### 4. ≡ƒñû AgroBot Chatbot
- Conversational AI powered by Groq (Llama 3.3 70B Versatile)
- Answers farming questions, pest management queries, market advice
- Multilingual support (Hindi/English toggle)
- Session-based conversation history

### 5. ≡ƒîÉ Live Environment Data (Hardware Bypass)
- **Weather**: OpenWeatherMap / Open-Meteo APIs
- **Soil**: ISRIC SoilGrids REST API (pH, organic carbon, bulk density, sand/clay/silt)
- **Macronutrients**: NASA POWER API estimates

---

## ≡ƒ¢á∩╕Å Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Vanilla CSS, Recharts, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Auth & DB** | Supabase (PostgreSQL) |
| **ML ΓÇö Crop** | XGBoost, scikit-learn |
| **ML ΓÇö Vision** | YOLOv8n (Ultralytics), ResNet50 (PyTorch/torchvision) |
| **AI ΓÇö Vision** | Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct) |
| **AI ΓÇö LLM** | Groq API (llama-3.3-70b-versatile) |
| **Image Processing** | OpenCV (cv2), Pillow |
| **Weather APIs** | OpenWeatherMap, Open-Meteo |
| **Soil APIs** | ISRIC SoilGrids, NASA POWER |
| **i18n** | Custom React i18n (English + Hindi) |

---

## ≡ƒºá AI Models & Pipeline

### Model 1: Crop Predictor

```
Input: N, P, K, pH, Rainfall, Temperature, Humidity
  Γåô
XGBoost Classifier (trained on Indian crop dataset)
  Γåô
Output: Recommended crop + confidence + top alternatives
```

- **Algorithm**: XGBoost (Extreme Gradient Boosting)
- **Features**: 7 environmental parameters
- **Classes**: 22 Indian crops (Rice, Maize, Chickpea, Mango, Cotton, etc.)
- **Training data**: Custom dataset mapping NPK + climate ΓåÆ optimal crop

### Model 2: Plant Disease Diagnosis (4-Stage Pipeline)

```
Upload Image
  Γåô
[Stage A] YOLOv8n  ΓåÆ  Detect & crop plant regions (leaf/stem/root/fruit)
  Γåô
[Stage B] Groq Vision (Llama 4 Scout)  ΓåÆ  Universal crop & disease ID
  Γåô
[Stage C] ResNet50  ΓåÆ  Precise disease classification (38 PlantVillage classes)
       Smart arbitration: picks best result based on YOLO regions + crop domain
  Γåô
[Stage D] Groq LLM (Llama 3.3 70B)  ΓåÆ  Treatment advice with Indian context
  Γåô
Output: Annotated image + diagnosis + AI treatment plan
```

**PlantVillage Classes (ResNet50)**: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Bell Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato ΓÇö 38 diseases total.

**Groq Vision handles**: Wheat, Rice, Mango, Sugarcane, Cotton, Chickpea, Banana, and any crop from any angle.

**Smart Arbitration Logic**:
- If YOLO found leaf regions + ResNet is confident + both predict domain crops ΓåÆ ResNet wins (precise)
- If YOLO fell back to full image + Vision sees non-domain crop ΓåÆ Groq Vision wins (universal)
- Result cached per disease for faster subsequent requests

### Model 3: AgroBot (Conversational)

- **Model**: Groq `llama-3.3-70b-versatile`
- Session-based with conversation history
- Context-aware farming Q&A

---

## ≡ƒôü Project Structure

```
AgroSustain/
Γö£ΓöÇΓöÇ backend/
Γöé   Γö£ΓöÇΓöÇ main.py                  # FastAPI app ΓÇö all routes
Γöé   Γö£ΓöÇΓöÇ requirements.txt         # Python dependencies
Γöé   Γö£ΓöÇΓöÇ .env.example             # Environment variable template
Γöé   Γö£ΓöÇΓöÇ setup_tables.sql         # Supabase schema
Γöé   Γö£ΓöÇΓöÇ ml/
Γöé   Γöé   Γö£ΓöÇΓöÇ crop_predictor.py    # XGBoost inference
Γöé   Γöé   Γö£ΓöÇΓöÇ disease_classifier.py# ResNet50 inference
Γöé   Γöé   Γö£ΓöÇΓöÇ leaf_detector.py     # YOLOv8 plant region detection
Γöé   Γöé   Γö£ΓöÇΓöÇ vision_analyzer.py   # Groq Vision (Llama 4 Scout) wrapper
Γöé   Γöé   Γö£ΓöÇΓöÇ economics.py         # Economic calculations
Γöé   Γöé   Γö£ΓöÇΓöÇ download_datasets.py # Indian crop dataset downloader (Kaggle)
Γöé   Γöé   Γö£ΓöÇΓöÇ train_resnet50.py    # ResNet50 training script
Γöé   Γöé   ΓööΓöÇΓöÇ train_yolo.py        # YOLOv8 training script
Γöé   Γö£ΓöÇΓöÇ models/
Γöé   Γöé   Γö£ΓöÇΓöÇ disease_classes.json # ResNet50 class labels
Γöé   Γöé   ΓööΓöÇΓöÇ *.pth / *.pt         # Trained weights (gitignored ΓÇö download separately)
Γöé   ΓööΓöÇΓöÇ utils/
Γö£ΓöÇΓöÇ frontend/
Γöé   Γö£ΓöÇΓöÇ src/
Γöé   Γöé   Γö£ΓöÇΓöÇ pages/
Γöé   Γöé   Γöé   Γö£ΓöÇΓöÇ Landing.jsx       # Home page
Γöé   Γöé   Γöé   Γö£ΓöÇΓöÇ CropPredictor.jsx # Smart crop advisor
Γöé   Γöé   Γöé   Γö£ΓöÇΓöÇ PlantDoctor.jsx   # Disease diagnosis UI
Γöé   Γöé   Γöé   Γö£ΓöÇΓöÇ Economics.jsx     # Economic dashboard
Γöé   Γöé   Γöé   Γö£ΓöÇΓöÇ Chatbot.jsx       # AgroBot
Γöé   Γöé   Γöé   ΓööΓöÇΓöÇ Auth.jsx          # Login / Signup
Γöé   Γöé   Γö£ΓöÇΓöÇ App.jsx               # Router + layout
Γöé   Γöé   Γö£ΓöÇΓöÇ api.js                # Axios API client
Γöé   Γöé   Γö£ΓöÇΓöÇ i18n.jsx              # Multilingual strings
Γöé   Γöé   ΓööΓöÇΓöÇ index.css             # Global design system
Γöé   Γö£ΓöÇΓöÇ package.json
Γöé   ΓööΓöÇΓöÇ vite.config.js
Γö£ΓöÇΓöÇ datasets/                    # Training data (gitignored)
Γö£ΓöÇΓöÇ .gitignore
ΓööΓöÇΓöÇ README.md
```

---

## ≡ƒÜÇ Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Groq](https://console.groq.com) account (free tier works)
- A [Supabase](https://supabase.com) project
- API keys for OpenWeatherMap or Open-Meteo (free)

### 1. Clone the Repository

```bash
git clone https://github.com/Saumyajeet21/AgroSustain.git
cd AgroSustain
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment template and fill in your API keys
copy backend\.env.example backend\.env
```

Edit `backend/.env` with your API keys (see [Environment Variables](#-environment-variables)).

```bash
# Start the backend server
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Create frontend env file
echo VITE_API_BASE_URL=http://127.0.0.1:8000 > .env

npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Download Trained Model Weights

The model weights are not included in the repository (too large). To get them:

**Option A ΓÇö Use Groq Vision only** (works immediately without any local models):
- The system falls back to Groq Vision for all detections if no local model is found.

**Option B ΓÇö Train locally**:
```bash
# Download Indian crop datasets (requires Kaggle API token)
python backend/ml/download_datasets.py

# Train ResNet50 disease classifier
python backend/ml/train_resnet50.py

# Train YOLOv8 plant detector (optional, falls back to pretrained)
python backend/ml/train_yolo.py
```

---

## ≡ƒöæ Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
# ΓöÇΓöÇ Groq AI (Required) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
GROQ_API_KEY=your_groq_api_key_here
# Get free key at: https://console.groq.com

# ΓöÇΓöÇ Supabase (Required for Auth) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# ΓöÇΓöÇ Weather APIs (at least one required) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
OPENWEATHER_API_KEY=your_openweathermap_key
# Free tier: https://openweathermap.org/api

# ΓöÇΓöÇ Soil / Environment APIs ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# ISRIC SoilGrids: free, no key needed
# NASA POWER: free, no key needed
```

---

## ≡ƒôí API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/crop/predict` | XGBoost crop recommendation |
| `POST` | `/api/economics/calculate` | Financial projection for a crop |
| `POST` | `/api/disease/diagnose` | 4-stage plant disease diagnosis |
| `GET`  | `/api/disease/result/{job_id}/annotated` | Annotated image result |
| `GET`  | `/api/environment/live` | Live weather + soil data by GPS |
| `POST` | `/api/chat` | AgroBot conversational endpoint |
| `GET`  | `/docs` | Interactive Swagger UI |

---

## ≡ƒôè Economic Dashboard

The dashboard uses static crop profiles based on Indian agricultural averages:

| Metric | Source |
|--------|--------|
| Yield per hectare | ICAR + Ministry of Agriculture averages |
| Market price (Γé╣/ton) | Approximate APMC / MSP reference prices |
| Investment per hectare | Estimated seed + fertilizer + labor + irrigation costs |

**Supported crops**: Rice, Maize, Chickpea, Kidney Beans, Pigeon Peas, Mung Bean, Black Gram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee (22 crops)

---

## ≡ƒæ¿ΓÇì≡ƒÆ╗ Authors

Developed as a Minor Project ΓÇö **Department of Computer Science & Engineering**

- **Saumyajeet** ΓÇö [@Saumyajeet21](https://github.com/Saumyajeet21)

---

## ≡ƒôä License

This project is licensed under the MIT License.

---

<div align="center">
<i>Built for the future of Smart Agriculture ≡ƒî╛</i>
</div>
