# Bharat Bytes Genesis - Backend API

FastAPI-based backend for water availability prediction and crop recommendation system.

## Features

- 🌊 Water solvency prediction using ML models
- 🌾 Intelligent crop recommendation system
- 🔐 API key authentication
- 📊 Real-time weather data integration
- 🚀 Fast and scalable FastAPI framework

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` and set your API key (see API Key Generation section below)

### Running the Server

Start the development server:
```bash
cd app
python main.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- Main API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Health Check
```
GET /health
```
Returns API health status.

### Water Status
```
POST /api/water-status
Content-Type: application/json

{
  "location": "Mumbai"
}
```
Returns water availability and solvency prediction for the specified location.

**Response:**
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

### Crop Recommendations
```
POST /api/crop-recommendation
Content-Type: application/json

{
  "location": "Pune",
  "crop_name": "Wheat"  // optional
}
```
Returns crop recommendations based on water availability.

**Response:**
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
      "reasoning": "Good water availability for Wheat. Conditions are favorable..."
    }
  ],
  "timestamp": "2026-02-06T08:42:18.863Z"
}
```

## API Key Generation

The backend uses API key authentication for secure access. Here's your API key:

```
API_KEY=bharat-bytes-genesis-2026-api-key-v1
```

### Using the API Key

Include the API key in your requests using the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/api/water-status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bharat-bytes-genesis-2026-api-key-v1" \
  -d '{"location": "Mumbai"}'
```

### Frontend Integration

Add the API key to your frontend environment variables:

**For Vite (React):**
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=bharat-bytes-genesis-2026-api-key-v1
```

Then use it in your frontend code:
```javascript
const API_URL = import.meta.env.VITE_API_URL;
const API_KEY = import.meta.env.VITE_API_KEY;

fetch(`${API_URL}/api/water-status`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
  body: JSON.stringify({ location: 'Mumbai' }),
});
```

### Generating a New API Key

If you need to generate a new API key:

```bash
python -c "from app.utils.helpers import generate_api_key; print(generate_api_key())"
```

Or use Python interactively:
```python
from app.utils.helpers import generate_api_key
new_key = generate_api_key()
print(f"New API Key: {new_key}")
```

Update the key in your `.env` file and distribute it to authorized users.

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── routes/
│   │   ├── health.py          # Health check endpoint
│   │   └── water_status.py    # Water and crop endpoints
│   ├── schemas/
│   │   ├── request.py         # Request models
│   │   └── response.py        # Response models
│   ├── services/
│   │   ├── ml_inference.py    # ML model integration
│   │   ├── water_balance.py   # Water calculations
│   │   └── crop_advisor.py    # Crop recommendations
│   └── utils/
│       └── helpers.py         # Utility functions
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── Dockerfile                # Docker configuration
└── README.md                 # This file
```

## ML Model Integration

The backend integrates the ML-based water solvency predictor from the `ml/` directory. It:

1. Fetches live weather data from Visual Crossing API
2. Converts units and calculates water balance
3. Uses Linear Regression to predict insolvency timeline
4. Provides safety recommendations for sowing

## Supported Crops

The system provides recommendations for:
- **Sugarcane** (High water need)
- **Paddy/Rice** (High water need)
- **Wheat** (Medium water need)
- **Cotton** (Medium water need)
- **Mustard** (Low water need)
- **Chickpea** (Low water need)

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5174`
- All origins (for development)

Update the CORS configuration in `app/main.py` for production deployment.

## Docker Deployment

Build the Docker image:
```bash
docker build -t bharat-bytes-backend .
```

Run the container:
```bash
docker run -p 8000:8000 --env-file .env bharat-bytes-backend
```

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include:
```json
{
  "error": "Error message",
  "status": "error"
}
```

## Development

### Testing Endpoints

Use the interactive API documentation at `/docs` or test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Water status
curl -X POST http://localhost:8000/api/water-status \
  -H "Content-Type: application/json" \
  -d '{"location": "Delhi"}'

# Crop recommendations
curl -X POST http://localhost:8000/api/crop-recommendation \
  -H "Content-Type: application/json" \
  -d '{"location": "Bangalore"}'
```

## Production Considerations

1. **Security**:
   - Change the default API key
   - Use HTTPS in production
   - Implement rate limiting
   - Add request logging

2. **Performance**:
   - Enable caching for weather data
   - Use a production ASGI server (Gunicorn + Uvicorn)
   - Consider adding a reverse proxy (Nginx)

3. **Monitoring**:
   - Add logging and monitoring
   - Track API usage metrics
   - Set up health check alerts

## License

See the LICENSE file in the root directory.

## Support

For issues and questions, please open an issue on the GitHub repository.
