# 🚀 Quick Reference Card - Backend API

## Your API Key
```
bharat-bytes-genesis-2026-api-key-v1
```

## Start Backend
```bash
cd backend && source venv/bin/activate && cd app && python main.py
```

## Base URL
```
http://localhost:8000
```

## Quick Test
```bash
curl http://localhost:8000/health
```

## Frontend .env
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=bharat-bytes-genesis-2026-api-key-v1
```

## API Call Example
```javascript
fetch('http://localhost:8000/api/water-status', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'bharat-bytes-genesis-2026-api-key-v1',
  },
  body: JSON.stringify({ location: 'Mumbai' }),
});
```

## Documentation
- **Setup**: `backend/README.md`
- **Integration**: `API_INTEGRATION_GUIDE.md`
- **Summary**: `BACKEND_COMPLETE_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs

## Supported Endpoints
- `GET /health` - Health check
- `POST /api/water-status` - Water prediction
- `POST /api/crop-recommendation` - Crop recommendations

## Generate New Key
```bash
cd backend && python generate_api_key.py
```
