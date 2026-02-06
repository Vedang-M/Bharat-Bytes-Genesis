"""
Crop Advisor Service
--------------------
Given a crop and current water availability, returns a recommendation.
Uses rule-based logic matching crop water requirements against available water.
"""

from typing import Optional

# Crop water requirements (mm per season) and suitability thresholds
CROP_PROFILES = {
    "sugarcane": {
        "water_required": 800,
        "suitable_min": 650,
        "caution_min": 450,
    },
    "paddy": {
        "water_required": 700,
        "suitable_min": 550,
        "caution_min": 350,
    },
    "wheat": {
        "water_required": 450,
        "suitable_min": 350,
        "caution_min": 250,
    },
    "mustard": {
        "water_required": 250,
        "suitable_min": 200,
        "caution_min": 130,
    },
    "chickpea": {
        "water_required": 200,
        "suitable_min": 160,
        "caution_min": 100,
    },
    "cotton": {
        "water_required": 500,
        "suitable_min": 400,
        "caution_min": 280,
    },
}

# Yield expectations
_YIELD_MAP = {
    "suitable": {
        "en": "Good yield expected with current water levels",
        "hi": "वर्तमान जल स्तर के साथ अच्छी उपज की संभावना",
    },
    "caution": {
        "en": "Moderate yield possible — adopt water-saving techniques",
        "hi": "मध्यम उपज संभव — जल-बचत तकनीक अपनाएं",
    },
    "not-recommended": {
        "en": "Low yield risk — consider an alternative crop",
        "hi": "कम उपज का जोखिम — वैकल्पिक फसल पर विचार करें",
    },
}

# Tips per recommendation level
_TIPS = {
    "suitable": {
        "en": [
            "Use drip irrigation to optimize water usage",
            "Apply mulching to retain soil moisture",
            "Schedule irrigation in early morning or evening",
        ],
        "hi": [
            "ड्रिप सिंचाई का उपयोग करें",
            "मल्चिंग से पानी बचाएं",
            "सुबह या शाम को सिंचाई करें",
        ],
    },
    "caution": {
        "en": [
            "Switch to drip or sprinkler irrigation immediately",
            "Apply organic mulch to reduce evaporation",
            "Monitor soil moisture regularly",
            "Consider rainwater harvesting",
        ],
        "hi": [
            "तुरंत ड्रिप या स्प्रिंकलर सिंचाई अपनाएं",
            "वाष्पीकरण कम करने के लिए जैविक मल्चिंग करें",
            "मिट्टी की नमी नियमित जांचें",
            "वर्षा जल संचयन पर विचार करें",
        ],
    },
    "not-recommended": {
        "en": [
            "Choose a low-water crop like mustard or chickpea",
            "Implement rainwater harvesting before next season",
            "Consult local agricultural extension office",
            "Consider crop insurance for risk protection",
        ],
        "hi": [
            "सरसों या चना जैसी कम पानी वाली फसल चुनें",
            "अगले मौसम से पहले वर्षा जल संचयन लगाएं",
            "स्थानीय कृषि विस्तार कार्यालय से परामर्श करें",
            "जोखिम सुरक्षा के लिए फसल बीमा पर विचार करें",
        ],
    },
}


def get_crop_advice(
    crop_id: str,
    water_availability: int,
    language: str = "hi",
) -> dict:
    """Return crop recommendation based on water availability."""

    crop_id = crop_id.strip().lower()
    lang = language if language in ("en", "hi") else "hi"

    profile = CROP_PROFILES.get(crop_id)
    if profile is None:
        # Unknown crop — return generic caution
        return {
            "crop_id": crop_id,
            "recommendation": "caution",
            "water_required": 0,
            "water_available": water_availability,
            "yield_prediction": _YIELD_MAP["caution"][lang],
            "tips": _TIPS["caution"][lang],
        }

    water_required = profile["water_required"]

    if water_availability >= profile["suitable_min"]:
        recommendation = "suitable"
    elif water_availability >= profile["caution_min"]:
        recommendation = "caution"
    else:
        recommendation = "not-recommended"

    return {
        "crop_id": crop_id,
        "recommendation": recommendation,
        "water_required": water_required,
        "water_available": water_availability,
        "yield_prediction": _YIELD_MAP[recommendation][lang],
        "tips": _TIPS[recommendation][lang],
    }
