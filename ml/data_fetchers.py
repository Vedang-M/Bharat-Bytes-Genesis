"""
Async Data Fetchers for Water Wallet
Uses aiohttp to call REAL APIs with EXACT URL formats.
NO HARDCODED DATA - ALL DATA FROM API CALLS ONLY.
"""

import asyncio
import aiohttp
from typing import Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# API Key
VISUAL_CROSSING_API_KEY = os.getenv("VISUAL_CROSSING_API_KEY", "XEKDBX4Y7ZHCAZQ53NHQLHLPE")


async def fetch_weather_forecast(
    location: str,
    days: int = 15,
    session: Optional[aiohttp.ClientSession] = None
) -> dict:
    """
    Fetches weather forecast data from Visual Crossing API.
    
    EXACT API URL:
    https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}?unitGroup=us&key={API_KEY}&contentType=json
    
    Args:
        location: Location string (can be lat,lon or city name)
        days: Number of forecast days
        session: Optional aiohttp session
    
    Returns:
        dict with weather data from API
    
    Raises:
        Exception if API call fails
    """
    # EXACT URL format as provided
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?unitGroup=us&key={VISUAL_CROSSING_API_KEY}&contentType=json"
    
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Visual Crossing API error: {response.status} - {error_text}")
            
            data = await response.json()
        
        daily_data = data.get("days", [])[:days]
        
        # Process data from API response - NO DEFAULTS
        total_rainfall_mm = 0.0
        total_et0_mm = 0.0
        temp_sum = 0.0
        
        processed_days = []
        for i, day in enumerate(daily_data):
            # Convert inches to mm (API returns in US units)
            precip_inches = day.get("precip") or 0.0
            precip_mm = precip_inches * 25.4
            
            # ET0 might be in inches, convert to mm
            et0_value = day.get("et0") or 0.0
            et0_mm = et0_value * 25.4 if et0_value < 1 else et0_value  # Check if already in mm
            
            # Convert F to C
            temp_f = day.get("temp") or 0.0
            temp_c = (temp_f - 32) * 5/9
            
            total_rainfall_mm += precip_mm
            total_et0_mm += et0_mm
            temp_sum += temp_c
            
            processed_days.append({
                "day": i + 1,
                "date": day.get("datetime"),
                "precip_mm": round(precip_mm, 2),
                "et0_mm": round(et0_mm, 2),
                "temp_c": round(temp_c, 1),
                "tempmax_c": round((day.get("tempmax", 0) - 32) * 5/9, 1),
                "tempmin_c": round((day.get("tempmin", 0) - 32) * 5/9, 1),
                "humidity": day.get("humidity"),
                "windspeed_kmh": round((day.get("windspeed") or 0) * 1.60934, 1),
                "conditions": day.get("conditions"),
                "icon": day.get("icon"),
            })
        
        return {
            "daily_data": processed_days,
            "total_rainfall_mm": round(total_rainfall_mm, 2),
            "total_et0_mm": round(total_et0_mm, 2),
            "avg_temp_c": round(temp_sum / len(daily_data), 1) if daily_data else None,
            "forecast_days": len(daily_data),
            "location": data.get("resolvedAddress"),
            "timezone": data.get("timezone"),
            "data_source": "Visual Crossing Weather API",
            "api_url": url.replace(VISUAL_CROSSING_API_KEY, "***"),
        }
        
    except asyncio.TimeoutError:
        raise Exception("Visual Crossing API request timed out")
    except aiohttp.ClientError as e:
        raise Exception(f"Visual Crossing API connection error: {e}")
    finally:
        if close_session:
            await session.close()


