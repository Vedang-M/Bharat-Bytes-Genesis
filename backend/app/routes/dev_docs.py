"""
Developer Documentation Routes
Public endpoints for API documentation and ML model metrics.
"""

import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/dev", tags=["Developer Documentation"])

# Path to metrics directory
ML_METRICS_DIR = Path(__file__).parent.parent.parent.parent / "ml" / "metrics"


def load_all_metrics() -> List[Dict[str, Any]]:
    """Load all model metrics from JSON files."""
    metrics = []
    
    if not ML_METRICS_DIR.exists():
        return metrics
    
    for metrics_file in ML_METRICS_DIR.glob("*_metrics.json"):
        try:
            with open(metrics_file, 'r') as f:
                metrics.append(json.load(f))
        except Exception as e:
            print(f"Error loading {metrics_file}: {e}")
    
    return metrics


def get_confidence_summary(models: List[Dict]) -> Dict[str, str]:
    """Generate confidence summary from model metrics."""
    confidence = {}
    
    for model in models:
        model_name = model.get("model_name", "unknown")
        model_type = model.get("model_type", "unknown")
        
        if model_type == "classification":
            f1 = model.get("f1_score_weighted", 0)
            accuracy = model.get("accuracy", 0)
            if f1 >= 0.85:
                conf_level = "High"
            elif f1 >= 0.70:
                conf_level = "Moderate"
            else:
                conf_level = "Low"
            confidence[model_name] = f"{conf_level} confidence (F1: {f1:.2f}, Accuracy: {accuracy:.2f})"
            
        elif model_type == "regression":
            r2 = model.get("r2_score", 0)
            mape = model.get("mape_percent")
            if r2 >= 0.85:
                conf_level = "High"
            elif r2 >= 0.70:
                conf_level = "Moderate"
            else:
                conf_level = "Low"
            if mape:
                confidence[model_name] = f"{conf_level} confidence (R²: {r2:.2f}, MAPE: {mape:.1f}%)"
            else:
                confidence[model_name] = f"{conf_level} confidence (R²: {r2:.2f})"
                
        elif model_type == "forecasting":
            mape = model.get("mape_percent", 0)
            if mape and mape <= 10:
                conf_level = "High"
            elif mape and mape <= 20:
                conf_level = "Moderate"
            else:
                conf_level = "Low"
            confidence[model_name] = f"{conf_level} confidence (MAPE: {mape:.1f}%)" if mape else "N/A"
    
    return confidence


def format_model_summary(model: Dict) -> Dict[str, Any]:
    """Format model metrics for documentation display."""
    model_type = model.get("model_type", "unknown")
    summary = {
        "name": model.get("model_name"),
        "type": model_type,
        "version": model.get("model_version", "1.0"),
        "last_evaluated": model.get("evaluation_timestamp"),
        "total_samples": model.get("total_samples"),
    }
    
    if model_type == "classification":
        summary["metrics"] = {
            "accuracy": round(model.get("accuracy", 0), 4),
            "precision": round(model.get("precision_weighted", 0), 4),
            "recall": round(model.get("recall_weighted", 0), 4),
            "f1_score": round(model.get("f1_score_weighted", 0), 4),
        }
        if "per_class_metrics" in model:
            summary["per_class_metrics"] = model["per_class_metrics"]
        if "confusion_matrix" in model:
            summary["confusion_matrix"] = model["confusion_matrix"]
            
    elif model_type == "regression":
        summary["metrics"] = {
            "r2_score": round(model.get("r2_score", 0), 4),
            "rmse": round(model.get("rmse", 0), 4),
            "mae": round(model.get("mae", 0), 4),
        }
        if model.get("mape_percent"):
            summary["metrics"]["mape_percent"] = round(model["mape_percent"], 2)
        summary["target_variable"] = model.get("target_variable")
        
    elif model_type == "forecasting":
        summary["metrics"] = {
            "rmse": round(model.get("rmse", 0), 4),
            "mae": round(model.get("mae", 0), 4),
        }
        if model.get("mape_percent"):
            summary["metrics"]["mape_percent"] = round(model["mape_percent"], 2)
        if model.get("confidence_interval_coverage_percent"):
            summary["metrics"]["ci_coverage"] = round(model["confidence_interval_coverage_percent"], 2)
    
    return summary


