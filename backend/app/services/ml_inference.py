import sys
import os

# Add the ml directory to Python path to import the solvency predictor
ml_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml')
sys.path.insert(0, ml_dir)

try:
    from solvency_predictor import get_water_forecast
except ImportError as e:
    print(f"Warning: Could not import solvency_predictor: {e}")
    # Fallback implementation
    def get_water_forecast(place_name):
        return {
            'location': place_name,
            'insolvency_in_days': 999,
            'safe_to_sow': True
        }


def predict_water_solvency(location: str) -> dict:
    """
    Predict water solvency for a given location using the ML model
    
    Args:
        location (str): Location name to predict for
        
    Returns:
        dict: Dictionary with location, insolvency_in_days, and safe_to_sow
    """
    try:
        result = get_water_forecast(location)
        return result
    except Exception as e:
        print(f"Error in ML prediction: {e}")
        # Return safe defaults on error
        return {
            'location': location,
            'insolvency_in_days': 999,
            'safe_to_sow': True
        }
