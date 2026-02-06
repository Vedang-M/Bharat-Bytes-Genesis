import secrets
import string


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure random API key
    
    Args:
        length: Length of the API key (default 32)
        
    Returns:
        str: Secure random API key
    """
    alphabet = string.ascii_letters + string.digits + '-_'
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key


def format_location_name(location: str) -> str:
    """
    Format location name for consistency
    
    Args:
        location: Raw location string
        
    Returns:
        str: Formatted location name
    """
    return location.strip().title()
