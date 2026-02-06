import requests
import json

URL = "http://localhost:8000/ml/yield/predict"

payload = {
    "rainfall_mm": 100.0,
    "et0_mm": 500.0,
    "recharge_mm": 120.0,
    "soil_awc_mm": 150.0,
    "crop_req_mm": 450.0, # Approx Wheat
    "groundwater_depth_m": 10.0,
    "avg_temp_c": 25.0
}

print(f"Testing API: {URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(URL, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        print("\nSUCCESS: Yield prediction and profit estimation received.")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Connection failed: {e}")

# Write to file for reliable reading
with open("verification_output.txt", "w") as f:
    try:
        if 'response' in locals() and response.status_code == 200:
            f.write("SUCCESS\n")
            f.write(json.dumps(response.json(), indent=2))
        else:
            f.write("FAILURE\n")
            if 'response' in locals():
                f.write(f"Status: {response.status_code}\n")
                f.write(response.text)
            else:
                f.write("No response received.\n")
    except Exception as e:
        f.write(f"Error writing output: {e}")
