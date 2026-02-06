
import sys
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error
import xgboost as xgb

# Explicitly define model path to match default
MODEL_CACHE_DIR = Path("ml/models")

def calculate_metrics():
    print("="*60)
    print("CALCULATING MODEL ACCURACY METRICS")
    print("="*60)
    
    # Check if models exist
    if not (MODEL_CACHE_DIR / "water_balance.joblib").exists():
        print(f"Error: Models not found in {MODEL_CACHE_DIR.absolute()}")
        return

    # 1. Load Models
    print("Loading models...")
    wb_model = joblib.load(MODEL_CACHE_DIR / "water_balance.joblib")
    sol_model = joblib.load(MODEL_CACHE_DIR / "solvency.joblib")
    ins_model = joblib.load(MODEL_CACHE_DIR / "insolvency_day.joblib")

    # 2. Generate Test Data (Synthetic set N=1000)
    print("Generating 1000 test samples (Unseen Data)...")
    np.random.seed(42)
    
    X_test = []
    y_wb_true = []
    y_sol_true = []
    y_ins_true = []
    
    for _ in range(1000):
        # [rainfall, et0, recharge, soil_awc, crop_req, depth, temp]
        feat = [
            np.random.uniform(0, 1500), # rainfall
            np.random.uniform(300, 800), # et0
            np.random.uniform(50, 300),  # recharge
            np.random.uniform(100, 200), # soil
            np.random.uniform(250, 1800),# crop
            np.random.uniform(2, 40),    # depth
            np.random.uniform(15, 35)    # temp
        ]
        X_test.append(feat)
        
        # Ground Truth Logic
        rainfall, et0, recharge, soil_awc, crop_req, depth, temp = feat
        
        seasonal_recharge = recharge / 4
        soil_storage = soil_awc * 1.5 * 0.3
        et0_adjusted = et0 * (1 + (temp - 25) * 0.02)
        wb = max(0, rainfall + seasonal_recharge + soil_storage - et0_adjusted - (depth * 2))
        
        y_wb_true.append(wb)
        y_sol_true.append(1 if wb >= crop_req * 0.7 else 0)
        
        daily = crop_req / 120
        y_ins_true.append(min(365, max(0, wb / daily)))
        
    X_test = np.array(X_test)
    
    # 3. Score
    with open("results_metric.txt", "w") as f:
        f.write("METRICS:\n")
        # Water Balance
        wb_pred = wb_model.predict(X_test)
        f.write(f"1. Water Balance R2 Score: {r2_score(y_wb_true, wb_pred):.4f}\n")
        
        # Solvency
        sol_pred = sol_model.predict(X_test)
        f.write(f"2. Solvency Accuracy: {accuracy_score(y_sol_true, sol_pred):.2%}\n")
        
        # Insolvency
        ins_pred = ins_model.predict(X_test)
        f.write(f"3. Insolvency Day R2 Score: {r2_score(y_ins_true, ins_pred):.4f}\n")
    
    print("Metrics written to results_metric.txt")

if __name__ == "__main__":
    calculate_metrics()
