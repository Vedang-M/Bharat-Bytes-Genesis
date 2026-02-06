# Bharat Bytes Genesis - API Key & Frontend Integration Guide

## Your Backend API Key

Your generated backend API key is:

```
API_KEY=bharat-bytes-genesis-2026-api-key-v1
```

**⚠️ IMPORTANT: Keep this key secure and do not commit it to your repository!**

---

## Quick Start

### 1. Backend Setup

The FastAPI backend is now fully functional. To start the server:

```bash
cd backend
source venv/bin/activate
cd app
python main.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 2. Frontend Integration

#### Step 1: Create Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=bharat-bytes-genesis-2026-api-key-v1
```

#### Step 2: Create API Configuration File

Create `frontend/src/config/api.js`:

```javascript
// API Configuration
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  apiKey: import.meta.env.VITE_API_KEY || 'bharat-bytes-genesis-2026-api-key-v1',
  timeout: 30000, // 30 seconds
};

export default API_CONFIG;
```

#### Step 3: Create API Service

Create `frontend/src/services/apiService.js`:

```javascript
import API_CONFIG from '../config/api';

class APIService {
  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.apiKey = API_CONFIG.apiKey;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': this.apiKey,
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Get water status for a location
  async getWaterStatus(location) {
    return this.request('/api/water-status', {
      method: 'POST',
      body: JSON.stringify({ location }),
    });
  }

  // Get crop recommendations for a location
  async getCropRecommendations(location, cropName = null) {
    const body = { location };
    if (cropName) {
      body.crop_name = cropName;
    }

    return this.request('/api/crop-recommendation', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health', {
      method: 'GET',
    });
  }
}

// Export singleton instance
const apiService = new APIService();
export default apiService;
```

#### Step 4: Use in Components

Example usage in `WaterStatusScreen.jsx`:

```javascript
import { useEffect, useState } from 'react';
import apiService from '../services/apiService';

function WaterStatusScreen() {
  const [waterData, setWaterData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWaterStatus = async (location) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getWaterStatus(location);
      setWaterData(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch water status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Get location and fetch water status
    const userLocation = JSON.parse(localStorage.getItem('user_location'));
    if (userLocation?.city) {
      fetchWaterStatus(userLocation.city);
    }
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!waterData) return <div>No data available</div>;

  return (
    <div>
      <h1>Water Status for {waterData.location}</h1>
      <p>Status: {waterData.status}</p>
      <p>Water Availability: {waterData.water_availability}mm</p>
      <p>Safe to Sow: {waterData.safe_to_sow ? 'Yes' : 'No'}</p>
      <p>Insolvency in Days: {waterData.insolvency_in_days}</p>
    </div>
  );
}
```

Example usage in `CropSelect.jsx`:

```javascript
import { useEffect, useState } from 'react';
import apiService from '../services/apiService';

function CropSelect() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      const userLocation = JSON.parse(localStorage.getItem('user_location'));
      
      try {
        const data = await apiService.getCropRecommendations(userLocation?.city || 'Delhi');
        setRecommendations(data.recommendations);
      } catch (err) {
        console.error('Failed to fetch crop recommendations:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  return (
    <div>
      <h2>Crop Recommendations</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="grid">
          {recommendations.map((crop) => (
            <div key={crop.crop_id} className="crop-card">
              <h3>{crop.crop_name}</h3>
              <p>Water Need: {crop.water_need}</p>
              <p>Recommendation: {crop.recommendation}</p>
              <p>Score: {crop.suitability_score}/100</p>
              <p>{crop.reasoning}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## API Endpoints Reference

### 1. Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "message": "API is running smoothly",
  "version": "1.0.0",
  "timestamp": "2026-02-06T08:42:18.863Z"
}
```

### 2. Water Status

**Endpoint**: `POST /api/water-status`

**Request Body**:
```json
{
  "location": "Mumbai"
}
```

**Response**:
```json
{
  "location": "Mumbai",
  "insolvency_in_days": 25,
  "safe_to_sow": true,
  "status": "safe",
  "water_availability": 750,
  "timestamp": "2026-02-06T08:42:18.863Z"
}
```

**Status Values**:
- `safe`: Water availability is good (>15 days)
- `limited`: Water availability is moderate (1-15 days)
- `critical`: Water shortage (0 days)

