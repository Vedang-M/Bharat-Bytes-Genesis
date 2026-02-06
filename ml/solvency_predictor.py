
import requests
import numpy as np
from sklearn.linear_model import LinearRegression

def get_water_forecast(place_name):
    """
    Fetches live weather data, converts units, calculates water balance,
    and predicts the 'Day of Insolvency' using Linear Regression.

    Args:
        place_name (str): The name of the location to fetch data for.

    Returns:
        dict: A dictionary containing location, insolvency_in_days, and safe_to_sow status.
    """
    
    # 1. Dynamic URL Construction
    api_key = "XEKDBX4Y7ZHCAZQ53NHQLHLPE"
    base_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{place_name}?unitGroup=us&key={api_key}&contentType=json"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        # Return a fallback or error state if API fails. 
        # For now, returning safe defaults to avoid crash, but in production should raise.
        return {'location': place_name, 'insolvency_in_days': -1, 'safe_to_sow': False}

    daily_data = data.get('days', [])[:15] # Ensure we take the first 15 days if more are returned

    X = []
    Y = []
    cumulative_balance = 0.0

    # 2. Unit Conversion & 3. Cumulative Calculation
    for i, day in enumerate(daily_data):
        # Extract raw values (US units: inches, Fahrenheit)
        precip_in = day.get('precip', 0.0) or 0.0 # handle None
        et0_in = day.get('et0', 0.0) or 0.0       # handle None
        # temp_f = day.get('temp', 0.0) # Temperature not used in balance, but conversion requested
        
        # Convert to Metric
        precip_mm = precip_in * 25.4
        et0_mm = et0_in * 25.4
        # temp_c = (temp_f - 32) * 5/9  # Calculated as requested, though unused in balance

        # Calculate Balance
        # Assumption: Crop Consumption is approximated by ET0 (Reference Evapotranspiration)
        # as no specific crop factor was provided. 
        # Daily Balance = Rainfall - Consumption
        daily_balance = precip_mm - et0_mm

        cumulative_balance += daily_balance

        # Prepare for Regression
        # X: Day Number (1 to 15)
        # Y: Cumulative Water Balance (mm)
        day_number = i + 1
        X.append([day_number])
        Y.append(cumulative_balance)

    # 3. Model Training (Insolvency Detector)
    if not X:
         return {'location': place_name, 'insolvency_in_days': 0, 'safe_to_sow': False}

    X_arr = np.array(X)
    Y_arr = np.array(Y)

    model = LinearRegression()
    model.fit(X_arr, Y_arr)

    # Prediction: Find day index where Y crosses zero.
    # Y = m*X + c  =>  0 = m*X + c  =>  X = -c / m
    m = model.coef_[0]
    c = model.intercept_

    insolvency_day = 0
    safe_to_sow = False

    if m == 0:
        # Slope is zero.
        if c > 0:
             # Always positive balance
             insolvency_day = 999 
             safe_to_sow = True
        else:
             # Always negative balance
             insolvency_day = 0
             safe_to_sow = False
    else:
        # Calculate zero crossing
        zero_crossing_x = -c / m
        
        # Interpret the result
        # If m > 0 (Water is increasing), check if we started negative
        if m > 0:
            if c >= 0:
                 # Started positive and increasing -> safe
                 insolvency_day = 999 
                 safe_to_sow = True
            else:
                 # Started negative but increasing -> "solvent" after day X?
                 # But "Insolvency" usually means running OUT of water. 
                 # If we are gaining water, we might recover. 
                 # However, if we view "Insolvency" as "Balance <= 0", then:
                 # It STOPS being insolvent at X.
                 # The prompt asks for "Day of Insolvency" which implies when it BECOMES insolvent.
                 # If increasing, it effectively never becomes insolvent in the future (assuming logical monotonic trend).
                 insolvency_day = 999
                 safe_to_sow = True
        else:
            # m < 0 (Water is decreasing)
            # This is the critical case. When does it hit zero?
            insolvency_day = int(np.ceil(zero_crossing_x))
            
            # Logic for "Safe to Sow"
            # If insolvency is far away (e.g., > 15 days), it might be safe.
            # If insolvency is in the past (negative day) or very soon, unsafe.
            if insolvency_day > 15:
                safe_to_sow = True
            else:
                safe_to_sow = False
            
            # Handle Past Insolvency: if crossing was before day 1.
            if insolvency_day < 1:
                insolvency_day = 0 # Already insolvent

    # 4. Output
    return {
        'location': place_name,
        'insolvency_in_days': insolvency_day,
        'safe_to_sow': safe_to_sow
    }
