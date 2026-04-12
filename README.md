# 🌱 AgroSustain: Smart Weather & Soil Based Crop Recommendation System

AgroSustain is an AI-driven agricultural platform designed to empower farmers to make data-driven, climate-resilient decisions. Aligning with **SDG 13 (Climate Action)**, this system combines real-time environmental APIs, advanced machine learning, and conversational AI to secure farming futures.

**Crucially, AgroSustain operates 100% in software—bypassing the need for physical IoT sensors** by leveraging geospatial and meteorological APIs based on the user's GPS location.

---

## ✨ Key Features

1. **Smart Crop & Fertilizer Recommendation** 
   - Predicts the ideal crop based on live weather and soil inputs fetched automatically for the user's location.
2. **Economic Dashboard**
   - Calculates estimated financial investments, expected crop yield, and projected profits based on the user's farm size.
3. **AI Plant Doctor Chatbot**
   - A multimodal chatbot where farmers can upload pictures of sick crops. The system locates the specific leaves, diagnoses the disease, and provides actionable, plain-English treatment advice.
4. **Hardware-Free Live Data Auto-Fetch**
   - Fetches live temperature, humidity, rainfall, and topsoil parameters (pH, bulk density, base nutrients) based on GPS coordinates.

---

## 🛠️ Architecture & Tech Stack

### 1. Frontend (The User Interface)
* **Framework:** React.js (Vite)
* **Styling:** Tailwind CSS
* **Icons:** Lucide-React
* **Data Visualization:** Recharts (for the financial dashboard)

### 2. Backend (The Core Engine)
* **Framework:** Python / FastAPI
* **Database & Authentication:** Supabase (PostgreSQL)
* **Image Processing:** OpenCV (`cv2`) for dynamic image cropping and bounding boxes in the computer vision pipeline.

### 3. External Integrations (Hardware Bypass)
* **Meteorological Data:** OpenWeatherMap API / Tomorrow.io
* **Geospatial Soil Data:** ISRIC SoilGrids REST API / NASA POWER
* **LLM Engine:** Google Gemini 1.5 Flash (Google AI Studio)

---

## 🧠 The AI Models

AgroSustain relies on a highly specialized multi-model architecture for maximum real-world reliability.

### Model 1: Crop Predictor (Tabular Data)
* **Algorithm:** XGBoost (Extreme Gradient Boosting)
* **Purpose:** Evaluates arrays of environmental metrics to recommend the single most viable crop.
* **Training Data:** Custom agricultural dataset mapping Nitrogen, Phosphorus, Potassium (NPK), pH, Rainfall, and Temperature to specific crops.

### Model 2: Plant Disease Diagnosis (Two-Stage Vision Pipeline)
To handle messy, real-world field photography, the visual diagnosis uses a "Detect-and-Classify" system:
1. **Stage A (The Scout - YOLOv8):** Scans the uploaded photo to detect leaves, isolating them from complex backgrounds, and draws strict bounding boxes. 
2. **Stage B (The Expert - ResNet50):** The FastAPI backend crops the image to the YOLO bounding box and passes the clean, isolated leaf to ResNet50 for highly accurate disease classification.

### Model 3: The Conversational Chatbot (Natural Language)
* **Algorithm:** Google Gemini 1.5 Flash
* **Purpose:** Translates the mathematical classifications from XGBoost and ResNet50 into friendly, localized, and actionable conversational advice for the farmer.

---

## 🚀 How It Works (The Data Flow)

### Scenario A: Recommending a Crop
1. The user navigates to the *Predict* page and clicks "Auto-Fetch Data".
2. The frontend sends their GPS coordinates to the FastAPI backend.
3. The backend concurrently queries **OpenWeatherMap** (for live climate data) and **ISRIC SoilGrids** (for soil pH/nutrients).
4. The backend processes this combined environmental array through the pre-trained **XGBoost model**.
5. The system returns the optimal crop recommendation to the frontend, displaying it alongside expected financial yields.

### Scenario B: Diagnosing a Plant Disease
1. Within the *Plant Doctor Chatbot*, the user uploads a photo of an afflicted field.
2. The backend runs the **YOLOv8** scout model to locate the precise leaves, using **OpenCV** to physically crop them.
3. The clean leaf crops are passed to the **ResNet50** expert model to yield a definitive disease diagnosis.
4. **OpenCV** draws bounding boxes and confidence labels back onto the original user image.
5. The backend hands the diagnosis context to the **Gemini API** to generate a friendly, step-by-step treatment plan.
6. The fully annotated image and the conversational treatment plan are returned to the user via the React chat interface.

---

*Built for the future of Smart Agriculture.*