### 3. Crop Recommendations

**Endpoint**: `POST /api/crop-recommendation`

**Request Body** (all crops):
```json
{
  "location": "Pune"
}
```

**Request Body** (specific crop):
```json
{
  "location": "Pune",
  "crop_name": "Wheat"
}
```

**Response**:
```json
{
  "location": "Pune",
  "insolvency_in_days": 18,
  "safe_to_sow": true,
  "water_status": "safe",
  "recommendations": [
    {
      "crop_id": "wheat",
      "crop_name": "Wheat",
      "water_need": "medium",
      "recommendation": "suitable",
      "suitability_score": 85.0,
      "reasoning": "Good water availability for Wheat. Conditions are favorable with adequate irrigation."
    }
  ],
  "timestamp": "2026-02-06T08:42:18.863Z"
}
```

**Recommendation Values**:
- `suitable`: Good for cultivation
- `caution`: Marginal conditions, needs monitoring
- `not-recommended`: Poor conditions, high risk

---

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Water status
curl -X POST http://localhost:8000/api/water-status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bharat-bytes-genesis-2026-api-key-v1" \
  -d '{"location": "Delhi"}'

# Crop recommendations
curl -X POST http://localhost:8000/api/crop-recommendation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bharat-bytes-genesis-2026-api-key-v1" \
  -d '{"location": "Bangalore"}'

# Specific crop recommendation
curl -X POST http://localhost:8000/api/crop-recommendation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bharat-bytes-genesis-2026-api-key-v1" \
  -d '{"location": "Pune", "crop_name": "Wheat"}'
```

### Using JavaScript (Browser Console)

```javascript
// Test water status
fetch('http://localhost:8000/api/water-status', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'bharat-bytes-genesis-2026-api-key-v1',
  },
  body: JSON.stringify({ location: 'Mumbai' }),
})
  .then(res => res.json())
  .then(data => console.log(data));

// Test crop recommendations
fetch('http://localhost:8000/api/crop-recommendation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'bharat-bytes-genesis-2026-api-key-v1',
  },
  body: JSON.stringify({ location: 'Delhi' }),
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Supported Crops

The backend currently supports 6 crops with different water requirements:

| Crop | Water Need | Min Water (mm) | Optimal Water (mm) |
|------|------------|----------------|-------------------|
| Sugarcane | High | 700 | 1000 |
| Paddy/Rice | High | 650 | 950 |
| Wheat | Medium | 350 | 500 |
| Cotton | Medium | 400 | 600 |
| Mustard | Low | 200 | 350 |
| Chickpea | Low | 180 | 300 |

---

## Security Best Practices

1. **Never commit API keys**: Add `.env` to `.gitignore`
2. **Use environment variables**: Keep keys out of source code
3. **Rotate keys regularly**: Generate new keys periodically
4. **Use HTTPS in production**: Never send keys over HTTP
5. **Implement rate limiting**: Prevent API abuse
6. **Monitor usage**: Track API calls and detect anomalies

---

## Troubleshooting

### Backend won't start

```bash
# Make sure you're in the virtual environment
cd backend
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
cd app
python main.py
```

### CORS errors in frontend

The backend is configured to allow requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5174`

If your frontend runs on a different port, update `app/main.py` origins list.

### API key authentication fails

Make sure you're including the header correctly:
```
X-API-Key: bharat-bytes-genesis-2026-api-key-v1
```

### ML predictions show error values

The ML model requires internet access to fetch weather data. In restricted environments, it returns safe defaults:
- `insolvency_in_days: -1`
- `safe_to_sow: false`

This is handled gracefully by the backend.

---

## Next Steps

1. ✅ Backend is ready and running
2. 📝 **YOU**: Add the API key to your frontend `.env` file
3. 📝 **YOU**: Create the API service files in your frontend
4. 📝 **YOU**: Update components to use the API service
5. 🚀 Test the integration end-to-end

---

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the logs in the backend terminal
3. Test endpoints with curl to isolate issues
4. Open an issue on GitHub

---

**Generated**: 2026-02-06
**Backend Version**: 1.0.0
**API Key**: `bharat-bytes-genesis-2026-api-key-v1`