@router.get("/doc")
async def dev_documentation():
    """
    Developer Documentation Endpoint
    
    Returns comprehensive documentation about the Water Wallet API including:
    - System information and version
    - ML model performance metrics
    - Prediction confidence scoring
    - Data sources and update frequencies
    
    No authentication required - public developer documentation.
    """
    # Load all model metrics
    models = load_all_metrics()
    
    # Get latest evaluation date
    evaluation_dates = [m.get("evaluation_timestamp", "") for m in models if m.get("evaluation_timestamp")]
    latest_evaluation = max(evaluation_dates) if evaluation_dates else None
    
    # Format model summaries
    model_summaries = [format_model_summary(m) for m in models]
    
    # Generate confidence summary
    confidence_summary = get_confidence_summary(models)
    
    return {
        "system": {
            "name": "Water Wallet API",
            "version": "1.0.0",
            "description": "AI-Based Solvency System for Small & Marginal Farmers",
            "tagline": "Village-Level Water Accountant for Sustainable Agriculture",
            "documentation_generated": datetime.now().isoformat(),
        },
        
        "ml_models": {
            "summary": f"{len(models)} models trained and evaluated",
            "models": model_summaries,
            "model_types": {
                "classification": "XGBoost Classifier - Binary classification for crop viability and solvency",
                "regression": "XGBoost Regressor / Gradient Boosting - Continuous predictions for yield and water balance",
                "forecasting": "Meta Prophet - Time series forecasting for groundwater levels"
            }
        },
        
        "prediction_confidence": confidence_summary if confidence_summary else {
            "note": "Train models to see confidence metrics",
            "command": "python -m ml.scripts.train_models"
        },
        
        "data_sources": [
            {
                "name": "Visual Crossing Weather API",
                "description": "15-day weather forecast, precipitation, temperature, humidity, ET0 calculations",
                "update_frequency": "Hourly",
                "coverage": "Global",
                "api_type": "REST API",
                "status": "Active",
                "used_in": ["Water Balance", "Solvency Prediction", "Crop Viability"]
            },
            {
                "name": "ISRIC SoilGrids 2.0",
                "description": "Soil properties - clay/sand %, water holding capacity, soil organic carbon",
                "update_frequency": "Static (Updated annually)",
                "coverage": "Global at 250m resolution",
                "api_type": "REST API",
                "status": "Active",
                "used_in": ["Water Balance", "Yield Prediction"]
            }
        ],
        
        "api_endpoints": {
            "water_status": {
                "path": "/api/water-status",
                "method": "GET",
                "description": "Get water balance and solvency status for a location",
                "auth_required": True
            },
            "crop_check": {
                "path": "/api/crop-check/{crop_id}",
                "method": "GET",
                "description": "Check viability of a specific crop at location",
                "auth_required": False
            },
            "smart_swap": {
                "path": "/api/smart-swap/{crop_id}",
                "method": "GET",
                "description": "Get water-efficient crop alternatives",
                "auth_required": False
            },
            "ml_viability": {
                "path": "/ml/viability/analyze",
                "method": "POST",
                "description": "ML-powered crop viability analysis",
                "auth_required": False
            },
            "ml_yield": {
                "path": "/ml/yield/predict",
                "method": "POST",
                "description": "Predict crop yield using ML model",
                "auth_required": False
            },
            "ml_groundwater": {
                "path": "/ml/groundwater/forecast",
                "method": "POST",
                "description": "Prophet-based groundwater level forecast",
                "auth_required": False
            },
            "model_metrics": {
                "path": "/ml/metrics",
                "method": "GET",
                "description": "Get ML model performance metrics",
                "auth_required": False
            }
        },
        
        "crop_database": {
            "total_crops": 20,
            "categories": ["High Water (Sugarcane, Paddy)", "Medium Water (Wheat, Maize)", "Low Water (Millets, Pulses)"],
            "data_includes": ["Water requirements (mm)", "Season days", "MSP per quintal", "Average yield", "Suitable states"]
        },
        
        "technical_stack": {
            "backend": "FastAPI (Python 3.10+)",
            "ml_framework": "XGBoost, Prophet, scikit-learn",
            "database": "Firebase Firestore",
            "authentication": "Firebase Auth",
            "frontend": "React + Vite",
            "deployment": "Docker-ready"
        },
        
        "evaluation_summary": {
            "latest_evaluation": latest_evaluation,
            "total_models_evaluated": len(models),
            "training_data_sources": "Real API data from agricultural regions across India"
        }
    }


@router.get("/doc/models")
async def get_model_details():
    """
    Get detailed information about each ML model.
    Returns raw metrics data for all trained models.
    """
    models = load_all_metrics()
    
    if not models:
        return {
            "message": "No model metrics available",
            "hint": "Run training scripts to generate metrics",
            "commands": [
                "python -m ml.scripts.train_models",
                "python -m ml.scripts.train_yield_model",
                "python -m ml.scripts.train_viability_model"
            ]
        }
    
    return {
        "total_models": len(models),
        "models": models
    }


@router.get("/doc/health")
async def system_health():
    """
    System health check for developers.
    Shows status of ML models and data connections.
    """
    from pathlib import Path
    
    model_dir = Path(__file__).parent.parent.parent.parent / "ml" / "models"
    
    # Check which models exist
    model_files = {
        "water_balance": model_dir / "water_balance.joblib",
        "solvency": model_dir / "solvency.joblib",
        "insolvency_day": model_dir / "insolvency_day.joblib",
        "yield_predictor": model_dir / "yield_predictor.joblib",
        "crop_viability": model_dir / "crop_viability_xgb.joblib",
        "prophet_groundwater": model_dir / "groundwater_prophet_real_soil.joblib",
    }
    
    model_status = {}
    for name, path in model_files.items():
        model_status[name] = {
            "available": path.exists(),
            "path": str(path) if path.exists() else None,
            "size_kb": round(path.stat().st_size / 1024, 2) if path.exists() else None
        }
    
    # Check metrics availability
    metrics = load_all_metrics()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": model_status,
        "metrics_available": len(metrics),
        "models_with_metrics": [m.get("model_name") for m in metrics],
        "api_status": {
            "backend": "running",
            "ml_module": "available",
            "firebase": "configured" if Path(__file__).parent.parent.parent.parent.parent / "firebase-service-account.json" else "not_configured"
        }
    }
