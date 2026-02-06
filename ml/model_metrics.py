"""
Model Metrics Tracking System
=============================
Tracks and stores performance metrics for all ML models in the Water Wallet system.

Models Tracked:
- Classification: Solvency (XGBoost), Crop Viability (XGBoost)
- Regression: Water Balance (XGBoost), Insolvency Day (XGBoost), Yield Predictor (XGBoost)
- Forecasting: Prophet (if implemented)

Usage:
    from ml.model_metrics import ModelMetrics
    
    # For classification models
    metrics = ModelMetrics("solvency")
    metrics.save_classification_metrics(y_true, y_pred, labels=['Risky', 'Solvent'])
    
    # For regression models
    metrics = ModelMetrics("yield_predictor")
    metrics.save_regression_metrics(y_true, y_pred)
    
    # Load metrics later
    data = ModelMetrics.load_metrics("solvency")
"""

import json
import os
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

# Optional sklearn imports - metrics calculation
try:
    from sklearn.metrics import (
        accuracy_score,
        precision_recall_fscore_support,
        confusion_matrix,
        classification_report,
        mean_squared_error,
        mean_absolute_error,
        r2_score,
        mean_absolute_percentage_error,
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Metrics calculation will be limited.")


# Metrics directory - relative to ml/ folder
METRICS_DIR = Path(__file__).parent / "metrics"


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)


