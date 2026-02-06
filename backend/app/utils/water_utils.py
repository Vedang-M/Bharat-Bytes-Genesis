"""
Water Wallet Utility Functions
Backend helper functions for calculations and data transformations.
"""


def normalize_water_to_percentage(water_mm: float) -> float:
    """
    Convert water availability in mm to percentage of optimal water availability.
    500mm or more = 100% (full water wallet)
    
    Args:
        water_mm: Available water in millimeters
    
    Returns:
        Percentage value between 0.0 and 100.0, rounded to 1 decimal place
    
    Examples:
        0mm → 0%
        250mm → 50%
        500mm → 100%
        1000mm → 100% (capped)
    """
    if water_mm <= 0:
        return 0.0
    
    percentage = (water_mm / 500.0) * 100.0
    
    # Cap at 100% and round to 1 decimal place
    return min(round(percentage, 1), 100.0)


def get_status_from_percentage(percentage: float) -> str:
    """
    Get water status category from percentage.
    
    Args:
        percentage: Water availability percentage (0-100)
    
    Returns:
        Status string: CRITICAL, LOW, MODERATE, or GOOD
    """
    if percentage < 20:
        return "CRITICAL"
    elif percentage < 40:
        return "LOW"
    elif percentage < 70:
        return "MODERATE"
    else:
        return "GOOD"