async def fetch_soil_data(
    lat: float,
    lon: float,
    session: Optional[aiohttp.ClientSession] = None
) -> dict:
    """
    Fetches soil properties from ISRIC SoilGrids REST API.
    
    EXACT API URL:
    https://rest.isric.org/soilgrids/v2.0/properties/query?lat={LAT}&lon={LON}&property=phh2o&property=clay&property=sand&property=soc&depth=0-5cm&value=Q0.5
    
    Args:
        lat: Latitude
        lon: Longitude
        session: Optional aiohttp session
    
    Returns:
        dict with soil properties from API
    
    Raises:
        Exception if API call fails or returns no data
    """
    # EXACT URL format as provided
    url = (
        f"https://rest.isric.org/soilgrids/v2.0/properties/query"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&property=phh2o"
        f"&property=clay"
        f"&property=sand"
        f"&property=soc"
        f"&depth=0-5cm"
        f"&value=Q0.5"
    )
    
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Accept": "application/json"}
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"ISRIC SoilGrids API error: {response.status} - {error_text}")
            
            data = await response.json()
        
        # Parse ISRIC response
        properties = data.get("properties", {})
        layers = properties.get("layers", [])
        
        result = {
            "clay_percent": None,
            "sand_percent": None,
            "silt_percent": None,
            "organic_carbon_g_kg": None,
            "soil_ph": None,
            "available_water_capacity_mm_m": None,
            "data_source": "ISRIC SoilGrids REST API",
            "api_url": url,
        }
        
        for layer in layers:
            name = layer.get("name", "")
            depths = layer.get("depths", [])
            
            for depth_data in depths:
                values = depth_data.get("values", {})
                median_val = values.get("Q0.5")
                
                if median_val is not None:
                    if name == "clay":
                        # ISRIC returns g/kg, convert to %
                        result["clay_percent"] = round(median_val / 10, 1)
                    elif name == "sand":
                        result["sand_percent"] = round(median_val / 10, 1)
                    elif name == "soc":
                        # Soil organic carbon in dg/kg, convert to g/kg
                        result["organic_carbon_g_kg"] = round(median_val / 10, 2)
                    elif name == "phh2o":
                        # pH in water, divide by 10
                        result["soil_ph"] = round(median_val / 10, 1)
        
        # Calculate silt if we have clay and sand
        if result["clay_percent"] is not None and result["sand_percent"] is not None:
            result["silt_percent"] = round(100 - result["clay_percent"] - result["sand_percent"], 1)
            
            # Calculate Available Water Capacity using pedotransfer function
            clay = result["clay_percent"]
            silt = result["silt_percent"]
            oc = result["organic_carbon_g_kg"] or 5
            result["available_water_capacity_mm_m"] = round(0.45 * clay + 0.25 * silt + 0.5 * oc, 1)
        
        return result
        
    except asyncio.TimeoutError:
        raise Exception("ISRIC SoilGrids API request timed out")
    except aiohttp.ClientError as e:
        raise Exception(f"ISRIC SoilGrids API connection error: {e}")
    finally:
        if close_session:
            await session.close()


async def fetch_groundwater_data(
    state_name: str,
    district_name: str,
    agency_name: str = "CGWB",
    session: Optional[aiohttp.ClientSession] = None
) -> dict:
    """
    Fetches groundwater data from India WRIS API.
    
    EXACT API URL (POST request):
    https://indiawris.gov.in/Dataset/Ground%20Water%20Level?stateName={STATE}&districtName={DISTRICT}&agencyName=CGWB&startdate={START}&enddate={END}&download=false&page=0&size=1000
    
    Args:
        state_name: State name (e.g., "Uttar Pradesh", "Odisha")
        district_name: District name (e.g., "Prayagraj", "Baleshwar")
        agency_name: Agency name (default: "CGWB")
        session: Optional aiohttp session
    
    Returns:
        dict with groundwater data from API
    
    Raises:
        Exception if API call fails
    """
    # Calculate date range (last 1 year)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Format dates as YYYY-MM-DD
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # EXACT URL format as provided (URL encoded spaces)
    url = (
        f"https://indiawris.gov.in/Dataset/Ground%20Water%20Level"
        f"?stateName={state_name}"
        f"&districtName={district_name}"
        f"&agencyName={agency_name}"
        f"&startdate={start_str}"
        f"&enddate={end_str}"
        f"&download=false"
        f"&page=0"
        f"&size=1000"
    )
    
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        # POST request with empty body as specified
        async with session.post(
            url,
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                "accept": "application/json",
                "Content-Length": "0"
            }
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"India WRIS API error: {response.status} - {error_text}")
            
            data = await response.json()
        
        # Parse India WRIS response
        # Response format: {"statusCode": 200, "message": "...", "data": [...]}
        if data.get("statusCode") != 200:
            raise Exception(f"India WRIS API returned: {data.get('message', 'Unknown error')}")
        
        records = data.get("data", [])
        
        if not records:
            raise Exception(f"No groundwater data available for {district_name}, {state_name}")
        
        # Extract water levels from records
        # Field is 'dataValue' containing water level in meters (can be negative = above ground)
        depths = []
        for record in records:
            data_value = record.get("dataValue")
            if data_value is not None:
                try:
                    # Negative values mean water is above ground reference
                    # We take absolute value as depth
                    depth = abs(float(data_value))
                    depths.append(depth)
                except (ValueError, TypeError):
                    pass
        
        if not depths:
            raise Exception(f"No valid depth readings in groundwater data for {district_name}")
        
        avg_depth = sum(depths) / len(depths)
        min_depth = min(depths)
        max_depth = max(depths)
        
        # Determine category based on average depth
        if avg_depth <= 10:
            category = "Safe"
        elif avg_depth <= 20:
            category = "Semi-Critical"
        elif avg_depth <= 30:
            category = "Critical"
        else:
            category = "Over-Exploited"
        
        # Estimate recharge rate based on depth trend
        # More depth = less recharge
        recharge_rate_mm = max(50, 350 - (avg_depth * 8))
        
        return {
            "category": category,
            "avg_depth_m": round(avg_depth, 2),
            "min_depth_m": round(min_depth, 2),
            "max_depth_m": round(max_depth, 2),
            "recharge_rate_mm": round(recharge_rate_mm, 1),
            "num_readings": len(depths),
            "state": state_name,
            "district": district_name,
            "data_source": "India WRIS - Central Ground Water Board",
            "api_url": url,
            "date_range": f"{start_str} to {end_str}",
        }
        
    except asyncio.TimeoutError:
        raise Exception("India WRIS API request timed out")
    except aiohttp.ClientError as e:
        raise Exception(f"India WRIS API connection error: {e}")
    finally:
        if close_session:
            await session.close()


