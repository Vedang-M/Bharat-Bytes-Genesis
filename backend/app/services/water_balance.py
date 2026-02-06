def calculate_water_status(insolvency_in_days: int, safe_to_sow: bool) -> str:
    """
    Calculate overall water status based on insolvency prediction
    
    Args:
        insolvency_in_days (int): Days until water insolvency
        safe_to_sow (bool): Whether it's safe to sow
        
    Returns:
        str: Status - 'safe', 'limited', or 'critical'
    """
    if insolvency_in_days == 0:
        return "critical"
    elif insolvency_in_days <= 15:
        return "limited"
    else:
        return "safe"


def estimate_water_availability(insolvency_in_days: int) -> int:
    """
    Estimate water availability in mm based on insolvency days
    
    Args:
        insolvency_in_days (int): Days until water insolvency
        
    Returns:
        int: Estimated water availability in mm
    """
    # Simple estimation: map insolvency days to water availability
    # 0 days = 0mm, 15 days = 400mm, 999 days = 1000mm
    if insolvency_in_days == 0:
        return 0
    elif insolvency_in_days <= 15:
        # Linear interpolation between 0 and 400
        return int((insolvency_in_days / 15) * 400)
    elif insolvency_in_days < 999:
        # Linear interpolation between 400 and 1000
        progress = min((insolvency_in_days - 15) / (30 - 15), 1.0)
        return int(400 + (progress * 600))
    else:
        return 1000
