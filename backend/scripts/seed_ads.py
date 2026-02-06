"""
Fertilizer Ads Seeder Script
Populates Firestore with sample government-approved fertilizer advertisements.

Usage:
    python -m backend.scripts.seed_ads
    
Or from backend directory:
    python scripts/seed_ads.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
project_root = backend_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from app.firebase_config import initialize_firebase, get_firestore_client
from datetime import datetime


SAMPLE_ADS = [
    {
        "id": "ad_001",
        "brand_name": "IFFCO",
        "product_name": "Nano Urea",
        "image_url": "https://storage.googleapis.com/jalkosh-ads/iffco_nano_urea.jpg",
        "government_approved": True,
        "approval_number": "FCO/2023/1234",
        "target_crops": ["wheat", "rice", "cotton", "sugarcane"],
        "target_regions": ["maharashtra", "punjab", "haryana", "uttar pradesh"],
        "target_season": "kharif",
        "price_per_unit": 266.50,
        "unit": "500ml bottle",
        "retailer_links": [
            "https://www.iffcobazar.in/nano-urea",
            "https://www.amazon.in/dp/B09ABCD123"
        ],
        "active": True
    },
    {
        "id": "ad_002",
        "brand_name": "IFFCO",
        "product_name": "Nano DAP",
        "image_url": "https://storage.googleapis.com/jalkosh-ads/iffco_nano_dap.jpg",
        "government_approved": True,
        "approval_number": "FCO/2023/5678",
        "target_crops": ["wheat", "rice", "maize", "soybean"],
        "target_regions": ["maharashtra", "madhya pradesh", "rajasthan", "gujarat"],
        "target_season": "rabi",
        "price_per_unit": 600.00,
        "unit": "500ml bottle",
        "retailer_links": [
            "https://www.iffcobazar.in/nano-dap",
            "https://www.flipkart.com/nano-dap"
        ],
        "active": True
    },
    {
        "id": "ad_003",
        "brand_name": "Coromandel",
        "product_name": "Gromor 14-35-14",
        "image_url": "https://storage.googleapis.com/jalkosh-ads/coromandel_gromor.jpg",
        "government_approved": True,
        "approval_number": "FCO/2024/2345",
        "target_crops": ["cotton", "sugarcane", "vegetables"],
        "target_regions": ["maharashtra", "karnataka", "andhra pradesh", "telangana"],
        "target_season": "kharif",
        "price_per_unit": 1450.00,
        "unit": "50kg bag",
        "retailer_links": [
            "https://www.coromandelgroup.com/gromor"
        ],
        "active": True
    },
    {
        "id": "ad_004",
        "brand_name": "Rashtriya Chemicals",
        "product_name": "RCF Suphala 15:15:15",
        "image_url": "https://storage.googleapis.com/jalkosh-ads/rcf_suphala.jpg",
        "government_approved": True,
        "approval_number": "FCO/2024/6789",
        "target_crops": ["rice", "wheat", "vegetables", "fruits"],
        "target_regions": ["maharashtra", "gujarat", "karnataka", "tamil nadu"],
        "target_season": "rabi",
        "price_per_unit": 1350.00,
        "unit": "50kg bag",
        "retailer_links": [
            "https://www.rcfltd.com/products/suphala"
        ],
        "active": True
    },
    {
        "id": "ad_005",
        "brand_name": "Zuari Agro",
        "product_name": "Jai Kisaan Urea",
        "image_url": "https://storage.googleapis.com/jalkosh-ads/zuari_urea.jpg",
        "government_approved": True,
        "approval_number": "FCO/2023/9012",
        "target_crops": ["wheat", "rice", "maize", "sugarcane", "cotton"],
        "target_regions": ["punjab", "haryana", "uttar pradesh", "bihar"],
        "target_season": "kharif",
        "price_per_unit": 266.50,
        "unit": "45kg bag",
        "retailer_links": [
            "https://www.zuari-agro.com/products/urea"
        ],
        "active": True
    },
    {
        "id": "ad_006",
        "brand_name": "NFL",
        "product_name": "Kisan Khad Urea",
        "image_url": "https://storage.googleapis.com/jalkosh-ads/nfl_urea.jpg",
        "government_approved": True,
        "approval_number": "FCO/2024/3456",
        "target_crops": ["rice", "wheat", "cotton"],
        "target_regions": ["punjab", "haryana", "madhya pradesh"],
        "target_season": "rabi",
        "price_per_unit": 266.50,
        "unit": "45kg bag",
        "retailer_links": [
            "https://www.nationalfertilizers.com/products"
        ],
        "active": True
    }
]


def seed_ads():
    """Seed Firestore with sample fertilizer ads."""
    print("Initializing Firebase...")
    if not initialize_firebase():
        print("ERROR: Failed to initialize Firebase.")
        print("Make sure firebase-service-account.json is in the project root.")
        return 0
    
    db = get_firestore_client()
    if not db:
        print("ERROR: Could not get Firestore client.")
        return 0
    
    print(f"\nSeeding {len(SAMPLE_ADS)} fertilizer ads to Firestore...\n")
    
    collection = db.collection("fertilizer_ads")
    created_count = 0
    
    for ad in SAMPLE_ADS:
        try:
            ad_id = ad.pop("id")
            ad["created_at"] = datetime.utcnow()
            
            # Check if ad already exists
            existing = collection.document(ad_id).get()
            if existing.exists:
                print(f"  - {ad_id}: Already exists, skipping...")
                ad["id"] = ad_id  # Restore id
                continue
            
            collection.document(ad_id).set(ad)
            print(f"  + {ad_id}: Created ({ad.get('product_name')})")
            created_count += 1
            ad["id"] = ad_id  # Restore id for logging
            
        except Exception as e:
            print(f"  ! Error creating ad: {e}")
    
    print(f"\n✓ Successfully seeded {created_count} ads!")
    return created_count


if __name__ == "__main__":
    seed_ads()
