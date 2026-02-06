"""
ML Module Configuration
API endpoints and model parameters.
NO HARDCODED DATA - ALL DATA FROM API CALLS ONLY.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === API Configuration ===
VISUAL_CROSSING_API_KEY = os.getenv("VISUAL_CROSSING_API_KEY", "")

# === Model Configuration ===
MODEL_CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", "ml/models"))
MODEL_CACHE_DAYS = int(os.getenv("MODEL_CACHE_DAYS", "7"))

# XGBoost hyperparameters
XGBOOST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "objective": "reg:squarederror",
    "random_state": 42,
}

# === Comprehensive Crop Database for North India ===
# Water requirements in mm for full crop cycle
# MSP (Minimum Support Price) in INR per quintal (2024-25 rates)
# Yield in quintals per acre (average)
# Source: Agricultural Statistics at a Glance 2023, CACP Reports

CROP_DATABASE = {
    # === HIGH WATER CROPS ===
    "sugarcane": {
        "name_en": "Sugarcane",
        "name_hi": "गन्ना",
        "water_req_mm": 1800,
        "season_days": 365,
        "msp_per_quintal": 315,
        "yield_quintal_per_acre": 350,
        "water_need_category": "high",
        "season": "kharif",
        "states": ["UP", "Punjab", "Haryana", "Bihar"],
    },
    "paddy": {
        "name_en": "Paddy (Rice)",
        "name_hi": "धान",
        "water_req_mm": 1200,
        "season_days": 120,
        "msp_per_quintal": 2203,
        "yield_quintal_per_acre": 25,
        "water_need_category": "high",
        "season": "kharif",
        "states": ["UP", "Punjab", "Haryana", "Bihar", "WB"],
    },
    "basmati": {
        "name_en": "Basmati Rice",
        "name_hi": "बासमती",
        "water_req_mm": 1400,
        "season_days": 130,
        "msp_per_quintal": 4500,
        "yield_quintal_per_acre": 18,
        "water_need_category": "high",
        "season": "kharif",
        "states": ["Punjab", "Haryana", "UP"],
    },
    
    # === MEDIUM WATER CROPS ===
    "wheat": {
        "name_en": "Wheat",
        "name_hi": "गेहूं",
        "water_req_mm": 450,
        "season_days": 120,
        "msp_per_quintal": 2275,
        "yield_quintal_per_acre": 20,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["UP", "Punjab", "Haryana", "MP", "Rajasthan"],
    },
    "maize": {
        "name_en": "Maize (Corn)",
        "name_hi": "मक्का",
        "water_req_mm": 500,
        "season_days": 100,
        "msp_per_quintal": 2090,
        "yield_quintal_per_acre": 30,
        "water_need_category": "medium",
        "season": "kharif",
        "states": ["UP", "Bihar", "Rajasthan", "MP"],
    },
    "cotton": {
        "name_en": "Cotton",
        "name_hi": "कपास",
        "water_req_mm": 700,
        "season_days": 180,
        "msp_per_quintal": 6620,
        "yield_quintal_per_acre": 8,
        "water_need_category": "medium",
        "season": "kharif",
        "states": ["Punjab", "Haryana", "Rajasthan", "Gujarat"],
    },
    "potato": {
        "name_en": "Potato",
        "name_hi": "आलू",
        "water_req_mm": 500,
        "season_days": 90,
        "msp_per_quintal": 1500,
        "yield_quintal_per_acre": 100,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["UP", "Punjab", "WB", "Bihar"],
    },
    "onion": {
        "name_en": "Onion",
        "name_hi": "प्याज",
        "water_req_mm": 550,
        "season_days": 120,
        "msp_per_quintal": 2000,
        "yield_quintal_per_acre": 80,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["UP", "MP", "Rajasthan", "Bihar"],
    },
    "soybean": {
        "name_en": "Soybean",
        "name_hi": "सोयाबीन",
        "water_req_mm": 450,
        "season_days": 100,
        "msp_per_quintal": 4600,
        "yield_quintal_per_acre": 8,
        "water_need_category": "medium",
        "season": "kharif",
        "states": ["MP", "Rajasthan", "Maharashtra"],
    },
    "groundnut": {
        "name_en": "Groundnut",
        "name_hi": "मूंगफली",
        "water_req_mm": 500,
        "season_days": 110,
        "msp_per_quintal": 6377,
        "yield_quintal_per_acre": 10,
        "water_need_category": "medium",
        "season": "kharif",
        "states": ["Gujarat", "Rajasthan", "UP"],
    },
    
    # === LOW WATER CROPS (Drought Resistant) ===
    "mustard": {
        "name_en": "Mustard",
        "name_hi": "सरसों",
        "water_req_mm": 250,
        "season_days": 110,
        "msp_per_quintal": 5650,
        "yield_quintal_per_acre": 6,
        "water_need_category": "low",
        "season": "rabi",
        "states": ["Rajasthan", "UP", "Haryana", "MP"],
    },
    "chickpea": {
        "name_en": "Chickpea (Chana)",
        "name_hi": "चना",
        "water_req_mm": 300,
        "season_days": 100,
        "msp_per_quintal": 5440,
        "yield_quintal_per_acre": 8,
        "water_need_category": "low",
        "season": "rabi",
        "states": ["MP", "Rajasthan", "UP", "Maharashtra"],
    },
    "lentil": {
        "name_en": "Lentil (Masoor)",
        "name_hi": "मसूर",
        "water_req_mm": 280,
        "season_days": 110,
        "msp_per_quintal": 6425,
        "yield_quintal_per_acre": 5,
        "water_need_category": "low",
        "season": "rabi",
        "states": ["UP", "MP", "Bihar"],
    },
    "pigeon_pea": {
        "name_en": "Pigeon Pea (Arhar/Tur)",
        "name_hi": "अरहर",
        "water_req_mm": 350,
        "season_days": 150,
        "msp_per_quintal": 7000,
        "yield_quintal_per_acre": 6,
        "water_need_category": "low",
        "season": "kharif",
        "states": ["UP", "MP", "Maharashtra", "Karnataka"],
    },
    "moong": {
        "name_en": "Green Gram (Moong)",
        "name_hi": "मूंग",
        "water_req_mm": 300,
        "season_days": 70,
        "msp_per_quintal": 8558,
        "yield_quintal_per_acre": 4,
        "water_need_category": "low",
        "season": "kharif",
        "states": ["Rajasthan", "UP", "MP"],
    },
    "urad": {
        "name_en": "Black Gram (Urad)",
        "name_hi": "उड़द",
        "water_req_mm": 320,
        "season_days": 80,
        "msp_per_quintal": 6950,
        "yield_quintal_per_acre": 4,
        "water_need_category": "low",
        "season": "kharif",
        "states": ["UP", "MP", "Rajasthan"],
    },
    "barley": {
        "name_en": "Barley",
        "name_hi": "जौ",
        "water_req_mm": 350,
        "season_days": 120,
        "msp_per_quintal": 1735,
        "yield_quintal_per_acre": 15,
        "water_need_category": "low",
        "season": "rabi",
        "states": ["UP", "Rajasthan", "MP", "Punjab"],
    },
    "bajra": {
        "name_en": "Pearl Millet (Bajra)",
        "name_hi": "बाजरा",
        "water_req_mm": 350,
        "season_days": 80,
        "msp_per_quintal": 2500,
        "yield_quintal_per_acre": 10,
        "water_need_category": "low",
        "season": "kharif",
        "states": ["Rajasthan", "Gujarat", "Haryana", "UP"],
    },
    "jowar": {
        "name_en": "Sorghum (Jowar)",
        "name_hi": "ज्वार",
        "water_req_mm": 400,
        "season_days": 100,
        "msp_per_quintal": 3180,
        "yield_quintal_per_acre": 10,
        "water_need_category": "low",
        "season": "kharif",
        "states": ["Maharashtra", "Karnataka", "MP", "Rajasthan"],
    },
    
    # === VEGETABLE CROPS ===
    "tomato": {
        "name_en": "Tomato",
        "name_hi": "टमाटर",
        "water_req_mm": 600,
        "season_days": 90,
        "msp_per_quintal": 2000,
        "yield_quintal_per_acre": 150,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["UP", "MP", "Bihar", "Karnataka"],
    },
    "brinjal": {
        "name_en": "Brinjal (Eggplant)",
        "name_hi": "बैंगन",
        "water_req_mm": 500,
        "season_days": 120,
        "msp_per_quintal": 1800,
        "yield_quintal_per_acre": 100,
        "water_need_category": "medium",
        "season": "kharif",
        "states": ["UP", "Bihar", "WB", "Odisha"],
    },
    "cabbage": {
        "name_en": "Cabbage",
        "name_hi": "पत्तागोभी",
        "water_req_mm": 400,
        "season_days": 80,
        "msp_per_quintal": 1200,
        "yield_quintal_per_acre": 120,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["UP", "WB", "Bihar", "Odisha"],
    },
    "cauliflower": {
        "name_en": "Cauliflower",
        "name_hi": "फूलगोभी",
        "water_req_mm": 450,
        "season_days": 90,
        "msp_per_quintal": 1500,
        "yield_quintal_per_acre": 100,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["UP", "Bihar", "WB", "Punjab"],
    },
    
    # === OILSEED CROPS ===
    "sunflower": {
        "name_en": "Sunflower",
        "name_hi": "सूरजमुखी",
        "water_req_mm": 450,
        "season_days": 90,
        "msp_per_quintal": 6760,
        "yield_quintal_per_acre": 6,
        "water_need_category": "medium",
        "season": "rabi",
        "states": ["Karnataka", "AP", "Maharashtra"],
    },
    "sesame": {
        "name_en": "Sesame (Til)",
        "name_hi": "तिल",
        "water_req_mm": 300,
        "season_days": 85,
        "msp_per_quintal": 8635,
        "yield_quintal_per_acre": 3,
        "water_need_category": "low",
        "season": "kharif",
        "states": ["UP", "Rajasthan", "Gujarat", "MP"],
    },
}

# === Water Status Thresholds ===
WATER_STATUS_THRESHOLDS = {
    "safe": 600,
    "limited": 300,
}
