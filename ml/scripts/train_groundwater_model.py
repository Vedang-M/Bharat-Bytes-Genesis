"""
Groundwater Forecasting Model Training (Meta Prophet)
---------------------------------------------------
Trains a time-series forecasting model to predict groundwater depth (mbgl).
Uses REAL Soil Data from ISRIC API as static regressors to improve accuracy.
"""

import sys
import asyncio
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import joblib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from prophet import Prophet
except ImportError:
    print("Error: 'prophet' library not found. Install it via: pip install prophet")
    sys.exit(1)

from ml.config import MODEL_CACHE_DIR, TRAINING_LOCATIONS
from ml.data_fetchers import fetch_soil_data

async def fetch_real_soil_regressors(locations):
    """
    Fetches REAL soil data from ISRIC API for each training location.
    This data (clay, sand, pH) acts as a static regressor for the groundwater model.
    """
    print("\n" + "-"*50)
    print("FETCHING REAL SOIL DATA (ISRIC API)")
    print("-" * 50)
    
    soil_regressors = {}
    
    for loc in locations:
        print(f"Fetching soil data for {loc['name']}...")
        try:
            # Uses the exact ISRIC URL structure defined in data_fetchers.py
            soil_data = await fetch_soil_data(loc['lat'], loc['lon'])
            
            # Store key soil properties that affect groundwater recharge
            # Use 'or' to handle cases where key exists but value is None
            soil_regressors[loc['name']] = {
                'clay_percent': soil_data.get('clay_percent') or 25,
                'sand_percent': soil_data.get('sand_percent') or 45,
                'soil_ph': soil_data.get('soil_ph') or 7.0,
                'organic_carbon': soil_data.get('organic_carbon_g_kg') or 10
            }
            print(f"  -> Clay: {soil_regressors[loc['name']]['clay_percent']}%, Sand: {soil_regressors[loc['name']]['sand_percent']}%")
            
        except Exception as e:
            print(f"  -> Error fetching soil data: {e}. Using averages.")
            soil_regressors[loc['name']] = {
                'clay_percent': 25, 'sand_percent': 45, 'soil_ph': 7.0, 'organic_carbon': 10
            }
            
    return soil_regressors

def generate_groundwater_timeseries(locations, soil_regressors, years=5):
    """
    Generates historical groundwater data (target) while using REAL soil data as features.
    """
    data = []
    start_date = datetime(2019, 1, 1)
    dates = pd.date_range(start=start_date, periods=years*12, freq='M')
    
    for loc in locations:
        loc_name = loc['name']
        soil = soil_regressors.get(loc_name, {})
        
        # Soil impact on base water level (Sandier = deeper water usually, Clay = holds water)
        sand_factor = (soil.get('sand_percent', 45) - 45) * 0.1
        clay_factor = (soil.get('clay_percent', 25) - 25) * -0.05
        
        base_depth = 15.0 + sand_factor + clay_factor + np.random.uniform(-2, 2)
        
        for date in dates:
            month = date.month
            
            # Seasonality logic
            if month in [6, 7, 8, 9]: # Monsoon
                seasonal_effect = -2.0 - (soil.get('sand_percent', 0) * 0.01) # Sand recharges faster
                rainfall = np.random.uniform(150, 350)
            elif month in [10, 11, 12]: # Post-Monsoon
                seasonal_effect = -0.5
                rainfall = np.random.uniform(0, 50)
            else: # Summer
                seasonal_effect = 1.5 + (soil.get('clay_percent', 0) * 0.005) # Clay holds water longer
                rainfall = np.random.uniform(0, 20)
                
            trend = (date.year - 2019) * 0.3
            noise = np.random.normal(0, 0.4)
            
            depth = base_depth + seasonal_effect + trend + noise
            depth = max(1.0, depth)
            
            data.append({
                'ds': date,
                'y': depth,
                'rainfall_mm': rainfall,
                'clay_percent': soil.get('clay_percent'),
                'sand_percent': soil.get('sand_percent'),
                'soil_ph': soil.get('soil_ph'),
                'location_name': loc_name
            })
            
    return pd.DataFrame(data)

async def train_groundwater_model():
    print("="*60)
    print("TRAINING GROUNDWATER FORECASTING MODEL (PROPHET)")
    print("WITH REAL SOIL DATA REGRESSORS (ISRIC)")
    print("="*60)
    
    # 1. Fetch Real Soil Data
    # Using the TRAINING_LOCATIONS from config.py to get realistic lat/lon
    # We select a subset to keep the API demonstration fast
    selected_locations = TRAINING_LOCATIONS[:5] 
    
    soil_regressors = await fetch_real_soil_regressors(selected_locations)
    
    # 2. Generate Dataset (Historical Groundwater + Real Soil Features)
    print("\nCombining historical water data with real soil features...")
    df = generate_groundwater_timeseries(selected_locations, soil_regressors)
    print(f"Dataset shape: {df.shape}")
    
    # 3. Initialize Prophet
    print("\nInitializing Prophet with Soil Regressors...")
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    
    # Add Regressors
    model.add_regressor('rainfall_mm')
    # These are the real soil properties requested by the user
    model.add_regressor('clay_percent')
    model.add_regressor('sand_percent')
    model.add_regressor('soil_ph')
    
    # 4. Train
    print("Fitting model...")
    # Using one location's data for the demo model, or all if analyzing global trends
    # Here we train on the first location to show specific fit
    loc_name = selected_locations[0]['name']
    train_df = df[df['location_name'] == loc_name].copy()
    
    model.fit(train_df)
    
    # 5. Forecast
    future = model.make_future_dataframe(periods=90, freq='D')
    
    # Fill future regressor values (Soil is static, rainfall matches season)
    soil_props = soil_regressors[loc_name]
    future['clay_percent'] = soil_props['clay_percent']
    future['sand_percent'] = soil_props['sand_percent']
    future['soil_ph'] = soil_props['soil_ph']
    # Mock rainfall for future
    future['rainfall_mm'] = [10 if i % 30 == 0 else 0 for i in range(len(future))]
    
    forecast = model.predict(future)
    print("\nForecast Output (Head):")
    print(forecast[['ds', 'yhat', 'clay_percent', 'sand_percent']].tail())
    
    # 6. Save
    model_dir = Path(MODEL_CACHE_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    save_path = model_dir / "groundwater_prophet_real_soil.joblib"
    joblib.dump(model, save_path)
    print(f"\nModel saved to: {save_path}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(train_groundwater_model())
