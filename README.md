# 🌱 AgroSustain — AI-Powered Smart Farming Platform

> An intelligent agricultural platform that helps Indian farmers make smarter decisions using AI, real-time weather & soil data, and computer vision — **no hardware or IoT sensors required.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat)](https://console.groq.com)

---

## 📌 About the Project

AgroSustain is a full-stack web application built as a **Minor Project** for the Department of Computer Science & Engineering. It addresses a critical gap in Indian agriculture — most farmers lack access to timely, data-driven guidance on what to grow, how to detect crop diseases, and whether a crop is financially viable for their land.

The platform operates **completely in software**, automatically fetching live weather and soil data from the user's GPS coordinates, eliminating the need for expensive IoT sensors or manual data entry.

It is aligned with **UN SDG 2 (Zero Hunger)** and **UN SDG 13 (Climate Action)**.

---

## ✨ Features

### 🌾 Smart Crop Advisor
Automatically fetches live temperature, humidity, rainfall, and soil parameters (pH, nitrogen, phosphorus, potassium) based on the user's GPS location. These are passed through a trained **XGBoost model** that recommends the most suitable crop with confidence scores and alternatives.

### 🔬 AI Plant Doctor
A multi-stage computer vision pipeline that diagnoses plant diseases from any photo:
- **YOLOv8** detects and crops plant regions (leaf, stem, root, fruit, whole plant)
- **Groq Vision (Llama 4 Scout)** universally identifies crop and disease — works on wheat, rice, mango, and any crop even outside the training dataset
- **ResNet50** provides precise disease classification across 38 PlantVillage classes
- **Groq LLM** generates step-by-step treatment advice with Indian pesticide/fungicide names
- Smart arbitration logic decides which model result to trust based on YOLO's detections

### 📊 Economic Dashboard
Enter a crop name and farm area (in hectares) to instantly see:
- Projected total yield (metric tons)
- Estimated investment (seed + fertilizer + labor + irrigation)
- Expected revenue and net profit
- Return on Investment (ROI) and profit margin
- Visual bar chart and donut chart breakdown

Data is based on Indian agricultural averages from ICAR and Ministry of Agriculture references. Covers 22 major Indian crops.

### 🤖 AgroBot Chatbot
Conversational AI assistant powered by **Groq (Llama 3.3 70B Versatile)**. Farmers can ask questions about pest management, irrigation, market prices, and more. Supports Hindi and English with session-based conversation history.

### 🌐 Live Environment Data (Hardware-Free)
- **Weather**: OpenWeatherMap / Open-Meteo APIs
- **Soil properties**: ISRIC SoilGrids REST API (pH, organic carbon, texture)
- **Macronutrients**: Estimated via NASA POWER API

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, Vanilla CSS, Recharts, Lucide Icons |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database & Auth | Supabase (PostgreSQL) |
| ML — Crop | XGBoost, scikit-learn |
| ML — Vision | YOLOv8n (Ultralytics), ResNet50 (PyTorch) |
| AI — Vision | Groq Vision API (Llama 4 Scout 17B) |
| AI — Language | Groq API (Llama 3.3 70B Versatile) |
| Image Processing | OpenCV, Pillow |
| Environment Data | OpenWeatherMap, ISRIC SoilGrids, NASA POWER |
| i18n | Custom React context (English + Hindi) |

---

## 🧠 How the Plant Doctor Works

```
📷  User uploads a plant photo
        │
        ▼
  ┌─────────────┐
  │  Stage A    │  YOLOv8 detects plant regions (leaf / stem / root / fruit)
  │  YOLO       │  Draws bounding boxes, crops each region
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Stage B    │  Groq Vision (Llama 4 Scout) analyzes the full image
  │  Groq Vision│  Identifies: crop species, plant part, disease, severity
  └──────┬──────┘  Works for ANY crop — including wheat, rice, mango
         │
         ▼
  ┌─────────────┐
  │  Stage C    │  ResNet50 classifies each YOLO-cropped region
  │  ResNet50   │  38-class PlantVillage disease classifier
  └──────┬──────┘  Smart arbitration: picks the most reliable result
         │
         ▼
  ┌─────────────┐
  │  Stage D    │  Groq LLM (Llama 3.3 70B) generates treatment advice
  │  Groq LLM   │  Includes Indian fungicide/pesticide names, actionable steps
  └──────┬──────┘
         │
         ▼
✅  Annotated image + disease diagnosis + treatment plan
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+  
- Node.js 18+  
- [Free Groq API key](https://console.groq.com)  
- [Supabase project](https://supabase.com) (for authentication)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/Saumyajeet21/AgroSustain.git
cd AgroSustain

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / Mac

pip install -r backend/requirements.txt

# Set up environment variables
copy backend\.env.example backend\.env
# Open backend/.env and add your API keys
```

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Start Backend

```bash
# From project root
uvicorn backend.main:app --reload --port 8000
```

Open **http://localhost:5173** in your browser.

---

## 🔑 Environment Variables

Fill in `backend/.env` (template in `backend/.env.example`):

```env
GROQ_API_KEY=          # Required — get free at console.groq.com
SUPABASE_URL=          # Your Supabase project URL
SUPABASE_KEY=          # Supabase anon/public key
OPENWEATHER_API_KEY=   # Optional — free at openweathermap.org
```

---

## 📁 Project Structure

```
AgroSustain/
├── backend/
│   ├── main.py                    # FastAPI app — all routes & pipeline
│   ├── requirements.txt
│   ├── .env.example               # Environment variable template
│   ├── setup_tables.sql           # Supabase database schema
│   └── ml/
│       ├── crop_predictor.py      # XGBoost crop recommendation
│       ├── disease_classifier.py  # ResNet50 disease classification
│       ├── leaf_detector.py       # YOLOv8 plant region detection
│       ├── vision_analyzer.py     # Groq Vision (Llama 4 Scout) wrapper
│       ├── economics.py           # Financial projection calculator
│       ├── train_resnet50.py      # ResNet50 training script
│       ├── train_yolo.py          # YOLOv8 training script
│       └── download_datasets.py   # Indian crop dataset downloader
└── frontend/
    └── src/
        ├── pages/
        │   ├── Landing.jsx         # Home page
        │   ├── CropPredictor.jsx   # Crop advisor
        │   ├── PlantDoctor.jsx     # Disease diagnosis UI
        │   ├── Economics.jsx       # Financial dashboard
        │   ├── Chatbot.jsx         # AgroBot UI
        │   └── Auth.jsx            # Login / Signup
        ├── App.jsx                 # Router & layout
        ├── api.js                  # Axios API client
        └── i18n.jsx                # Hindi / English strings
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/crop/predict` | XGBoost crop recommendation |
| `POST` | `/api/disease/diagnose` | 4-stage plant disease diagnosis |
| `GET`  | `/api/disease/result/{id}/annotated` | Annotated result image |
| `POST` | `/api/economics/calculate` | Crop financial projection |
| `GET`  | `/api/environment/live` | Live weather + soil data by GPS |
| `POST` | `/api/chat` | AgroBot conversational endpoint |
| `GET`  | `/docs` | Interactive Swagger UI |

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

*Built for the future of Smart Agriculture 🌾 — Minor Project, Department of CSE*
