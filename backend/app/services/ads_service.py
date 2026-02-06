"""
Fertilizer Ads Service
Service layer for managing government-approved fertilizer advertisements in Firestore.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..firebase_config import get_firestore_client

# Collection name
COLLECTION_NAME = "fertilizer_ads"


async def get_ads(
    crop: Optional[str] = None,
    region: Optional[str] = None,
    season: Optional[str] = None,
    limit: int = 2
) -> List[Dict[str, Any]]:
    """
    Fetch fertilizer ads from Firestore with filters.
    
    Args:
        crop: Target crop to filter by (e.g., "wheat", "rice")
        region: Target region/state to filter by (e.g., "Maharashtra")
        season: Target season to filter by (e.g., "kharif", "rabi")
        limit: Maximum number of ads to return (default: 2)
    
    Returns:
        List of filtered fertilizer ad documents
    
    Note:
        Firestore has limitations with multiple array-contains queries.
        We filter by crop in the query and filter by region in memory.
    """
    db = get_firestore_client()
    
    if not db:
        return []
    
    try:
        # Start with base query - only active, government-approved ads
        query = db.collection(COLLECTION_NAME)
        query = query.where('active', '==', True)
        query = query.where('government_approved', '==', True)
        
        # Filter by season if provided
        if season:
            query = query.where('target_season', '==', season.lower())
        
        # Filter by crop using array_contains
        # Note: Firestore allows only one array-contains per query
        if crop:
            query = query.where('target_crops', 'array_contains', crop.lower())
        
        # Execute query with limit (fetch slightly more for in-memory filtering)
        fetch_limit = limit * 3 if region else limit
        results = query.limit(fetch_limit).stream()
        
        # Convert to list and apply in-memory filters
        ads = []
        for doc in results:
            ad_data = doc.to_dict()
            ad_data['id'] = doc.id  # Include document ID
            
            # In-memory filter for region (can't use two array_contains in Firestore)
            if region:
                target_regions = [r.lower() for r in ad_data.get('target_regions', [])]
                if region.lower() not in target_regions:
                    continue
            
            ads.append(ad_data)
            
            # Stop if we have enough ads
            if len(ads) >= limit:
                break
        
        return ads
        
    except Exception as e:
        print(f"Error fetching ads from Firestore: {e}")
        return []


async def get_ad_by_id(ad_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single ad by ID.
    
    Args:
        ad_id: The ad document ID
    
    Returns:
        Ad document or None if not found
    """
    db = get_firestore_client()
    
    if not db:
        return None
    
    try:
        doc = db.collection(COLLECTION_NAME).document(ad_id).get()
        if doc.exists:
            ad_data = doc.to_dict()
            ad_data['id'] = doc.id
            return ad_data
        return None
    except Exception as e:
        print(f"Error fetching ad {ad_id}: {e}")
        return None


async def create_ad(ad_data: Dict[str, Any]) -> Optional[str]:
    """
    Create a new fertilizer ad.
    
    Args:
        ad_data: Ad document data
    
    Returns:
        Created document ID or None on failure
    """
    db = get_firestore_client()
    
    if not db:
        return None
    
    try:
        # Normalize data
        ad_data['target_crops'] = [c.lower() for c in ad_data.get('target_crops', [])]
        ad_data['target_regions'] = [r.lower() for r in ad_data.get('target_regions', [])]
        ad_data['target_season'] = ad_data.get('target_season', 'kharif').lower()
        ad_data['created_at'] = datetime.utcnow()
        ad_data['active'] = ad_data.get('active', True)
        ad_data['government_approved'] = ad_data.get('government_approved', True)
        
        # If ID is provided, use it as document ID
        if 'id' in ad_data:
            doc_id = ad_data.pop('id')
            db.collection(COLLECTION_NAME).document(doc_id).set(ad_data)
            return doc_id
        else:
            doc_ref = db.collection(COLLECTION_NAME).add(ad_data)
            return doc_ref[1].id
            
    except Exception as e:
        print(f"Error creating ad: {e}")
        return None


async def seed_sample_ads() -> int:
    """
    Seed the database with sample government-approved fertilizer ads.
    
    Returns:
        Number of ads created
    """
    sample_ads = [
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
    
    created_count = 0
    for ad in sample_ads:
        result = await create_ad(ad)
        if result:
            created_count += 1
            print(f"Created ad: {result}")
    
    return created_count
