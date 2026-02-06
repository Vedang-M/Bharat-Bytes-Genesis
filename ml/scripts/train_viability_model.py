"""
Crop Viability Model Training (XGBoost)
---------------------------------------
Trains a classification model to determine if a crop is 'Solvent' (Safe) or
'Insolvent' (Risky) based on soil, weather, and groundwater conditions.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
except ImportError:
    print("Error: XGBoost/Scikit-Learn not found. Install via: pip install xgboost scikit-learn")
    sys.exit(1)

from ml.config import MODEL_CACHE_DIR, CROP_DATABASE
from ml.model_metrics import ModelMetrics

def generate_viability_dataset(n_samples=5000):
    """
    Generates a synthetic dataset representing various farming scenarios.
    Features: Water Balance components, Soil, Crop Requirements.
    Target: 1 (Solvent/Safe) or 0 (Risky).
    """
    np.random.seed(42)
    
    # 1. Generate Features
    # Soil Water (mm/m)
    soil_awc = np.random.uniform(100, 200, n_samples)
    
    # Groundwater Depth (m) - Deeper is worse
    gw_depth = np.random.uniform(3, 40, n_samples)
    
    # Rainfall Forecast (mm) - Season total
    rainfall = np.random.exponential(400, n_samples) # Skewed, some high some low
    
    # Crop Water Requirement (mm)
    crop_reqs = np.random.uniform(300, 1500, n_samples)
    
    # Temperature (C) - affects ET0
    temp = np.random.normal(28, 5, n_samples)
    
    # 2. Derive Logic for Ground Truth (Target)
    # This logic mimics the physical reality we want the model to learn
    
    # Simple Water Budget Calculation
    effective_rainfall = rainfall * 0.7
    groundwater_access = np.maximum(0, (20 - gw_depth) * 50) # deeper = less access
    total_water_available = effective_rainfall + groundwater_access + (soil_awc * 0.5)
    
    # Et0 stress factor
    heat_stress = (temp - 30) * 20
    adjusted_demand = crop_reqs + np.maximum(0, heat_stress)
    
    # Viability: Available > Demand with 10% buffer
    viability_score = total_water_available / adjusted_demand
    
    # Target: 1 if score > 1.1, else 0
    y = (viability_score > 1.1).astype(int)
    
    # Create DataFrame
    X = pd.DataFrame({
        'soil_awc_mm': soil_awc,
        'gw_depth_m': gw_depth,
        'rainfall_mm': rainfall,
        'crop_req_mm': crop_reqs,
        'avg_temp_c': temp
    })
    
    return X, y

def train_viability_model():
    print("="*60)
    print("TRAINING CROP VIABILITY CLASSIFIER (XGBOOST)")
    print("="*60)
    
    # 1. Data Generation
    print("Generating synthetic training dataset (5000 samples)...")
    X, y = generate_viability_dataset()
    
    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    # 3. Model Initialization
    # Using XGBClassifier for binary classification
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        objective='binary:logistic',
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    # 4. Training
    print("\nTraining XGBoost model...")
    model.fit(X_train, y_train)
    
    # 5. Evaluation
    print("\nEvaluating model performance...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Risky', 'Solvent']))
    
    # Save metrics using ModelMetrics
    metrics = ModelMetrics("crop_viability")
    metrics.save_classification_metrics(
        y_test, y_pred,
        labels=['Risky', 'Solvent'],
        additional_info={
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": list(X.columns)
        }
    )
    
    # Feature Importance
    print("\nFeature Importance:")
    feature_imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    print(feature_imp)
    
    # 6. Saving
    model_dir = Path(MODEL_CACHE_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    save_path = model_dir / "crop_viability_xgb.joblib"
    
    joblib.dump(model, save_path)
    print(f"\nModel saved to: {save_path}")
    print("="*60 + "\n")

if __name__ == "__main__":
    train_viability_model()
