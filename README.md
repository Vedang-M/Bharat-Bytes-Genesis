<p align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/droplet.svg" width="80" height="80" alt="KisanSetu Logo"/>
</p>

<h1 align="center">🌾 KisanSetu - Water Wallet for Farmers</h1>

<p align="center">
  <strong>AI-Powered Agricultural Water Management & Crop Advisory Platform</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#installation">Installation</a> •
  <a href="#api-documentation">API Docs</a> •
  <a href="#ml-models">ML Models</a> •
  <a href="#contributors">Contributors</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/XGBoost-2.0+-FF6600?style=for-the-badge" alt="XGBoost"/>
  <img src="https://img.shields.io/badge/Firebase-Auth-FFCA28?style=for-the-badge&logo=firebase" alt="Firebase"/>
  <img src="https://img.shields.io/badge/Prophet-Forecasting-blue?style=for-the-badge" alt="Prophet"/>
</p>

---

## 📋 Overview

**KisanSetu** (किसान सेतु - "Farmer's Bridge") is a comprehensive digital platform designed to empower Indian farmers with data-driven insights for sustainable water management and profitable crop planning. The platform combines real-time weather data, soil analysis, machine learning predictions, and market intelligence to provide actionable farming recommendations.

### 🎯 Problem Statement

Indian farmers face critical challenges:
- **Water Scarcity**: Declining groundwater levels and unpredictable rainfall
- **Crop Selection**: Difficulty choosing crops that match available water resources
- **Market Access**: Limited visibility into market prices and buyer demand
- **Financial Risk**: Crop failures due to water mismanagement lead to debt cycles

### 💡 Our Solution

KisanSetu provides:
- **Water Wallet**: Real-time tracking of water budget (rainfall + groundwater + soil storage)
- **Smart Crop Advisory**: AI-powered recommendations based on water availability
- **Solvency Prediction**: Early warning system for water deficit risks
- **Marketplace**: Water-filtered crop marketplace with buyer signals
- **Bilingual Support**: Full Hindi and English localization

---

## ✨ Features

### 🌊 Water Management
- **Real-time Water Balance** - Calculate available water from rainfall, groundwater, and soil storage
- **Solvency Status** - Visual indicator showing if current water supports planned crops
- **Insolvency Day Prediction** - Forecast when water deficit may occur
- **Groundwater Depth Forecasting** - 90-day Prophet-based predictions

### 🌱 Crop Planning
- **Sowing Swap Analysis** - Check if intended crop is viable with current water
- **Alternative Crop Suggestions** - Get recommendations for water-efficient alternatives
- **Profit-Per-Drop Metric** - Rank crops by income earned per mm of water used
- **Seasonal Filtering** - Kharif, Rabi, and Zaid season support

### 📊 ML-Powered Predictions
- **Yield Estimation** - Dynamic yield prediction based on environmental conditions
- **Viability Classification** - Binary classification of crop feasibility
- **Water Balance Regression** - Precise water availability calculations
- **Groundwater Forecasting** - Time-series predictions with soil regressors

### 🏪 Marketplace
- **Water-Safe Crops Only** - Shows only crops that fit your water budget
- **Buyer Signals** - Mandi names, prices, distances, and demand levels
- **Efficiency Ranking** - Crops sorted by profit-per-drop efficiency
- **Local Market Data** - Maharashtra APMC market integration

### 👥 User Roles
- **Farmer** - Core water wallet and crop advisory features
- **Sarpanch (Village Head)** - Dashboard for community-level water oversight
- **Admin** - Platform administration and analytics

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2 | UI Framework |
| Vite | 7.2 | Build Tool & Dev Server |
| Tailwind CSS | 3.4 | Utility-First Styling |
| React Router | 7.13 | Client-Side Routing |
| Chart.js | 4.5 | Data Visualization |
| Lucide React | 0.563 | Icon Library |
| Firebase | 12.9 | Authentication |
| React Toastify | 11.0 | Notifications |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.104+ | REST API Framework |
| Uvicorn | 0.24+ | ASGI Server |
| Pydantic | 2.5+ | Data Validation |
| Firebase Admin | 6.4+ | Auth Verification |
| aiohttp | 3.9+ | Async HTTP Client |

### Machine Learning
| Technology | Version | Purpose |
|------------|---------|---------|
| XGBoost | 2.0+ | Gradient Boosting Models |
| Scikit-learn | 1.3+ | ML Utilities & Metrics |
| Prophet | Latest | Time-Series Forecasting |
| NumPy | 1.24+ | Numerical Computing |
| Pandas | 2.0+ | Data Manipulation |
| Joblib | 1.3+ | Model Serialization |