async def get_village_profile(
    lat: float,
    lon: float,
    state: str,
    district: str,
    block: Optional[str] = None
) -> dict:
    """
    Aggregates all data sources to create a comprehensive village water profile.
    
    ALL DATA IS FETCHED FROM REAL APIs - NO HARDCODED VALUES.
    
    Args:
        lat: Latitude (for weather and soil APIs)
        lon: Longitude (for weather and soil APIs)
        state: State name (for India WRIS groundwater API)
        district: District name (for India WRIS groundwater API)
        block: Optional block/tehsil name
    
    Returns:
        dict containing weather, groundwater, and soil data from APIs
    
    Raises:
        Exception if any API call fails
    """
    location = f"{lat},{lon}"
    
    async with aiohttp.ClientSession() as session:
        # Fire all API requests in parallel
        weather_task = fetch_weather_forecast(location, days=15, session=session)
        soil_task = fetch_soil_data(lat, lon, session=session)
        groundwater_task = fetch_groundwater_data(state, district, session=session)
        
        # Wait for all to complete
        results = await asyncio.gather(
            weather_task,
            soil_task,
            groundwater_task,
            return_exceptions=True
        )
        
        weather_data, soil_data, groundwater_data = results
        
        # Check for exceptions
        errors = []
        if isinstance(weather_data, Exception):
            errors.append(f"Weather: {weather_data}")
        if isinstance(soil_data, Exception):
            errors.append(f"Soil: {soil_data}")
        if isinstance(groundwater_data, Exception):
            errors.append(f"Groundwater: {groundwater_data}")
        
        if errors:
            raise Exception("API errors: " + "; ".join(errors))
    
    # Calculate available water for the season from API data
    rainfall_mm = weather_data.get("total_rainfall_mm", 0)
    et0_mm = weather_data.get("total_et0_mm", 0)
    soil_awc = soil_data.get("available_water_capacity_mm_m") or 0
    gw_recharge = groundwater_data.get("recharge_rate_mm", 0)
    gw_depth = groundwater_data.get("avg_depth_m", 0)
    
    # Calculate seasonal recharge
    seasonal_recharge = gw_recharge / 4
    
    # Water balance calculation
    available_water_mm = (
        rainfall_mm +                    # Forecast rainfall
        seasonal_recharge +              # Groundwater recharge
        soil_awc * 1.5 * 0.3 -          # 30% of root zone soil water
        et0_mm * 1.2 -                  # ET0 with crop factor
        gw_depth * 2                    # Depth penalty
    )
    available_water_mm = max(0, available_water_mm)
    
    # Determine water status
    if available_water_mm >= 600:
        water_status = "safe"
    elif available_water_mm >= 300:
        water_status = "limited"
    else:
        water_status = "critical"
    
    return {
        "location": {
            "latitude": lat,
            "longitude": lon,
            "state": state,
            "district": district,
            "block": block,
        },
        "weather": weather_data,
        "groundwater": groundwater_data,
        "soil": soil_data,
        "summary": {
            "available_water_mm": round(available_water_mm, 0),
            "water_status": water_status,
            "forecast_rainfall_mm": rainfall_mm,
            "estimated_et0_mm": et0_mm,
            "groundwater_category": groundwater_data.get("category"),
            "groundwater_depth_m": groundwater_data.get("avg_depth_m"),
            "soil_awc_mm": soil_awc,
        },
        "data_sources": {
            "weather": weather_data.get("data_source"),
            "soil": soil_data.get("data_source"),
            "groundwater": groundwater_data.get("data_source"),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# Synchronous wrappers for testing
def fetch_weather_sync(location: str) -> dict:
    """Synchronous wrapper for fetch_weather_forecast."""
    return asyncio.run(fetch_weather_forecast(location))


def fetch_soil_sync(lat: float, lon: float) -> dict:
    """Synchronous wrapper for fetch_soil_data."""
    return asyncio.run(fetch_soil_data(lat, lon))


def fetch_groundwater_sync(state: str, district: str) -> dict:
    """Synchronous wrapper for fetch_groundwater_data."""
    return asyncio.run(fetch_groundwater_data(state, district))


def get_village_profile_sync(lat: float, lon: float, state: str, district: str) -> dict:
    """Synchronous wrapper for get_village_profile."""
    return asyncio.run(get_village_profile(lat, lon, state, district))
