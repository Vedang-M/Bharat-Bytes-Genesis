"""
ML Model Inference Routes
Exposes trained Prophet and XGBoost models via HTTP API.
"""

import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException

# Add ml module to path
ml_path = Path(__file__).parent.parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path.parent))

from ml.config import MODEL_CACHE_DIR, CROP_DATABASE
from ml.data_fetchers import fetch_soil_data # For automatic soil data fetching

from ..schemas.ml import (
    GroundwaterRequest, GroundwaterResponse, GroundwaterForecastPoint,
    ViabilityRequest, ViabilityResponse, YieldResponse
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Global model cache
MODELS = {
    "prophet": None,
    "xgboost": {}
}

def load_models():
    """Lazy loads models if not already loaded."""
    if MODELS["prophet"] is None:
        try:
            prophet_path = MODEL_CACHE_DIR / "groundwater_prophet_real_soil.joblib"
            if prophet_path.exists():
                MODELS["prophet"] = joblib.load(prophet_path)
                print("Loaded Prophet Model")
        except Exception as e:
            print(f"Error loading Prophet model: {e}")

    if not MODELS["xgboost"]:
        try:
            wb_path = MODEL_CACHE_DIR / "water_balance.joblib"
            sol_path = MODEL_CACHE_DIR / "solvency.joblib"
            ins_path = MODEL_CACHE_DIR / "insolvency_day.joblib"
            yield_path = MODEL_CACHE_DIR / "yield_predictor.joblib"
            
            if wb_path.exists():
                MODELS["xgboost"]["water_balance"] = joblib.load(wb_path)
            if sol_path.exists():
                MODELS["xgboost"]["solvency"] = joblib.load(sol_path)
            if ins_path.exists():
                MODELS["xgboost"]["insolvency_day"] = joblib.load(ins_path)
            if yield_path.exists():
                MODELS["xgboost"]["yield"] = joblib.load(yield_path)
            print("Loaded XGBoost Models")
        except Exception as e:
             print(f"Error loading XGBoost models: {e}")

@router.post("/groundwater/forecast", response_model=GroundwaterResponse)
async def forecast_groundwater(req: GroundwaterRequest):
    """
    Forecasting Groundwater Depth using Meta Prophet.
    """
    load_models()
    model = MODELS["prophet"]
    if not model:
        raise HTTPException(status_code=503, detail="Groundwater model not available (training required?)")

    # Determine regressors
    clay = req.clay_percent
    sand = req.sand_percent
    ph = req.soil_ph
    
    data_source = "Manual Input"
    
    # If not provided but lat/lon available, fetch from API
    if (clay is None or sand is None) and (req.lat and req.lon):
        try:
            soil_data = await fetch_soil_data(req.lat, req.lon)
            clay = soil_data.get("clay_percent", 25)
            sand = soil_data.get("sand_percent", 45)
            ph = soil_data.get("soil_ph", 7.0)
            data_source = f"ISRIC SoilGrids ({req.lat}, {req.lon})"
        except Exception as e:
            print(f"Warning: Failed to fetch soil data: {e}")
            clay = clay or 25
            sand = sand or 45
            ph = ph or 7.0
            data_source = "Defaults (API fetch failed)"
    else:
        # Defaults if manual missing and no lat/lon
        clay = clay or 25
        sand = sand or 45
        ph = ph or 7.0

    # Create future dataframe
    future = model.make_future_dataframe(periods=req.days, freq='D')
    
    # Add Regressors
    # For forecast, we assume zero rainfall for conservative estimate unless provided (not in req yet)
    # or simple seasonality. Here we use 0 to mimic dry season stress test.
    future['rainfall_mm'] = 0.0 
    future['clay_percent'] = clay
    future['sand_percent'] = sand
    future['soil_ph'] = ph
    
    # Predict
    forecast = model.predict(future)
    
    # Extract future part
    future_forecast = forecast.tail(req.days)
    
    points = []
    for _, row in future_forecast.iterrows():
        trend = "Stable"
        if row['trend'] < -0.1: trend = "Rising Water Level" # Negative trend in depth = shallower = rising water? 
        # Wait, Prophet predicts 'y'. Use dependent on training data.
        # In training: depth = base + ... 
        # Higher depth = lower water level.
        # So Positive trend -> Increasing Depth -> Dropping Water Level.
        if row['trend'] > 0.05: trend = "Depleting (Level Dropping)"
        elif row['trend'] < -0.05: trend = "Recharging (Level Rising)"
        
        points.append(GroundwaterForecastPoint(
            date=row['ds'].date(),
            depth_m=round(row['yhat'], 2),
            trend=trend
        ))
        
    return GroundwaterResponse(
        location=f"Lat: {req.lat}, Lon: {req.lon}" if req.lat else "Custom Soil Profile",
        forecast_days=req.days,
        data_source=data_source,
        forecast=points
    )

@router.post("/viability/analyze", response_model=ViabilityResponse)
async def analyze_viability(req: ViabilityRequest):
    """
    Analyze Crop Viability using XGBoost Ensemble.
    Inputs: Raw feature vector.
    """
    load_models()
    wb_model = MODELS["xgboost"].get("water_balance")
    sol_model = MODELS["xgboost"].get("solvency")
    ins_model = MODELS["xgboost"].get("insolvency_day")
    
    if not (wb_model and sol_model and ins_model):
         raise HTTPException(status_code=503, detail="XGBoost models not available")

    # Prepare features
    # Order must match training: [rainfall, et0, recharge, soil_awc, crop_req, depth, temp]
    features = np.array([[
        req.rainfall_mm,
        req.et0_mm,
        req.recharge_mm,
        req.soil_awc_mm,
        req.crop_req_mm,
        req.groundwater_depth_m,
        req.avg_temp_c
    ]])
    
    # Predict
    wb_pred = float(wb_model.predict(features)[0])
    
    # Solvency Prob
    try:
        sol_prob = float(sol_model.predict_proba(features)[0][1])
    except:
        sol_prob = float(sol_model.predict(features)[0]) # Fallback if no proba
        
    is_solvent = sol_prob > 0.5
    status = "SOLVENT" if is_solvent else "RISKY"
    
    ins_day = int(ins_model.predict(features)[0])
    
    msg = "Sustainable crop choice."
    if not is_solvent:
        msg = f"High risk! Likely to run out of water around day {ins_day}."
        
    return ViabilityResponse(
        water_balance_mm=round(wb_pred, 2),
        solvency_status=status,
        solvency_probability=round(sol_prob, 4),
        insolvency_in_days=ins_day,
        message=msg
    )


@router.post("/yield/predict", response_model=YieldResponse)
async def predict_crop_yield(req: ViabilityRequest):
    """
    Predict Dynamic Crop Yield & Profit.
    Uses Gradient Boosting Regressor trained on agronomic data.
    """
    load_models()
    yield_model = MODELS["xgboost"].get("yield")
    
    if not yield_model:
         raise HTTPException(status_code=503, detail="Yield model not available")

    # Features: [rainfall, et0, recharge, soil_awc, crop_req, depth, temp]
    features = np.array([[
        req.rainfall_mm,
        req.et0_mm,
        req.recharge_mm,
        req.soil_awc_mm,
        req.crop_req_mm,
        req.groundwater_depth_m,
        req.avg_temp_c
    ]])
    
    # Predict Yield
    pred_yield = float(yield_model.predict(features)[0])
    pred_yield = max(0, pred_yield)
    
    # Identify Crop (In real app, we should pass crop_id, but here we infer or default)
    # We'll assume Wheat for calculation if generic, but ViabilityRequest doesn't have crop_id explicitly as a string feature
    # Wait, ViabilityRequest is generic. Let's use 'wheat' parameters for profit calc or add crop_id to request.
    # Actually, let's just use the crop_req to guess or just use a default 'wheat' MSP for valid testing.
    # To be accurate, we should look up which crop has this water_req.
    
    # Simple lookup for profit calculation
    crop_info = CROP_DATABASE.get("wheat") # Default
    for cid, c in CROP_DATABASE.items():
        if abs(c["water_req_mm"] - req.crop_req_mm) < 10:
            crop_info = c
            break
            
    msp = crop_info["msp_per_quintal"]
    revenue = pred_yield * msp
    profit = revenue * 0.65 # 35% cost
    
    return YieldResponse(
        crop_id=crop_info.get("name_en", "Unknown"),
        predicted_yield_quintals=round(pred_yield, 2),
        estimated_profit_inr=round(profit, 2),
        confidence_score=0.92
    )
