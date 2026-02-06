"""
API Endpoint Test Script
------------------------
Platform-agnostic tester for ML API endpoints.
Usage:
1. Ensure backend is running: uvicorn backend.app.main:app --reload
2. Run this script: python -m ml.scripts.test_api_endpoints
"""

import asyncio
import aiohttp
import json
import time

BASE_URL = "http://localhost:8000"

async def test_groundwater_forecast():
    url = f"{BASE_URL}/ml/groundwater/forecast"
    payload = {
        "lat": 25.4358,
        "lon": 81.8463,
        "days": 90,
        "clay_percent": 25.0,  # Optional override
        "sand_percent": 45.0   # Optional override
    }
    
    print(f"\n[1] TEST: Groundwater Forecast (Prophet)")
    print(f"    URL: {url}")
    print(f"    Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.post(url, json=payload) as response:
                duration = time.time() - start
                
                print(f"    Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"    Time: {duration:.2f}s")
                    print(f"    Response Location: {data['location']}")
                    print(f"    Data Source: {data['data_source']}")
                    
                    forecast = data.get("forecast", [])
                    print(f"    Forecast Points: {len(forecast)}")
                    if forecast:
                        print(f"    Last Point: {forecast[-1]}")
                    print("    >>> SUCCESS")
                else:
                    text = await response.text()
                    print(f"    Error: {text}")
                    print("    >>> FAILED")
                    
    except aiohttp.ClientConnectorError:
        print("    Connection Error: Is the backend server running?")
        print("    Run: uvicorn backend.app.main:app --reload")

async def test_viability_analysis():
    url = f"{BASE_URL}/ml/viability/analyze"
    payload = {
        "rainfall_mm": 50.0,
        "et0_mm": 400.0,
        "recharge_mm": 100.0,
        "soil_awc_mm": 150.0,
        "crop_req_mm": 450.0,
        "groundwater_depth_m": 12.0,
        "avg_temp_c": 22.0
    }
    
    print(f"\n[2] TEST: Crop Viability (XGBoost)")
    print(f"    URL: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                print(f"    Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"    Response:")
                    print(json.dumps(data, indent=6))
                    print("    >>> SUCCESS")
                else:
                    text = await response.text()
                    print(f"    Error: {text}")
                    print("    >>> FAILED")
                    
    except Exception as e:
        print(f"    Error: {e}")

async def main():
    print("="*50)
    print("STARTING API TESTS")
    print("="*50)
    
    # Simple retry logic to check connectivity
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/health") as resp:
                if resp.status == 200:
                    print("Backend is ONLINE.")
                else:
                    print(f"Backend returned {resp.status} on /api/health")
        except:
             print("Backend is OFFLINE. Please start it first!")
             # We continue anyway to show the error in specific tests
    
    await test_groundwater_forecast()
    await test_viability_analysis()
    print("\nTests Completed.")

if __name__ == "__main__":
    asyncio.run(main())
