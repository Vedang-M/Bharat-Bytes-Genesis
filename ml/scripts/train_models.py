"""
Model Training Script for Water Wallet
Fetches real data from APIs for RURAL AGRICULTURAL REGIONS and trains XGBoost models.

Usage:
    python -m ml.scripts.train_models

This script:
1. Fetches real weather data from Visual Crossing API for rural agricultural regions
2. Fetches real soil data from ISRIC SoilGrids API
3. Generates training features based on real API data
4. Trains XGBoost models for water balance, solvency, and insolvency prediction
5. Saves models to ml/models/ directory
"""

import os
import sys
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime

import joblib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import xgboost as xgb
except ImportError:
    print("Error: XGBoost not installed. Run: pip install xgboost")
    sys.exit(1)

from ml.data_fetchers import (
    fetch_weather_forecast,
    fetch_soil_data,
    fetch_groundwater_status,
)
from ml.config import CROP_DATABASE, XGBOOST_PARAMS, MODEL_CACHE_DIR


# ========================================================================
# TRAINING LOCATIONS - RURAL AGRICULTURAL REGIONS ACROSS NORTH INDIA
# ========================================================================
# These are actual agricultural districts/blocks, NOT urban cities
# Coordinates chosen for major farming regions

TRAINING_LOCATIONS = [
    # === UTTAR PRADESH (India's largest agricultural state) ===
    {"lat": 25.4358, "lon": 81.8463, "name": "Chaka Block, Prayagraj, UP"},
    {"lat": 25.3500, "lon": 81.7500, "name": "Sahson Block, Prayagraj, UP"},
    {"lat": 26.1445, "lon": 80.2330, "name": "Fatehpur District, UP"},
    {"lat": 26.4499, "lon": 80.3319, "name": "Kanpur Dehat, UP"},
    {"lat": 27.1767, "lon": 79.0205, "name": "Shikohabad, Firozabad, UP"},
    {"lat": 28.6692, "lon": 77.4538, "name": "Hapur District, UP"},
    {"lat": 25.9255, "lon": 84.1750, "name": "Ballia District, UP"},
    {"lat": 26.7922, "lon": 81.9226, "name": "Amethi District, UP"},
    {"lat": 27.8956, "lon": 78.0826, "name": "Aligarh District, UP"},
    {"lat": 26.6800, "lon": 83.1600, "name": "Gorakhpur Rural, UP"},
    
    # === PUNJAB (Wheat & Rice Bowl) ===
    {"lat": 30.2110, "lon": 74.9455, "name": "Bathinda District, Punjab"},
    {"lat": 30.0756, "lon": 75.0901, "name": "Mansa District, Punjab"},
    {"lat": 29.7200, "lon": 76.2100, "name": "Karnal District, Haryana"},
    {"lat": 30.3753, "lon": 76.7821, "name": "Patiala Rural, Punjab"},
    {"lat": 31.1048, "lon": 75.3462, "name": "Jalandhar Rural, Punjab"},
    
    # === HARYANA (Agricultural Hub) ===
    {"lat": 29.3919, "lon": 76.9689, "name": "Panipat Rural, Haryana"},
    {"lat": 28.9845, "lon": 76.0841, "name": "Jhajjar District, Haryana"},
    {"lat": 29.1667, "lon": 75.7333, "name": "Hisar District, Haryana"},
    {"lat": 28.6000, "lon": 77.3300, "name": "Palwal District, Haryana"},
    
    # === RAJASTHAN (Mustard & Bajra Belt) ===
    {"lat": 27.5530, "lon": 75.7870, "name": "Sikar District, Rajasthan"},
    {"lat": 26.9124, "lon": 75.7873, "name": "Jaipur Rural, Rajasthan"},
    {"lat": 25.3500, "lon": 74.6350, "name": "Bhilwara District, Rajasthan"},
    {"lat": 27.2000, "lon": 77.5000, "name": "Bharatpur District, Rajasthan"},
    {"lat": 26.4500, "lon": 74.6400, "name": "Ajmer Rural, Rajasthan"},
    
    # === MADHYA PRADESH (Soybean & Wheat Region) ===
    {"lat": 23.8388, "lon": 78.7378, "name": "Sagar District, MP"},
    {"lat": 24.5854, "lon": 77.4127, "name": "Vidisha District, MP"},
    {"lat": 22.0574, "lon": 78.9382, "name": "Chhindwara District, MP"},
    {"lat": 23.1765, "lon": 75.7885, "name": "Ujjain Rural, MP"},
    {"lat": 24.2000, "lon": 76.3500, "name": "Mandsaur District, MP"},
    
    # === BIHAR (Rice & Maize Belt) ===
    {"lat": 25.6000, "lon": 85.1000, "name": "Vaishali District, Bihar"},
    {"lat": 25.8500, "lon": 86.6000, "name": "Samastipur District, Bihar"},
    {"lat": 26.1200, "lon": 84.3900, "name": "Gopalganj District, Bihar"},
    {"lat": 25.2500, "lon": 87.8600, "name": "Katihar District, Bihar"},
    
    # === GUJARAT (Cotton & Groundnut) ===
    {"lat": 22.3000, "lon": 70.8000, "name": "Rajkot Rural, Gujarat"},
    {"lat": 21.7600, "lon": 72.1500, "name": "Bhavnagar Rural, Gujarat"},
    {"lat": 23.2000, "lon": 69.6600, "name": "Kutch District, Gujarat"},
]