class ModelMetrics:
    """
    Metrics tracking and storage for ML models.
    
    Attributes:
        model_name: Unique identifier for the model (e.g., "solvency", "yield_predictor")
        metrics: Dictionary containing calculated metrics
    """
    
    def __init__(self, model_name: str):
        """
        Initialize metrics tracker for a model.
        
        Args:
            model_name: Unique name for the model (used in filename)
        """
        self.model_name = model_name
        self.metrics: Dict[str, Any] = {}
        
        # Ensure metrics directory exists
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_metrics_path(self) -> Path:
        """Get the path to the metrics JSON file."""
        return METRICS_DIR / f"{self.model_name}_metrics.json"
    
    def save_classification_metrics(
        self,
        y_true: Union[np.ndarray, List],
        y_pred: Union[np.ndarray, List],
        labels: Optional[List[str]] = None,
        model_version: str = "1.0",
        additional_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calculate and save metrics for classification models.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            labels: Optional list of label names (e.g., ['Risky', 'Solvent'])
            model_version: Version string for the model
            additional_info: Any extra information to store
            
        Returns:
            Dictionary of calculated metrics
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for metrics calculation")
        
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        # Per-class metrics
        precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
            y_true, y_pred, average=None, zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Build metrics dictionary
        self.metrics = {
            "model_name": self.model_name,
            "model_type": "classification",
            "model_version": model_version,
            "evaluation_timestamp": datetime.now().isoformat(),
            
            # Overall metrics
            "accuracy": float(accuracy),
            "precision_weighted": float(precision),
            "recall_weighted": float(recall),
            "f1_score_weighted": float(f1),
            
            # Per-class metrics
            "per_class_metrics": {},
            
            # Confusion matrix
            "confusion_matrix": cm.tolist(),
            
            # Dataset info
            "total_samples": int(len(y_true)),
            "class_distribution": {},
        }
        
        # Add per-class metrics
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        for i, cls in enumerate(unique_classes):
            class_name = labels[i] if labels and i < len(labels) else str(cls)
            self.metrics["per_class_metrics"][class_name] = {
                "precision": float(precision_per_class[i]) if i < len(precision_per_class) else 0,
                "recall": float(recall_per_class[i]) if i < len(recall_per_class) else 0,
                "f1_score": float(f1_per_class[i]) if i < len(f1_per_class) else 0,
                "support": int(support_per_class[i]) if i < len(support_per_class) else 0,
            }
            self.metrics["class_distribution"][class_name] = int(np.sum(y_true == cls))
        
        # Add label names
        if labels:
            self.metrics["class_labels"] = labels
        
        # Add any additional info
        if additional_info:
            self.metrics["additional_info"] = additional_info
        
        # Save to file
        self._save_to_file()
        
        return self.metrics
    
    def save_regression_metrics(
        self,
        y_true: Union[np.ndarray, List],
        y_pred: Union[np.ndarray, List],
        model_version: str = "1.0",
        target_name: str = "target",
        additional_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calculate and save metrics for regression models.
        
        Args:
            y_true: Ground truth values
            y_pred: Predicted values
            model_version: Version string for the model
            target_name: Name of the target variable
            additional_info: Any extra information to store
            
        Returns:
            Dictionary of calculated metrics
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for metrics calculation")
        
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Calculate metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # MAPE (handle zeros)
        try:
            mape = mean_absolute_percentage_error(y_true, y_pred) * 100
        except:
            # Manual calculation avoiding division by zero
            mask = y_true != 0
            if mask.any():
                mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            else:
                mape = None
        
        # Build metrics dictionary
        self.metrics = {
            "model_name": self.model_name,
            "model_type": "regression",
            "model_version": model_version,
            "evaluation_timestamp": datetime.now().isoformat(),
            "target_variable": target_name,
            
            # Core metrics
            "r2_score": float(r2),
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae),
            "mape_percent": float(mape) if mape is not None else None,
            
            # Dataset info
            "total_samples": int(len(y_true)),
            "target_statistics": {
                "min": float(y_true.min()),
                "max": float(y_true.max()),
                "mean": float(y_true.mean()),
                "std": float(y_true.std()),
            },
            "prediction_statistics": {
                "min": float(y_pred.min()),
                "max": float(y_pred.max()),
                "mean": float(y_pred.mean()),
                "std": float(y_pred.std()),
            },
        }
        
        # Add any additional info
        if additional_info:
            self.metrics["additional_info"] = additional_info
        
        # Save to file
        self._save_to_file()
        
        return self.metrics
    
    def save_forecast_metrics(
        self,
        y_true: Union[np.ndarray, List],
        y_pred: Union[np.ndarray, List],
        forecast_horizon: int,
        confidence_intervals: Optional[Dict[str, List]] = None,
        model_version: str = "1.0",
        additional_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calculate and save metrics for time series forecasting models (e.g., Prophet).
        
        Args:
            y_true: Actual values
            y_pred: Forecasted values
            forecast_horizon: Number of periods forecasted
            confidence_intervals: Dict with 'lower' and 'upper' bounds
            model_version: Version string
            additional_info: Extra information
            
        Returns:
            Dictionary of calculated metrics
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for metrics calculation")
        
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Calculate metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        
        # MAPE
        try:
            mape = mean_absolute_percentage_error(y_true, y_pred) * 100
        except:
            mask = y_true != 0
            if mask.any():
                mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            else:
                mape = None
        
        # Build metrics dictionary
        self.metrics = {
            "model_name": self.model_name,
            "model_type": "forecasting",
            "model_version": model_version,
            "evaluation_timestamp": datetime.now().isoformat(),
            
            # Core metrics
            "rmse": float(rmse),
            "mae": float(mae),
            "mape_percent": float(mape) if mape is not None else None,
            
            # Forecast info
            "forecast_horizon": forecast_horizon,
            "total_samples": int(len(y_true)),
        }
        
        # Add confidence intervals if provided
        if confidence_intervals:
            self.metrics["confidence_intervals"] = {
                "lower_bound_mean": float(np.mean(confidence_intervals.get('lower', []))),
                "upper_bound_mean": float(np.mean(confidence_intervals.get('upper', []))),
                "interval_width_mean": float(
                    np.mean(np.array(confidence_intervals.get('upper', [])) - 
                           np.array(confidence_intervals.get('lower', [])))
                ) if 'upper' in confidence_intervals and 'lower' in confidence_intervals else None
            }
            
            # Calculate coverage (% of actuals within bounds)
            if 'lower' in confidence_intervals and 'upper' in confidence_intervals:
                lower = np.array(confidence_intervals['lower'])
                upper = np.array(confidence_intervals['upper'])
                coverage = np.mean((y_true >= lower) & (y_true <= upper)) * 100
                self.metrics["confidence_interval_coverage_percent"] = float(coverage)
        
        # Add any additional info
        if additional_info:
            self.metrics["additional_info"] = additional_info
        
        # Save to file
        self._save_to_file()
        
        return self.metrics
    
    def _save_to_file(self) -> None:
        """Save metrics to JSON file."""
        metrics_path = self._get_metrics_path()
        
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2, cls=NumpyEncoder)
        
        print(f"Metrics saved to: {metrics_path}")
    
    @staticmethod
    def load_metrics(model_name: str) -> Optional[Dict[str, Any]]:
        """
        Load saved metrics for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary of metrics or None if not found
        """
        metrics_path = METRICS_DIR / f"{model_name}_metrics.json"
        
        if not metrics_path.exists():
            return None
        
        with open(metrics_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_all_metrics() -> Dict[str, Dict[str, Any]]:
        """
        Load metrics for all models.
        
        Returns:
            Dictionary mapping model names to their metrics
        """
        all_metrics = {}
        
        if not METRICS_DIR.exists():
            return all_metrics
        
        for metrics_file in METRICS_DIR.glob("*_metrics.json"):
            model_name = metrics_file.stem.replace("_metrics", "")
            with open(metrics_file, 'r') as f:
                all_metrics[model_name] = json.load(f)
        
        return all_metrics
    
    @staticmethod
    def get_metrics_summary() -> Dict[str, Any]:
        """
        Get a summary of all model metrics.
        
        Returns:
            Summary dictionary with key metrics for each model
        """
        all_metrics = ModelMetrics.get_all_metrics()
        summary = {
            "generated_at": datetime.now().isoformat(),
            "models": {}
        }
        
        for model_name, metrics in all_metrics.items():
            model_type = metrics.get("model_type", "unknown")
            
            if model_type == "classification":
                summary["models"][model_name] = {
                    "type": "classification",
                    "accuracy": metrics.get("accuracy"),
                    "f1_score": metrics.get("f1_score_weighted"),
                    "last_evaluated": metrics.get("evaluation_timestamp"),
                }
            elif model_type == "regression":
                summary["models"][model_name] = {
                    "type": "regression",
                    "r2_score": metrics.get("r2_score"),
                    "rmse": metrics.get("rmse"),
                    "mae": metrics.get("mae"),
                    "last_evaluated": metrics.get("evaluation_timestamp"),
                }
            elif model_type == "forecasting":
                summary["models"][model_name] = {
                    "type": "forecasting",
                    "mape_percent": metrics.get("mape_percent"),
                    "rmse": metrics.get("rmse"),
                    "last_evaluated": metrics.get("evaluation_timestamp"),
                }
        
        return summary


def print_metrics_report():
    """Print a formatted report of all model metrics."""
    all_metrics = ModelMetrics.get_all_metrics()
    
    if not all_metrics:
        print("No metrics found. Train models first.")
        return
    
    print("\n" + "="*70)
    print("MODEL METRICS REPORT")
    print("="*70)
    
    for model_name, metrics in all_metrics.items():
        model_type = metrics.get("model_type", "unknown")
        print(f"\n{model_name.upper()}")
        print("-"*50)
        print(f"Type: {model_type}")
        print(f"Last Evaluated: {metrics.get('evaluation_timestamp', 'N/A')}")
        
        if model_type == "classification":
            print(f"Accuracy: {metrics.get('accuracy', 0):.4f}")
            print(f"Precision: {metrics.get('precision_weighted', 0):.4f}")
            print(f"Recall: {metrics.get('recall_weighted', 0):.4f}")
            print(f"F1 Score: {metrics.get('f1_score_weighted', 0):.4f}")
            print(f"Total Samples: {metrics.get('total_samples', 0)}")
            
            if 'per_class_metrics' in metrics:
                print("\nPer-Class Metrics:")
                for cls, cls_metrics in metrics['per_class_metrics'].items():
                    print(f"  {cls}: P={cls_metrics['precision']:.3f}, R={cls_metrics['recall']:.3f}, F1={cls_metrics['f1_score']:.3f}")
        
        elif model_type == "regression":
            print(f"R² Score: {metrics.get('r2_score', 0):.4f}")
            print(f"RMSE: {metrics.get('rmse', 0):.4f}")
            print(f"MAE: {metrics.get('mae', 0):.4f}")
            mape = metrics.get('mape_percent')
            if mape:
                print(f"MAPE: {mape:.2f}%")
            print(f"Total Samples: {metrics.get('total_samples', 0)}")
        
        elif model_type == "forecasting":
            print(f"RMSE: {metrics.get('rmse', 0):.4f}")
            print(f"MAE: {metrics.get('mae', 0):.4f}")
            mape = metrics.get('mape_percent')
            if mape:
                print(f"MAPE: {mape:.2f}%")
            print(f"Forecast Horizon: {metrics.get('forecast_horizon', 'N/A')}")
            coverage = metrics.get('confidence_interval_coverage_percent')
            if coverage:
                print(f"CI Coverage: {coverage:.1f}%")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print_metrics_report()
