"""
Yield Prediction Model Training Script
--------------------------------------
Trains a Gradient Boosting Regressor (XGBoost) to predict crop yield dynamically.
Uses agronomic rules to generate training data:
Yield = Base Yield * Water Stress Factor * Soil Factor * Temperature Stress

Features: [rainfall, et0, recharge, soil_awc, crop_req, depth, temp]
Target: yield_quintal_per_acre
"""

import os
import sys
import joblib
import numpy as np
import xgboost as xgb
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.config import CROP_DATABASE, MODEL_CACHE_DIR, XGBOOST_PARAMS
from ml.model_metrics import ModelMetrics

def generate_yield_data(n_samples=5000):
    print("Generating synthetic agronomic data for yield training...")
    
    X = []
    y = []
    
    crops = list(CROP_DATABASE.values())
    
    for _ in range(n_samples):
        # 1. Random Crop
        crop = np.random.choice(crops)
        base_yield = crop["yield_quintal_per_acre"]
        crop_req = crop["water_req_mm"]
        optimal_temp = 25 # simplified
        
        # 2. Random Environmental Conditions (Realistic Ranges)
        rainfall = np.random.uniform(0, 1500)
        et0 = np.random.uniform(400, 800)
        recharge = np.random.uniform(50, 300)
        soil_awc = np.random.uniform(50, 200) # 50=sandy, 200=clay
        depth = np.random.uniform(2, 40)
        temp = np.random.uniform(10, 40)
        
        # 3. Calculate Water Balance (The "Hidden" Physics)
        seasonal_recharge = recharge / 4
        soil_storage = soil_awc * 1.5 * 0.4
        et0_adjusted = et0 * (1 + abs(temp - optimal_temp) * 0.02)
        depth_penalty = depth * 1.5
        
        available_water = rainfall + seasonal_recharge + soil_storage
        water_demand = et0_adjusted + depth_penalty
        water_balance = available_water - water_demand
        
        # 4. Calculate Yield Factors
        
        # A. Water Stress Factor (Sigmoid-like)
        # If water >= crop_req, factor = 1.0 (max yield)
        # If water < crop_req, yield drops rapidly
        water_ratio = max(0, min(1.5, available_water / crop_req))
        if water_ratio >= 1.0:
            water_factor = 1.0
        elif water_ratio >= 0.7:
            water_factor = 0.8 + (water_ratio - 0.7) * (0.2 / 0.3) # Linear drop 1.0 -> 0.8
        else:
            water_factor = max(0, water_ratio * 1.1) # Sharp drop
            
        # B. Soil Factor
        # Higher AWC (Clay/Loam) is better than Low AWC (Sand)
        soil_factor = 0.8 + (soil_awc / 200) * 0.4 # 1.0 to 1.2 max
        soil_factor = min(1.1, soil_factor)
        
        # C. Temperature Stress
        # Penalty for deviation from optimal
        temp_diff = abs(temp - optimal_temp)
        if temp_diff <= 5:
            temp_factor = 1.0
        else:
            temp_factor = max(0.5, 1.0 - (temp_diff - 5) * 0.05)
            
        # 5. Final Yield Calculation
        # Add some random noise (farming uncertainty)
        noise = np.random.normal(0, 0.05)
        
        final_yield = base_yield * water_factor * soil_factor * temp_factor * (1 + noise)
        final_yield = max(0, final_yield)
        
        # Feature Vector (Must match WaterWalletModel._prepare_features order)
        # [rainfall, et0, recharge, soil_awc, crop_req, depth, temp]
        features = [rainfall, et0, recharge, soil_awc, crop_req, depth, temp]
        
        X.append(features)
        y.append(final_yield)
        
    return np.array(X), np.array(y)

def train_yield_model():
    print("="*60)
    print("TRAINING YIELD PREDICTION MODEL (XGBOOST)")
    print("="*60)
    
    # 1. Generate Data
    X, y = generate_yield_data()
    print(f"Generated {len(X)} samples.")
    print(f"Yield Range: {y.min():.1f} to {y.max():.1f} quintals/acre")
    
    # 2. Split data for evaluation
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # 3. Train Model
    print("Training XGBoost Regressor...")
    model = xgb.XGBRegressor(**XGBOOST_PARAMS)
    model.fit(X_train, y_train)
    
    # 4. Evaluate and save metrics
    y_pred = model.predict(X_test)
    metrics = ModelMetrics("yield_predictor")
    metrics.save_regression_metrics(
        y_test, y_pred,
        target_name="yield_quintal_per_acre",
        additional_info={
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": ["rainfall", "et0", "recharge", "soil_awc", "crop_req", "depth", "temp"]
        }
    )
    
    # 5. Save Model
    model_dir = Path(MODEL_CACHE_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    save_path = model_dir / "yield_predictor.joblib"
    
    joblib.dump(model, save_path)
    print(f"Model saved to: {save_path}")
    
    # 4. Save Metadata update
    meta_path = model_dir / "training_metadata.joblib"
    if meta_path.exists():
        meta = joblib.load(meta_path)
        meta["yield_model_updated"] = datetime.now().isoformat()
        joblib.dump(meta, meta_path)
        
    print("="*60)

if __name__ == "__main__":
    train_yield_model()
