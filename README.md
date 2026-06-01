# 🌱 AgroSustain

> AI-powered smart farming platform for Indian farmers — crop recommendations, plant disease diagnosis, and economic planning.

---

## What it does

AgroSustain helps farmers make better decisions using AI and real-time data — no hardware or IoT sensors needed.

| Feature | Description |
|---------|-------------|
| 🌾 **Crop Advisor** | Recommends the best crop based on live weather + soil data from your GPS location |
| 🔬 **Plant Doctor** | Upload any plant photo — AI diagnoses disease and prescribes treatment |
| 📊 **Economics** | Projects yield, investment, revenue, and ROI for any crop and farm size |
| 🤖 **AgroBot** | Conversational AI chatbot for farming queries (Hindi + English) |

---

## Tech Stack

**Frontend** — React 18, Vite, Recharts, Lucide Icons

**Backend** — Python, FastAPI, Supabase (PostgreSQL)

**AI Models**
- XGBoost — crop recommendation from soil + weather data
- YOLOv8 — detects plant regions (leaf, stem, root, fruit) in photos
- ResNet50 — classifies 38 plant diseases (PlantVillage dataset)
- Groq Vision (Llama 4 Scout) — identifies any crop universally, including wheat, rice, mango
- Groq LLM (Llama 3.3 70B) — treatment advice + chatbot

**APIs** — OpenWeatherMap, ISRIC SoilGrids, NASA POWER

---

## Plant Doctor Pipeline

```
📷 Upload image
     ↓
[YOLO]  →  Detect plant regions with bounding boxes
     ↓
[Groq Vision]  →  Identify crop + disease (works for ANY crop)
     ↓
[ResNet50]  →  Precise disease classification for known crops
     ↓
[Groq LLM]  →  Treatment advice with Indian pesticide names
     ↓
✅  Annotated image + diagnosis + treatment plan
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free)
- [Supabase](https://supabase.com) project

### Backend

```bash
git clone https://github.com/Saumyajeet21/AgroSustain.git
cd AgroSustain

python -m venv venv
venv\Scripts\activate

pip install -r backend/requirements.txt

copy backend\.env.example backend\.env
# Fill in your API keys in backend/.env

uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and set:

```
GROQ_API_KEY=           # https://console.groq.com
SUPABASE_URL=           # your supabase project URL
SUPABASE_KEY=           # supabase anon key
OPENWEATHER_API_KEY=    # https://openweathermap.org (free tier)
```

---

## Project Structure

```
AgroSustain/
├── backend/
│   ├── main.py                   # All API routes (FastAPI)
│   ├── requirements.txt
│   ├── .env.example
│   └── ml/
│       ├── crop_predictor.py     # XGBoost inference
│       ├── disease_classifier.py # ResNet50 inference
│       ├── leaf_detector.py      # YOLOv8 region detection
│       ├── vision_analyzer.py    # Groq Vision wrapper
│       ├── economics.py          # Financial calculations
│       ├── train_resnet50.py     # Training script
│       └── download_datasets.py  # Kaggle dataset downloader
└── frontend/
    └── src/
        ├── pages/
        │   ├── CropPredictor.jsx
        │   ├── PlantDoctor.jsx
        │   ├── Economics.jsx
        │   └── Chatbot.jsx
        ├── App.jsx
        └── api.js
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/crop/predict` | POST | Crop recommendation |
| `/api/disease/diagnose` | POST | Plant disease diagnosis |
| `/api/economics/calculate` | POST | Financial projection |
| `/api/environment/live` | GET | Live weather + soil data |
| `/api/chat` | POST | AgroBot chatbot |
| `/docs` | GET | Swagger UI |

---

*Built as a Minor Project — Computer Science & Engineering*
