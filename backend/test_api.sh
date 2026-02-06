#!/bin/bash
# Backend API Test Script

echo "=========================================="
echo "Bharat Bytes Genesis - Backend API Tests"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"
API_KEY="bharat-bytes-genesis-2026-api-key-v1"

echo "1. Testing Health Endpoint..."
echo "   GET /health"
curl -s ${BASE_URL}/health | python -m json.tool
echo ""
echo ""

echo "2. Testing Root Endpoint..."
echo "   GET /"
curl -s ${BASE_URL}/ | python -m json.tool
echo ""
echo ""

echo "3. Testing Water Status Endpoint..."
echo "   POST /api/water-status"
echo "   Location: Delhi"
curl -s -X POST ${BASE_URL}/api/water-status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"location": "Delhi"}' | python -m json.tool
echo ""
echo ""

echo "4. Testing Crop Recommendation Endpoint (All Crops)..."
echo "   POST /api/crop-recommendation"
echo "   Location: Mumbai"
curl -s -X POST ${BASE_URL}/api/crop-recommendation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"location": "Mumbai"}' | python -m json.tool | head -50
echo "   ... (truncated for brevity)"
echo ""
echo ""

echo "5. Testing Crop Recommendation Endpoint (Specific Crop)..."
echo "   POST /api/crop-recommendation"
echo "   Location: Bangalore, Crop: Wheat"
curl -s -X POST ${BASE_URL}/api/crop-recommendation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"location": "Bangalore", "crop_name": "Wheat"}' | python -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ All tests completed!"
echo "=========================================="
echo ""
echo "Note: ML predictions may show error values (-1) if"
echo "the weather API is not accessible. This is expected"
echo "in restricted network environments."
echo ""
