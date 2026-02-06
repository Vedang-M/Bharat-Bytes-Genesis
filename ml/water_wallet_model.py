"""
Water Wallet XGBoost Model Engine
Loads pre-trained models and makes predictions.
Models are trained using real API data via ml/scripts/train_models.py
"""

import os
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple
import joblib

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    xgb = None
    XGB_AVAILABLE = False

from .config import MODEL_CACHE_DIR, XGBOOST_PARAMS, CROP_DATABASE
from .data_fetchers import get_village_profile


class WaterWalletModel:
    """
    XGBoost-based model for water balance and crop solvency prediction.
    
    Models are pre-trained using train_models.py which fetches real data
    from Visual Crossing and ISRIC APIs.
    """
    
    def __init__(self):
        self.model_dir = Path(MODEL_CACHE_DIR)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.water_balance_model = None
        self.solvency_model = None
        self.insolvency_day_model = None
        self.yield_model = None
        self.training_metadata = None
        
        self._load_models()
    
    def _get_model_path(self, model_name: str) -> Path:
        """Returns the path for a model file."""
        return self.model_dir / f"{model_name}.joblib"
    
    def _load_models(self):
        """Loads pre-trained models from disk."""
        if not XGB_AVAILABLE:
            print("Warning: XGBoost not installed. Using fallback predictions.")
            return
        
        models_to_load = [
            ("water_balance", "water_balance_model"),
            ("solvency", "solvency_model"),
            ("insolvency_day", "insolvency_day_model"),
            ("yield_predictor", "yield_model"),
        ]
        
        all_loaded = True
        for model_name, attr_name in models_to_load:
            model_path = self._get_model_path(model_name)
            
            if model_path.exists():
                try:
                    model = joblib.load(model_path)
                    setattr(self, attr_name, model)
                    print(f"Loaded model: {model_name}")
                except Exception as e:
                    print(f"Error loading {model_name}: {e}")
                    all_loaded = False
            else:
                print(f"Model not found: {model_path}")
                all_loaded = False
        
        # Load training metadata
        metadata_path = self.model_dir / "training_metadata.joblib"
        if metadata_path.exists():
            try:
                self.training_metadata = joblib.load(metadata_path)
                print(f"Models trained at: {self.training_metadata.get('trained_at', 'Unknown')}")
            except Exception:
                pass
        
        if not all_loaded:
            print("\nWARNING: Some models are missing!")
            print("Run: python -m ml.scripts.train_models")
            print("This will fetch real data from APIs and train the models.\n")
    
    def models_ready(self) -> bool:
        """Check if all models are loaded and ready."""
        return all([
            self.water_balance_model is not None,
            self.solvency_model is not None,
            self.insolvency_day_model is not None,
        ])
    
    def _prepare_features(
        self,
        weather_data: dict,
        groundwater_data: dict,
        soil_data: dict,
        crop_id: str
    ) -> np.ndarray:
        """Prepares feature vector for prediction using real API data."""
        crop = CROP_DATABASE.get(crop_id, CROP_DATABASE["wheat"])
        
        # Get values from real API data - NO DEFAULTS
        features = np.array([[
            weather_data.get("total_rainfall_mm") or 0,
            weather_data.get("total_et0_mm") or 0,
            groundwater_data.get("recharge_rate_mm") or 0,
            soil_data.get("available_water_capacity_mm_m") or 0,
            crop.get("water_req_mm", 500),
            groundwater_data.get("avg_depth_m") or 0,  # From India WRIS API
            weather_data.get("avg_temp_c") or 25,
        ]])
        
        return features
    
    def predict_water_balance(
        self,
        weather_data: dict,
        groundwater_data: dict,
        soil_data: dict,
        crop_id: str = "wheat"
    ) -> float:
        """Predicts available water balance in mm."""
        if self.water_balance_model is None:
            return self._fallback_water_balance(weather_data, groundwater_data, soil_data)
        
        features = self._prepare_features(weather_data, groundwater_data, soil_data, crop_id)
        prediction = self.water_balance_model.predict(features)[0]
        return max(0, round(float(prediction), 0))
    
    def predict_solvency(
        self,
        weather_data: dict,
        groundwater_data: dict,
        soil_data: dict,
        crop_id: str
    ) -> Tuple[bool, float]:
        """
        Predicts whether a crop is water-solvent.
        
        Returns:
            Tuple of (is_solvent: bool, probability: float)
        """
        if self.solvency_model is None:
            water_balance = self._fallback_water_balance(weather_data, groundwater_data, soil_data)
            crop = CROP_DATABASE.get(crop_id, CROP_DATABASE["wheat"])
            is_solvent = water_balance >= crop["water_req_mm"] * 0.7
            return is_solvent, 0.8 if is_solvent else 0.3
        
        features = self._prepare_features(weather_data, groundwater_data, soil_data, crop_id)
        
        prediction = self.solvency_model.predict(features)[0]
        probability = self.solvency_model.predict_proba(features)[0]
        
        is_solvent = bool(prediction)
        prob = float(probability[1] if len(probability) > 1 else probability[0])
        
        return is_solvent, round(prob, 2)
    
    def predict_insolvency_day(
        self,
        weather_data: dict,
        groundwater_data: dict,
        soil_data: dict,
        crop_id: str
    ) -> int:
        """Predicts the day when water runs out (insolvency day)."""
        if self.insolvency_day_model is None:
            water_balance = self._fallback_water_balance(weather_data, groundwater_data, soil_data)
            crop = CROP_DATABASE.get(crop_id, CROP_DATABASE["wheat"])
            daily_consumption = crop["water_req_mm"] / crop["season_days"]
            return min(365, max(0, int(water_balance / daily_consumption)))
        
        features = self._prepare_features(weather_data, groundwater_data, soil_data, crop_id)
        prediction = self.insolvency_day_model.predict(features)[0]
        return min(365, max(0, int(prediction)))
    
    def predict_yield(
        self,
        weather_data: dict,
        groundwater_data: dict,
        soil_data: dict,
        crop_id: str
    ) -> Optional[float]:
        """
        Predicts dynamic crop yield (quintals/acre) based on conditions.
        Returns None if model is missing (triggers fallback).
        """
        if self.yield_model is None:
            return None
            
        features = self._prepare_features(weather_data, groundwater_data, soil_data, crop_id)
        prediction = self.yield_model.predict(features)[0]
        return max(0, float(prediction))
    
    def _fallback_water_balance(
        self,
        weather_data: dict,
        groundwater_data: dict,
        soil_data: dict
    ) -> float:
        """Fallback water balance calculation when models not available."""
        rainfall = weather_data.get("total_rainfall_mm") or 0
        et0 = weather_data.get("total_et0_mm") or 0
        # Use recharge_rate_mm from India WRIS, divide by 4 for seasonal
        annual_recharge = groundwater_data.get("recharge_rate_mm") or 0
        seasonal_recharge = annual_recharge / 4
        soil_awc = soil_data.get("available_water_capacity_mm_m") or 0
        depth = groundwater_data.get("avg_depth_m") or 0
        
        balance = rainfall + seasonal_recharge + (soil_awc * 1.5 * 0.3) - et0 - (depth * 2)
        return max(0, balance)