async def fetch_location_data(lat: float, lon: float, name: str) -> dict:
    """Fetches all data for a single location from real APIs."""
    print(f"  Fetching data for {name}...")
    
    try:
        weather = await fetch_weather_forecast(lat, lon, days=15)
        soil = await fetch_soil_data(lat, lon)
        groundwater = await fetch_groundwater_status(lat, lon)
        
        return {
            "name": name,
            "lat": lat,
            "lon": lon,
            "weather": weather,
            "soil": soil,
            "groundwater": groundwater,
            "success": True,
        }
    except Exception as e:
        print(f"    Error: {e}")
        return {
            "name": name,
            "lat": lat,
            "lon": lon,
            "success": False,
            "error": str(e),
        }


async def fetch_all_training_data() -> list:
    """Fetches data from all training locations using real APIs.
    Uses sequential calls with delay to avoid rate limiting."""
    print("\n" + "="*60)
    print("FETCHING REAL DATA FROM RURAL AGRICULTURAL REGIONS")
    print("="*60)
    
    results = []
    for loc in TRAINING_LOCATIONS:
        result = await fetch_location_data(loc["lat"], loc["lon"], loc["name"])
        results.append(result)
        # Add delay between requests to avoid rate limiting
        await asyncio.sleep(1.5)
    
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    failed = [r for r in results if isinstance(r, dict) and not r.get("success")]
    
    print(f"\nSuccessfully fetched: {len(successful)} locations")
    print(f"Failed: {len(failed)} locations")
    
    return successful


def generate_training_samples(api_data: list, samples_per_location: int = 100) -> tuple:
    """
    Generates training samples from real API data.
    
    For each location, creates multiple samples by:
    - Using actual weather, soil, groundwater data
    - Varying crop water requirements
    - Adding realistic noise
    
    Returns:
        X (features), y_water_balance, y_solvency, y_insolvency_day
    """
    print("\n" + "="*60)
    print("GENERATING TRAINING SAMPLES FROM API DATA")
    print("="*60)
    
    all_features = []
    all_water_balance = []
    all_solvency = []
    all_insolvency_days = []
    
    crops = list(CROP_DATABASE.values())
    
    for location in api_data:
        weather = location["weather"]
        soil = location["soil"]
        groundwater = location["groundwater"]
        
        # Base values from API
        base_rainfall = weather.get("total_rainfall_mm", 50)
        base_et0 = weather.get("total_et0_mm", 30)
        base_temp = weather.get("avg_temp_c", 25)
        
        clay = soil.get("clay_percent") or 25
        sand = soil.get("sand_percent") or 45
        soil_awc = soil.get("available_water_capacity_mm_m") or 150
        
        gw_recharge = groundwater.get("recharge_rate_mm", 200)
        gw_depth = groundwater.get("estimated_depth_m", 15)
        
        for _ in range(samples_per_location):
            # Add realistic variation
            rainfall = base_rainfall * np.random.uniform(0.3, 3.0)
            et0 = base_et0 * np.random.uniform(0.7, 1.5)
            temp = base_temp + np.random.uniform(-10, 10)
            
            # Pick a random crop
            crop = np.random.choice(crops)
            crop_water_req = crop["water_req_mm"]
            
            # Vary groundwater slightly
            recharge = gw_recharge * np.random.uniform(0.5, 1.5)
            depth = gw_depth + np.random.uniform(-5, 5)
            depth = max(3, min(40, depth))  # Realistic bounds
            
            # Feature vector
            features = [
                rainfall,
                et0,
                recharge,
                soil_awc,
                crop_water_req,
                depth,
                temp,
            ]
            
            # Calculate water balance (domain formula)
            seasonal_recharge = recharge / 4
            soil_storage = soil_awc * 1.5 * 0.3
            et0_adjusted = et0 * (1 + (temp - 25) * 0.02)
            depth_penalty = depth * 2
            
            water_balance = (
                rainfall +
                seasonal_recharge +
                soil_storage -
                et0_adjusted -
                depth_penalty
            )
            water_balance = max(0, water_balance)
            
            # Solvency: 1 if water >= 70% of crop need
            is_solvent = 1 if water_balance >= crop_water_req * 0.7 else 0
            
            # Insolvency day
            season_days = crop.get("season_days", 120)
            daily_consumption = crop_water_req / season_days if season_days > 0 else 5
            insolvency_day = min(365, max(0, water_balance / daily_consumption)) if daily_consumption > 0 else 365
            
            all_features.append(features)
            all_water_balance.append(water_balance)
            all_solvency.append(is_solvent)
            all_insolvency_days.append(insolvency_day)
    
    X = np.array(all_features)
    y_water = np.array(all_water_balance)
    y_solvency = np.array(all_solvency)
    y_insolvency = np.array(all_insolvency_days)
    
    print(f"Generated {len(X)} training samples from {len(api_data)} agricultural regions")
    print(f"  Water balance range: {y_water.min():.0f} - {y_water.max():.0f} mm")
    print(f"  Solvency ratio: {y_solvency.mean():.2%}")
    print(f"  Insolvency day range: {y_insolvency.min():.0f} - {y_insolvency.max():.0f} days")
    
    return X, y_water, y_solvency, y_insolvency


