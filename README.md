# 🌱 AgroSustain — AI-Powered Smart Farming Platform

<div align="center">

![AgroSustain Banner](https://img.shields.io/badge/AgroSustain-Smart%20Farming-38bd6c?style=for-the-badge&logo=leaf&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**An AI-driven agricultural platform empowering Indian farmers with data-driven, climate-resilient decisions.**

*Aligned with **SDG 13** (Climate Action)*

</div>

---

## 📋 Table of Contents

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

## 🌾 Overview

AgroSustain is a full-stack web application that helps Indian farmers make smarter agricultural decisions by combining:

- **Real-time environmental data** fetched automatically from GPS coordinates (no IoT hardware needed)
- **Machine learning** for crop recommendation (XGBoost) and plant disease diagnosis (YOLOv8 + ResNet50)
- **Groq Vision AI** (Llama 4 Scout) for universal crop identification — works on wheat, rice, mango, and any crop even if not in the training dataset
- **Groq LLM** (Llama 3.3 70B) for conversational treatment advice and farming chatbot

> **Hardware-Free**: Operates 100% in software by leveraging geospatial and meteorological APIs — no physical IoT sensors required.

---

## ✨ Key Features

### 1. 🌿 Smart Crop Advisor
- Auto-fetches live weather (temperature, humidity, rainfall) and soil data (pH, NPK, bulk density) from the user's GPS location
- Runs the environmental parameters through a trained **XGBoost classifier** to recommend the optimal crop
- Shows confidence scores and alternative crop suggestions
- Supports 22 major Indian crops

### 2. 🔬 AI Plant Doctor (4-Stage Vision Pipeline)
- Upload any photo of a plant — leaf, stem, root, fruit, or whole plant
- **Stage A**: YOLOv8 detects and crops all plant regions with bounding boxes
- **Stage B**: Groq Vision (Llama 4 Scout) universally identifies the crop and disease — works even for wheat, rice, mango, orange not in the training data
- **Stage C**: ResNet50 provides precise disease classification for its 38 known classes (PlantVillage dataset)
- **Stage D**: Groq LLM (Llama 3.3 70B) generates actionable treatment advice with Indian pesticide recommendations
- Smart arbitration: uses YOLO region detection to decide whether to trust ResNet or Groq Vision

### 3. 📊 Economic Dashboard
- Select any crop and enter your farm area (in hectares)
- Calculates projected yield, total investment, gross revenue, net profit, ROI, and profit margin
- Based on Indian agricultural averages (ICAR / Ministry of Agriculture data)
- Interactive bar chart and donut chart breakdowns (Recharts)

### 4. 🤖 AgroBot Chatbot
- Conversational AI powered by Groq (Llama 3.3 70B Versatile)
- Answers farming questions, pest management queries, market advice
- Multilingual support (Hindi/English toggle)
- Session-based conversation history

### 5. 🌐 Live Environment Data (Hardware Bypass)
- **Weather**: OpenWeatherMap / Open-Meteo APIs
- **Soil**: ISRIC SoilGrids REST API (pH, organic carbon, bulk density, sand/clay/silt)
- **Macronutrients**: NASA POWER API estimates

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Vanilla CSS, Recharts, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Auth & DB** | Supabase (PostgreSQL) |
| **ML — Crop** | XGBoost, scikit-learn |
| **ML — Vision** | YOLOv8n (Ultralytics), ResNet50 (PyTorch/torchvision) |
| **AI — Vision** | Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct) |
| **AI — LLM** | Groq API (llama-3.3-70b-versatile) |
| **Image Processing** | OpenCV (cv2), Pillow |
| **Weather APIs** | OpenWeatherMap, Open-Meteo |
| **Soil APIs** | ISRIC SoilGrids, NASA POWER |
| **i18n** | Custom React i18n (English + Hindi) |

---

## 🧠 AI Models & Pipeline

### Model 1: Crop Predictor

```
Input: N, P, K, pH, Rainfall, Temperature, Humidity
  ↓
XGBoost Classifier (trained on Indian crop dataset)
  ↓
Output: Recommended crop + confidence + top alternatives
```

- **Algorithm**: XGBoost (Extreme Gradient Boosting)
- **Features**: 7 environmental parameters
- **Classes**: 22 Indian crops (Rice, Maize, Chickpea, Mango, Cotton, etc.)
- **Training data**: Custom dataset mapping NPK + climate to optimal crop

### Model 2: Plant Disease Diagnosis (4-Stage Pipeline)