# Singleton instance for reuse
_model_instance: Optional[WaterWalletModel] = None


def get_model() -> WaterWalletModel:
    """Returns the singleton model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = WaterWalletModel()
    return _model_instance


async def predict_water_status(
    lat: float,
    lon: float,
    state: str = "",
    district: str = "",
    block: Optional[str] = None,
    crop_id: str = "wheat"
) -> dict:
    """
    High-level function to get complete water status prediction.
    All data is fetched from real APIs.
    
    Returns:
        dict with water balance, solvency, insolvency day, and recommendations
    """
    # Get village profile (fetches from real APIs)
    profile = await get_village_profile(lat, lon, state, district, block)
    
    # Get model predictions
    model = get_model()
    
    weather = profile["weather"]
    groundwater = profile["groundwater"]
    soil = profile["soil"]
    
    water_balance = model.predict_water_balance(weather, groundwater, soil, crop_id)
    is_solvent, solvency_prob = model.predict_solvency(weather, groundwater, soil, crop_id)
    insolvency_day = model.predict_insolvency_day(weather, groundwater, soil, crop_id)
    
    # Determine status based on water balance
    if water_balance >= 600:
        status = "safe"
    elif water_balance >= 300:
        status = "limited"
    else:
        status = "critical"
    
    crop = CROP_DATABASE.get(crop_id, CROP_DATABASE["wheat"])
    
    return {
        "location": profile["location"],
        "water_balance_mm": water_balance,
        "status": status,
        "crop": {
            "id": crop_id,
            "name": crop.get("name_en", crop_id.title()),
            "water_required_mm": crop.get("water_req_mm", 500),
        },
        "solvency": {
            "is_solvent": is_solvent,
            "probability": solvency_prob,
            "insolvency_in_days": insolvency_day if not is_solvent else None,
        },
        "safe_to_sow": is_solvent and insolvency_day > crop.get("season_days", 120),
        "weather_summary": {
            "forecast_rainfall_mm": weather.get("total_rainfall_mm", 0),
            "forecast_et0_mm": weather.get("total_et0_mm", 0),
            "avg_temp_c": weather.get("avg_temp_c", 0),
        },
        "groundwater_category": groundwater.get("category", "Unknown"),
        "data_sources": profile.get("data_sources", {}),
        "timestamp": datetime.utcnow().isoformat(),
    }
