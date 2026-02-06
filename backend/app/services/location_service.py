"""
Location Service
Auto-detects state and district from latitude/longitude using Nominatim API.
"""

import aiohttp
from typing import Optional, Tuple
from functools import lru_cache


# State name mappings for India WRIS API compatibility
STATE_NAME_MAPPINGS = {
    "Uttar Pradesh": "Uttar Pradesh",
    "UP": "Uttar Pradesh",
    "Punjab": "Punjab",
    "Haryana": "Haryana",
    "Bihar": "Bihar",
    "Madhya Pradesh": "Madhya Pradesh",
    "MP": "Madhya Pradesh",
    "Rajasthan": "Rajasthan",
    "Maharashtra": "Maharashtra",
    "Gujarat": "Gujarat",
    "Odisha": "Odisha",
    "Orissa": "Odisha",
    "West Bengal": "West Bengal",
    "WB": "West Bengal",
    "Karnataka": "Karnataka",
    "Tamil Nadu": "Tamil Nadu",
    "TN": "Tamil Nadu",
    "Andhra Pradesh": "Andhra Pradesh",
    "AP": "Andhra Pradesh",
    "Telangana": "Telangana",
    "Kerala": "Kerala",
    "Assam": "Assam",
    "Jharkhand": "Jharkhand",
    "Chhattisgarh": "Chhattisgarh",
    "Uttarakhand": "Uttarakhand",
    "Himachal Pradesh": "Himachal Pradesh",
    "Jammu and Kashmir": "Jammu and Kashmir",
    "Delhi": "Delhi",
    "Goa": "Goa",
    "Tripura": "Tripura",
    "Meghalaya": "Meghalaya",
    "Manipur": "Manipur",
    "Nagaland": "Nagaland",
    "Arunachal Pradesh": "Arunachal Pradesh",
    "Mizoram": "Mizoram",
    "Sikkim": "Sikkim",
}


# Default fallback locations for major Indian states
DEFAULT_LOCATIONS = {
    "Uttar Pradesh": {"district": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    "Punjab": {"district": "Ludhiana", "lat": 30.9010, "lon": 75.8573},
    "Haryana": {"district": "Karnal", "lat": 29.6857, "lon": 76.9905},
    "Bihar": {"district": "Patna", "lat": 25.5941, "lon": 85.1376},
    "Madhya Pradesh": {"district": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    "Rajasthan": {"district": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    "Maharashtra": {"district": "Pune", "lat": 18.5204, "lon": 73.8567},
    "Gujarat": {"district": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
}


async def reverse_geocode_location(lat: float, lon: float) -> dict:
    """
    Reverse geocode coordinates to get state and district.
    Uses Nominatim OpenStreetMap API.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict with state, district, city, and full address
    """
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?format=json"
        f"&lat={lat}"
        f"&lon={lon}"
        f"&zoom=10"
        f"&addressdetails=1"
        f"&accept-language=en"
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    "User-Agent": "WaterWallet-Backend/1.0",
                    "Accept-Language": "en",
                }
            ) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                address = data.get("address", {})
                
                # Extract state
                state = address.get("state", "")
                # Normalize state name
                state = STATE_NAME_MAPPINGS.get(state, state)
                
                # Extract district (try multiple fields)
                district = (
                    address.get("state_district") or
                    address.get("county") or
                    address.get("city") or
                    address.get("town") or
                    address.get("village") or
                    ""
                )
                
                # Clean up district name (remove "District" suffix)
                if district.endswith(" District"):
                    district = district[:-9]
                
                city = (
                    address.get("city") or
                    address.get("town") or
                    address.get("village") or
                    district
                )
                
                return {
                    "state": state,
                    "district": district,
                    "city": city,
                    "country": address.get("country", ""),
                    "display_name": data.get("display_name", ""),
                }
                
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return None


async def get_location_details(
    lat: float,
    lon: float,
    provided_state: Optional[str] = None,
    provided_district: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Get location details (state, district, city) with auto-detection fallback.
    
    If state/district are provided, uses those. Otherwise, auto-detects.
    If auto-detection fails, uses sensible defaults based on coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        provided_state: Optional state name provided by user
        provided_district: Optional district name provided by user
    
    Returns:
        Tuple of (state, district, city)
    """
    state = provided_state
    district = provided_district
    city = None
    
    # If state or district not provided, try reverse geocoding
    if not state or not district:
        geo_result = await reverse_geocode_location(lat, lon)
        
        if geo_result:
            if not state:
                state = geo_result.get("state", "")
            if not district:
                district = geo_result.get("district", "")
            city = geo_result.get("city", "")
    
    # If still no state, use a default based on India's geography
    if not state:
        # Simple heuristic based on lat/lon for major agricultural states
        if lat > 28 and lon > 74 and lon < 78:
            state = "Haryana"
        elif lat > 28 and lon > 73 and lon < 77:
            state = "Punjab"
        elif lat > 24 and lat < 28 and lon > 80 and lon < 85:
            state = "Uttar Pradesh"
        elif lat > 24 and lat < 28 and lon > 84 and lon < 89:
            state = "Bihar"
        elif lat > 22 and lat < 27 and lon > 74 and lon < 79:
            state = "Madhya Pradesh"
        elif lat > 24 and lat < 30 and lon > 69 and lon < 77:
            state = "Rajasthan"
        else:
            state = "Uttar Pradesh"  # Default
    
    # If no district, use state default
    if not district:
        default = DEFAULT_LOCATIONS.get(state, {"district": "Unknown"})
        district = default.get("district", "Unknown")
    
    if not city:
        city = district
    
    return state, district, city


def estimate_state_from_coordinates(lat: float, lon: float) -> str:
    """
    Estimate state name from coordinates using rough boundaries.
    This is a fallback when reverse geocoding fails.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Estimated state name
    """
    # Major Indian agricultural states with rough coordinate bounds
    state_bounds = [
        ("Punjab", 29.5, 32.5, 73.8, 76.9),
        ("Haryana", 27.6, 30.9, 74.4, 77.6),
        ("Uttar Pradesh", 23.8, 30.4, 77.0, 84.6),
        ("Bihar", 24.2, 27.5, 83.3, 88.2),
        ("Madhya Pradesh", 21.0, 26.9, 74.0, 82.8),
        ("Rajasthan", 23.0, 30.2, 69.4, 78.2),
        ("Gujarat", 20.0, 24.7, 68.1, 74.5),
        ("Maharashtra", 15.6, 22.0, 72.6, 80.9),
        ("West Bengal", 21.5, 27.2, 85.8, 89.9),
        ("Odisha", 17.8, 22.6, 81.3, 87.5),
    ]
    
    for state_name, lat_min, lat_max, lon_min, lon_max in state_bounds:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return state_name
    
    return "Uttar Pradesh"  # Default for India