### External APIs
| API | Provider | Purpose |
|-----|----------|---------|
| Weather Forecast | Visual Crossing | 15-day weather, ET0, rainfall |
| Soil Data | ISRIC SoilGrids | Clay, sand, pH, AWC, organic carbon |
| Authentication | Firebase | Phone/Email authentication |

---

## 📁 Project Structure

```
Bharat-Bytes-Genesis/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── routes/            # API endpoints
│   │   │   ├── auth.py        # Authentication routes
│   │   │   ├── water_status.py # Water balance API
│   │   │   ├── ml.py          # ML prediction endpoints
│   │   │   ├── sowing_swap.py # Crop viability & marketplace
│   │   │   ├── admin.py       # Admin operations
│   │   │   └── health.py      # Health checks
│   │   ├── schemas/           # Pydantic models
│   │   └── services/          # Business logic
│   ├── data/                  # Crop & buyer datasets
│   │   ├── crop_data.json     # 23 crops with water requirements
│   │   └── buyer_data.json    # Maharashtra APMC market data
│   └── requirements.txt
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Navigation.jsx
│   │   │   ├── WaterStatusScreen.jsx
│   │   │   ├── CropSelect.jsx
│   │   │   ├── SwapResultsModal.jsx
│   │   │   └── ...
│   │   ├── pages/             # Page components
│   │   │   └── Marketplace.jsx
│   │   ├── sarpanch/          # Sarpanch dashboard
│   │   ├── context/           # React contexts
│   │   └── utils/             # Utility functions
│   ├── package.json
│   └── vite.config.js
│
├── ml/                         # Machine Learning Module
│   ├── models/                # Trained model files (.joblib)
│   │   ├── water_balance.joblib
│   │   ├── solvency.joblib
│   │   ├── insolvency_day.joblib
│   │   ├── yield_predictor.joblib
│   │   └── groundwater_prophet_real_soil.joblib
│   ├── scripts/               # Training scripts
│   │   ├── train_models.py
│   │   ├── train_yield_model.py
│   │   └── train_groundwater_model.py
│   ├── metrics/               # Model performance metrics
│   ├── config.py              # ML configuration & crop database
│   ├── data_fetchers.py       # API data fetching
│   ├── water_wallet_model.py  # Main ML model class
│   └── model_metrics.py       # Metrics tracking system
│
└── firebase-service-account.json  # Firebase credentials
```

---

## 🚀 Installation

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **npm** or **yarn**
- **Firebase Project** (for authentication)
- **Visual Crossing API Key** (for weather data)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Bharat-Bytes-Genesis.git
cd Bharat-Bytes-Genesis
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

#### Backend Environment Variables (.env)

```env
# Visual Crossing Weather API
VISUAL_CROSSING_API_KEY=your_api_key_here

# Firebase (optional, for authentication)
GOOGLE_APPLICATION_CREDENTIALS=../firebase-service-account.json

# Model Cache
MODEL_CACHE_DIR=../ml/models
MODEL_CACHE_DAYS=7
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local with your Firebase config
```

#### Frontend Environment Variables (.env.local)

```env
# API URL
VITE_API_URL=http://localhost:8000

# Firebase Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### 4. Train ML Models (Optional)

```bash
# Navigate to project root
cd ..

# Train core models
python -m ml.scripts.train_models

# Train yield predictor
python -m ml.scripts.train_yield_model

# Train groundwater forecaster
python -m ml.scripts.train_groundwater_model
```

### 5. Run the Application

```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/verify-token` | Verify Firebase token |
| GET | `/api/auth/profile` | Get user profile |

### Water Status Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/water-status` | Get water balance for location |
| POST | `/api/water-status/calculate` | Calculate detailed water budget |
| GET | `/api/water-status/forecast` | Get groundwater forecast |

### ML Prediction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ml/water-balance/predict` | Predict water availability |
| POST | `/ml/solvency/predict` | Predict solvency status |
| POST | `/ml/insolvency-day/predict` | Predict days until insolvency |
| POST | `/ml/yield/predict` | Predict crop yield |

### Sowing Swap Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sowing-swap` | Check crop viability & get alternatives |
| GET | `/api/crops/water-requirements` | List all crops with water needs |
| GET | `/api/marketplace` | Get water-filtered crop marketplace |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| GET | `/api/admin/stats` | Get platform statistics |

---

## 🤖 ML Models

### Model Overview

