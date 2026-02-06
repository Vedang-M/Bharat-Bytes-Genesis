# Water Wallet API Documentation

## Overview

The Water Wallet API provides endpoints for water balance prediction, crop viability analysis, and smart crop recommendations for farmers.

**Base URL**: `http://localhost:8000`

## Quick Start for Frontend Integration

### 1. Install API Utility

Copy `frontend/src/utils/apiUtils.js` to your project.

### 2. Configure Backend URL

Create a `.env` file in your frontend:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Import and Use

```javascript
import { getWaterStatus, checkCropViability, getCropsList } from './utils/apiUtils';

// Get water status for a location
const waterData = await getWaterStatus(25.4358, 81.8463);
console.log(waterData.water_balance_mm); // Available water in mm
console.log(waterData.status); // "safe", "limited", or "critical"

// Check if a crop is viable
const cropResult = await checkCropViability('wheat', 25.4358, 81.8463);
console.log(cropResult.is_viable); // true/false
console.log(cropResult.recommendation); // "suitable", "caution", "not-recommended"

// Get list of crops
const crops = await getCropsList();
```

---

## Simplified API Endpoints (Recommended for Frontend)

### GET /api/water-status

Get water status using only latitude/longitude.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude (-90 to 90) |
| lon | float | Yes | Longitude (-180 to 180) |

**Example Request:**
```
GET /api/water-status?lat=25.4358&lon=81.8463
```

**Example Response:**
```json
{
  "location": {
    "latitude": 25.4358,
    "longitude": 81.8463,
    "state": "Uttar Pradesh",
    "district": "Prayagraj",
    "city": "Prayagraj"
  },
  "water_balance_mm": 450,
  "status": "limited",
  "crop": {
    "id": "wheat",
    "name": "Wheat",
    "water_required_mm": 450
  },
  "solvency": {
    "is_solvent": true,
    "probability": 0.85,
    "insolvency_in_days": null
  },
  "safe_to_sow": true,
  "weather_summary": {
    "forecast_rainfall_mm": 120.5,
    "forecast_et0_mm": 85.2,
    "avg_temp_c": 28.3
  },
  "groundwater_category": "Semi-Critical",
  "timestamp": "2026-02-06T10:30:00.000Z"
}
```

---

### GET /api/crop-check/{crop_id}

Check if a specific crop is viable for a location.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| crop_id | string | Crop identifier (e.g., 'wheat', 'sugarcane') |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |
| water_mm | float | No | Available water in mm (if already known) |

**Example Request:**
```
GET /api/crop-check/wheat?lat=25.4358&lon=81.8463
```

**Example Response:**
```json
{
  "crop_id": "wheat",
  "crop_name": "Wheat",
  "crop_name_hi": "गेहूं",
  "is_viable": true,
  "recommendation": "suitable",
  "water_required_mm": 450,
  "water_available_mm": 400,
  "water_ratio": 0.89,
  "water_deficit_mm": 50,
  "season_days": 120,
  "insolvency_warning_days": null,
  "message": "गेहूं के लिए पर्याप्त पानी उपलब्ध है। बुवाई की जा सकती है।",
  "message_en": "Sufficient water available for Wheat. Safe to sow."
}
```

**Recommendation Values:**
- `suitable` - Crop can be grown safely
- `caution` - Crop can be grown but may face water stress
- `not-recommended` - Insufficient water for this crop

---

### GET /api/smart-swap/{rejected_crop_id}

Get alternative crop recommendations when a crop is rejected.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| rejected_crop_id | string | The crop that was rejected |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| water_mm | float | Yes | Available water in mm |
| max_results | int | No | Number of recommendations (default: 3) |

**Example Request:**
```
GET /api/smart-swap/sugarcane?water_mm=400&max_results=3
```

**Example Response:**
```json
{
  "rejected_crop": "sugarcane",
  "available_water_mm": 400,
  "recommendations": [
    {
      "crop_id": "wheat",
      "crop_name": "Wheat",
      "crop_name_hi": "गेहूं",
      "water_required_mm": 450,
      "water_need_category": "medium",
      "profit_per_drop": 0.0112,
      "estimated_profit_inr": 59150,
      "water_fit_ratio": 0.89,
      "viability_score": 1.25,
      "image": "/wheat.webp"
    },
    {
      "crop_id": "chickpea",
      "crop_name": "Chickpea",
      "crop_name_hi": "चना",
      "water_required_mm": 300,
      "water_need_category": "low",
      "profit_per_drop": 0.0145,
      "estimated_profit_inr": 52000,
      "water_fit_ratio": 1.33,
      "viability_score": 1.93,
      "image": "/chickpea.webp"
    }
  ]
}
```

---

### GET /api/crops

Get list of all supported crops.

**Example Response:**
```json
{
  "crops": [
    {
      "id": "sugarcane",
      "name_en": "Sugarcane",
      "name_hi": "गन्ना",
      "water_req_mm": 1800,
      "water_need_category": "high",
      "season_days": 365,
      "image": "/sugarcane.webp"
    },
    {
      "id": "wheat",
      "name_en": "Wheat",
      "name_hi": "गेहूं",
      "water_req_mm": 450,
      "water_need_category": "medium",
      "season_days": 120,
      "image": "/wheat.webp"
    }
  ]
}
```

---

### GET /api/profit-ranking

Get all crops ranked by profit-per-drop (financial efficiency).

---

## Health Endpoints

### GET /health

Check API health status.

**Example Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Water Wallet API",
  "ml_available": true,
  "ml_models_ready": true,
  "crops_available": 15,
  "timestamp": "2026-02-06T10:30:00.000Z"
}
```

---

## Running the Backend

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Data Sources

- **Weather**: Visual Crossing Weather API (15-day forecast)
- **Soil**: ISRIC SoilGrids 2.0 REST API
- **Groundwater**: India WRIS (Central Ground Water Board)

---

## Water Need Categories

| Category | Water Requirement | Example Crops |
|----------|-------------------|---------------|
| High | > 800 mm | Sugarcane, Paddy, Basmati |
| Medium | 400-800 mm | Wheat, Maize, Cotton |
| Low | < 400 mm | Mustard, Chickpea, Millet |

---

## Status Definitions

| Status | Water Balance | Description |
|--------|---------------|-------------|
| Safe | ≥ 600 mm | Sufficient water for most crops |
| Limited | 300-600 mm | Choose medium/low water crops |
| Critical | < 300 mm | Only drought-resistant crops recommended |