```
Upload Image
  ↓
[Stage A] YOLOv8n  →  Detect & crop plant regions (leaf/stem/root/fruit)
  ↓
[Stage B] Groq Vision (Llama 4 Scout)  →  Universal crop & disease ID
  ↓
[Stage C] ResNet50  →  Precise disease classification (38 PlantVillage classes)
       Smart arbitration: picks best result based on YOLO regions + crop domain
  ↓
[Stage D] Groq LLM (Llama 3.3 70B)  →  Treatment advice with Indian context
  ↓
Output: Annotated image + diagnosis + AI treatment plan
```

**PlantVillage Classes (ResNet50)**: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Bell Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato — 38 diseases total.

**Groq Vision handles**: Wheat, Rice, Mango, Sugarcane, Cotton, Chickpea, Banana, and any crop from any angle.

**Smart Arbitration Logic**:
- If YOLO found leaf regions + ResNet is confident + crop matches training domain → ResNet wins (precise)
- If YOLO fell back to full image + Vision sees non-domain crop → Groq Vision wins (universal)
- Result cached per disease for faster subsequent requests

### Model 3: AgroBot (Conversational)

- **Model**: Groq `llama-3.3-70b-versatile`
- Session-based with conversation history
- Context-aware farming Q&A

---

## 📁 Project Structure

```
AgroSustain/
├── backend/
│   ├── main.py                  # FastAPI app — all routes
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variable template
│   ├── setup_tables.sql         # Supabase schema
│   ├── ml/
│   │   ├── crop_predictor.py    # XGBoost inference
│   │   ├── disease_classifier.py# ResNet50 inference
│   │   ├── leaf_detector.py     # YOLOv8 plant region detection
│   │   ├── vision_analyzer.py   # Groq Vision (Llama 4 Scout) wrapper
│   │   ├── economics.py         # Economic calculations
│   │   ├── download_datasets.py # Indian crop dataset downloader (Kaggle)
│   │   ├── train_resnet50.py    # ResNet50 training script
│   │   └── train_yolo.py        # YOLOv8 training script
│   ├── models/
│   │   ├── disease_classes.json # ResNet50 class labels
│   │   └── *.pth / *.pt         # Trained weights (gitignored — large files)
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx       # Home page
│   │   │   ├── CropPredictor.jsx # Smart crop advisor
│   │   │   ├── PlantDoctor.jsx   # Disease diagnosis UI
│   │   │   ├── Economics.jsx     # Economic dashboard
│   │   │   ├── Chatbot.jsx       # AgroBot
│   │   │   └── Auth.jsx          # Login / Signup
│   │   ├── App.jsx               # Router + layout
│   │   ├── api.js                # Axios API client
│   │   ├── i18n.jsx              # Multilingual strings
│   │   └── index.css             # Global design system
│   ├── package.json
│   └── vite.config.js
├── datasets/                    # Training data (gitignored)
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Groq](https://console.groq.com) account (free tier works)
- A [Supabase](https://supabase.com) project
- API key for [OpenWeatherMap](https://openweathermap.org/api) (free)

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
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Model Weights

The trained model weights are not included in the repository (too large for GitHub). Options:

**Option A — Groq Vision only** (works immediately, no local models needed):
The system automatically falls back to Groq Vision for all detections if no local model files are found.

**Option B — Train locally**:
```bash
# Download Indian crop datasets (requires Kaggle API token)
python backend/ml/download_datasets.py

# Train ResNet50 disease classifier (~2-4 hours on GPU)
python backend/ml/train_resnet50.py

# Train YOLOv8 plant detector (optional)
python backend/ml/train_yolo.py
```

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
# Groq AI (Required)
GROQ_API_KEY=your_groq_api_key_here
# Get free key at: https://console.groq.com

# Supabase (Required for Auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Weather API (at least one required)
OPENWEATHER_API_KEY=your_openweathermap_key
# Free tier: https://openweathermap.org/api
```

---

## 📡 API Reference

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

## 📊 Economic Dashboard

The dashboard uses crop profiles based on Indian agricultural averages:

| Metric | Source Basis |
|--------|-------------|
| Yield per hectare | ICAR + Ministry of Agriculture averages |
| Market price (Rs/ton) | Approximate APMC / MSP reference prices |
| Investment per hectare | Estimated seed + fertilizer + labor + irrigation |

**Supported crops (22 total)**: Rice, Maize, Chickpea, Kidney Beans, Pigeon Peas, Mung Bean, Black Gram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee

---

## 👨‍💻 Authors

Developed as a Minor Project — **Department of CSE(AIML)**

- **Saumyajeet** — [@Saumyajeet21](https://github.com/Saumyajeet21)