| Model | Algorithm | Type | Purpose |
|-------|-----------|------|---------|
| Water Balance | XGBoost Regressor | Regression | Predict total available water (mm) |
| Solvency | XGBoost Classifier | Classification | Classify as Solvent/Risky |
| Insolvency Day | XGBoost Regressor | Regression | Predict days until water deficit |
| Yield Predictor | XGBoost Regressor | Regression | Predict crop yield (quintals/acre) |
| Groundwater Prophet | Prophet | Forecasting | 90-day groundwater depth forecast |
| Crop Viability | XGBoost Classifier | Classification | Binary crop feasibility |

### Feature Engineering

All models use a consistent 7-feature vector:

```python
features = [
    total_rainfall_mm,      # From Visual Crossing API
    total_et0_mm,           # Evapotranspiration
    groundwater_recharge_mm,# Estimated from soil
    soil_awc_mm_m,          # From ISRIC SoilGrids
    crop_water_req_mm,      # From crop database
    groundwater_depth_m,    # Measured/estimated
    temperature_avg_c       # Average temperature
]
```

### XGBoost Parameters

```python
XGBOOST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "objective": "reg:squarederror",
    "random_state": 42
}
```

### Metrics Tracking

The `ModelMetrics` class automatically tracks:

**Classification Models:**
- Accuracy, Precision, Recall, F1-Score
- Confusion Matrix
- Per-class metrics

**Regression Models:**
- R² Score, MSE, RMSE, MAE, MAPE

**Forecasting Models:**
- RMSE, MAE, MAPE
- Confidence Interval Coverage

---

## 🌾 Crop Database

The platform supports **26 crops** across three water categories:

### High Water Crops (>700mm)
- Sugarcane (1800mm)
- Paddy/Rice (1200mm)
- Basmati Rice (1400mm)

### Medium Water Crops (400-700mm)
- Wheat (450mm)
- Maize (500mm)
- Cotton (700mm)
- Potato (500mm)
- Soybean (450mm)
- Groundnut (500mm)
- Tomato (600mm)

### Low Water Crops (<400mm)
- Mustard (250mm)
- Chickpea/Chana (300mm)
- Lentil/Masoor (280mm)
- Pigeon Pea/Arhar (350mm)
- Moong Dal (300mm)
- Bajra/Pearl Millet (350mm)
- Jowar/Sorghum (400mm)
- Sesame/Til (300mm)

---

## 🌐 Bilingual Support

The platform fully supports **Hindi (हिंदी)** and **English**:

- All UI labels and buttons
- Crop names (e.g., गेहूं / Wheat)
- Error messages and notifications
- Advisory recommendations
- Market information

---

## 📱 Progressive Web App (PWA)

KisanSetu is built as a PWA with:

- **Offline Support** - Works without internet connection
- **Installable** - Add to home screen on mobile
- **Responsive Design** - Mobile-first approach
- **Fast Loading** - Optimized for slow networks

---

## 🔒 Security

- **Firebase Authentication** - Secure phone/email login
- **Token Verification** - JWT-based API authentication
- **Role-Based Access** - Farmer, Sarpanch, Admin roles
- **CORS Protection** - Configured for production domains
- **Input Validation** - Pydantic schema validation

---

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest tests/

# Run frontend tests
cd frontend
npm run test

# Test ML models
python -m ml.scripts.test_models
```

---

## 📈 Performance

- **API Response Time**: <200ms average
- **ML Inference**: <50ms per prediction
- **Frontend Load**: <2s initial load
- **Lighthouse Score**: 90+ (PWA optimized)

---

## 👥 Contributors

This project was built by **Team Bharat Bytes**:

- **Vedang Mendhurwar** — [@Vedang-M](https://github.com/Vedang-M)
- **Ruturaj Rajwade** — [@RAR2025](https://github.com/RAR2025)
- **Abhishek Gore** — [@abhishek1709-vesit](https://github.com/abhishek1709-vesit)
- **Harshal Pednekar** — [@harshalnnpednekar](https://github.com/harshalnnpednekar)

---

## 🙏 Acknowledgments

- **Visual Crossing** - Weather data API
- **ISRIC SoilGrids** - Soil data API
- **Government of India** - MSP and crop data
- **Firebase** - Authentication services
- **Meta/Facebook** - Prophet library

---

<p align="center">
  Made with ❤️ for Indian Farmers
</p>

<p align="center">
  <strong>किसान सेतु - हर बूंद का हिसाब</strong><br>
  <em>KisanSetu - Every Drop Counts</em>
</p>