def train_models(X, y_water, y_solvency, y_insolvency):
    """Trains and saves XGBoost models."""
    print("\n" + "="*60)
    print("TRAINING XGBOOST MODELS")
    print("="*60)
    
    model_dir = Path(MODEL_CACHE_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Water Balance Regressor
    print("\n1. Training Water Balance Regressor...")
    water_model = xgb.XGBRegressor(**XGBOOST_PARAMS)
    water_model.fit(X, y_water)
    water_path = model_dir / "water_balance.joblib"
    joblib.dump(water_model, water_path)
    print(f"   Saved to: {water_path}")
    
    # Solvency Classifier
    print("\n2. Training Solvency Classifier...")
    solvency_model = xgb.XGBClassifier(**XGBOOST_PARAMS)
    solvency_model.fit(X, y_solvency)
    solvency_path = model_dir / "solvency.joblib"
    joblib.dump(solvency_model, solvency_path)
    print(f"   Saved to: {solvency_path}")
    
    # Insolvency Day Regressor
    print("\n3. Training Insolvency Day Predictor...")
    insolvency_model = xgb.XGBRegressor(**XGBOOST_PARAMS)
    insolvency_model.fit(X, y_insolvency)
    insolvency_path = model_dir / "insolvency_day.joblib"
    joblib.dump(insolvency_model, insolvency_path)
    print(f"   Saved to: {insolvency_path}")
    
    # Save training metadata
    metadata = {
        "trained_at": datetime.now().isoformat(),
        "num_samples": len(X),
        "num_locations": len(TRAINING_LOCATIONS),
        "location_names": [loc["name"] for loc in TRAINING_LOCATIONS],
        "feature_names": [
            "total_rainfall_mm",
            "total_et0_mm",
            "groundwater_recharge_mm",
            "soil_awc_mm_m",
            "crop_water_req_mm",
            "groundwater_depth_m",
            "temperature_avg_c",
        ],
        "data_sources": {
            "weather": "Visual Crossing Weather API",
            "soil": "ISRIC SoilGrids REST API",
            "groundwater": "Estimated from soil+weather",
        },
        "crops_count": len(CROP_DATABASE),
    }
    metadata_path = model_dir / "training_metadata.joblib"
    joblib.dump(metadata, metadata_path)
    print(f"\n   Metadata saved to: {metadata_path}")
    
    return water_model, solvency_model, insolvency_model


async def main():
    """Main training pipeline."""
    print("\n" + "="*60)
    print("WATER WALLET MODEL TRAINING")
    print("North India Agricultural Regions")
    print("="*60)
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Training locations: {len(TRAINING_LOCATIONS)} rural agricultural regions")
    print(f"Crops in database: {len(CROP_DATABASE)}")
    
    # Step 1: Fetch real data from APIs
    api_data = await fetch_all_training_data()
    
    if len(api_data) < 5:
        print("\nError: Not enough successful API responses for training.")
        print("Please check your network connection and API key.")
        sys.exit(1)
    
    # Step 2: Generate training samples
    X, y_water, y_solvency, y_insolvency = generate_training_samples(
        api_data, 
        samples_per_location=100
    )
    
    # Step 3: Train models
    models = train_models(X, y_water, y_solvency, y_insolvency)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Finished at: {datetime.now().isoformat()}")
    print(f"Models saved to: {MODEL_CACHE_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
