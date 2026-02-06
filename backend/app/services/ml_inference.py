"""
ML Inference Service
--------------------
Placeholder for future ONNX model inference.
Currently delegates to rule-based water_balance and crop_advisor services.
When models are trained and exported, load them here with onnxruntime.
"""

from .water_balance import get_water_availability
from .crop_advisor import get_crop_advice


def predict_water(district: str | None, state: str | None) -> dict:
    """Predict water availability — delegates to water_balance service."""
    return get_water_availability(district, state)


def predict_crop(crop_id: str, water_availability: int, language: str = "hi") -> dict:
    """Predict crop recommendation — delegates to crop_advisor service."""
    return get_crop_advice(crop_id, water_availability, language)
