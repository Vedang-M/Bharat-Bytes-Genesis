"""
Model Testing Script for Water Wallet
Tests that the XGBoost models are working correctly with real API data.

Usage:
    python -m ml.scripts.test_models
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml import (
    get_model,
    predict_water_status,
    check_crop_viability,
    get_smart_swap_recommendations,
    get_profit_per_drop_ranking,
    CROP_DATABASE,
)
from ml.data_fetchers import fetch_weather_forecast, fetch_soil_data


# Test locations in North India agricultural regions
TEST_LOCATIONS = [
    {"lat": 25.4358, "lon": 81.8463, "name": "Chaka, Prayagraj (UP)", "district": "Prayagraj"},
    {"lat": 30.2110, "lon": 74.9455, "name": "Bathinda (Punjab)", "district": "Bathinda"},
    {"lat": 27.5530, "lon": 75.7870, "name": "Sikar (Rajasthan)", "district": "Sikar"},
]


def print_header(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


async def test_api_connectivity():
    """Test that APIs are accessible."""
    print_header("TESTING API CONNECTIVITY")
    
    lat, lon = 25.4358, 81.8463  # Prayagraj
    
    print("\n1. Testing Visual Crossing Weather API...")
    try:
        weather = await fetch_weather_forecast(lat, lon, days=5)
        print(f"   ✅ SUCCESS - Got {weather['forecast_days']} days forecast")
        print(f"      Location: {weather.get('location', 'N/A')}")
        print(f"      Rainfall: {weather['total_rainfall_mm']} mm")
        print(f"      ET0: {weather['total_et0_mm']} mm")
        print(f"      Avg Temp: {weather['avg_temp_c']}°C")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    print("\n2. Testing ISRIC SoilGrids API...")
    try:
        soil = await fetch_soil_data(lat, lon)
        print(f"   ✅ SUCCESS - Got soil data")
        print(f"      Clay: {soil.get('clay_percent', 'N/A')}%")
        print(f"      Sand: {soil.get('sand_percent', 'N/A')}%")
        print(f"      AWC: {soil.get('available_water_capacity_mm_m', 'N/A')} mm/m")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    return True


def test_model_loading():
    """Test that models load correctly."""
    print_header("TESTING MODEL LOADING")
    
    model = get_model()
    
    print(f"\n1. Water Balance Model: ", end="")
    if model.water_balance_model is not None:
        print("✅ Loaded")
    else:
        print("❌ Not loaded")
        
    print(f"2. Solvency Model: ", end="")
    if model.solvency_model is not None:
        print("✅ Loaded")
    else:
        print("❌ Not loaded")
        
    print(f"3. Insolvency Day Model: ", end="")
    if model.insolvency_day_model is not None:
        print("✅ Loaded")
    else:
        print("❌ Not loaded")
    
    if model.training_metadata:
        print(f"\n   Training info:")
        print(f"   - Trained at: {model.training_metadata.get('trained_at', 'Unknown')}")
        print(f"   - Samples: {model.training_metadata.get('num_samples', 'Unknown')}")
        print(f"   - Locations: {model.training_metadata.get('num_locations', 'Unknown')}")
    
    return model.models_ready()


async def test_water_status_predictions():
    """Test water status predictions for different locations."""
    print_header("TESTING WATER STATUS PREDICTIONS")
    
    for loc in TEST_LOCATIONS:
        print(f"\n📍 {loc['name']}")
        print("-" * 50)
        
        try:
            result = await predict_water_status(
                lat=loc["lat"],
                lon=loc["lon"],
                district=loc["district"],
                crop_id="wheat"
            )
            
            print(f"   Water Balance: {result['water_balance_mm']} mm")
            print(f"   Status: {result['status'].upper()}")
            print(f"   Solvency: {result['solvency']['probability']:.0%}")
            print(f"   Safe to Sow: {'Yes ✅' if result['safe_to_sow'] else 'No ❌'}")
            print(f"   Weather: {result['weather_summary']['forecast_rainfall_mm']} mm rain, "
                  f"{result['weather_summary']['avg_temp_c']}°C")
            
            if not result['solvency']['is_solvent']:
                print(f"   ⚠️  Insolvency in: {result['solvency']['insolvency_in_days']} days")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_crop_viability():
    """Test crop viability for different crops."""
    print_header("TESTING CROP VIABILITY")
    
    lat, lon = 25.4358, 81.8463  # Prayagraj
    
    # Test with different crops
    test_crops = ["sugarcane", "wheat", "mustard", "chickpea", "paddy"]
    
    print(f"\n📍 Location: Prayagraj, UP")
    print("-" * 50)
    
    for crop_id in test_crops:
        try:
            result = await predict_water_status(lat, lon, crop_id=crop_id)
            crop = CROP_DATABASE.get(crop_id, {})
            
            emoji = "✅" if result['safe_to_sow'] else "❌"
            print(f"\n{emoji} {crop.get('name_en', crop_id)} ({crop.get('name_hi', '')})")
            print(f"   Water Need: {crop.get('water_req_mm', 0)} mm ({crop.get('water_need_category', '')})")
            print(f"   Solvency: {result['solvency']['probability']:.0%}")
            
            if not result['solvency']['is_solvent']:
                print(f"   ⚠️  Insolvency in: {result['solvency']['insolvency_in_days']} days")
            
        except Exception as e:
            print(f"\n❌ {crop_id}: {e}")


def test_smart_swap():
    """Test Smart Swap recommendations."""
    print_header("TESTING SMART SWAP RECOMMENDATIONS")
    
    print("\nScenario: Farmer wants to grow Sugarcane but only has 400mm water")
    print("-" * 50)
    
    recs = get_smart_swap_recommendations(
        rejected_crop_id="sugarcane",
        available_water_mm=400,
        max_recommendations=5
    )
    
    print(f"\nTop {len(recs)} Alternatives:")
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['crop_name']} ({rec['crop_name_hi']})")
        print(f"   Water Need: {rec['water_required_mm']} mm ({rec['water_need_category']})")
        print(f"   Profit/Drop: ₹{rec['profit_per_drop']:.4f}/liter")
        print(f"   Est. Profit: ₹{rec['estimated_profit_inr']:,} (2 acres)")


def test_profit_per_drop_ranking():
    """Test Profit Per Drop ranking."""
    print_header("PROFIT-PER-DROP RANKING (Top 10)")
    
    ranking = get_profit_per_drop_ranking()[:10]
    
    print(f"\n{'Rank':<5} {'Crop':<20} {'Water':<10} {'₹/Liter':<12} {'Est. Profit':<15}")
    print("-" * 65)
    
    for crop in ranking:
        print(f"{crop['rank']:<5} {crop['crop_name']:<20} {crop['water_required_mm']:<10} "
              f"₹{crop['profit_per_drop_inr']:<11.4f} ₹{crop['estimated_profit_2_acres_inr']:,}")


def test_crop_database():
    """Test that crop database has all required fields."""
    print_header("CROP DATABASE VALIDATION")
    
    required_fields = ["name_en", "name_hi", "water_req_mm", "season_days", 
                       "msp_per_quintal", "yield_quintal_per_acre", "water_need_category"]
    
    print(f"\nTotal crops in database: {len(CROP_DATABASE)}")
    print("-" * 50)
    
    missing_issues = []
    for crop_id, crop in CROP_DATABASE.items():
        for field in required_fields:
            if field not in crop:
                missing_issues.append(f"{crop_id}: missing '{field}'")
    
    if missing_issues:
        print("❌ Issues found:")
        for issue in missing_issues:
            print(f"   - {issue}")
    else:
        print("✅ All crops have required fields")
    
    # Show crop categories
    categories = {"high": [], "medium": [], "low": []}
    for crop_id, crop in CROP_DATABASE.items():
        cat = crop.get("water_need_category", "unknown")
        if cat in categories:
            categories[cat].append(crop["name_en"])
    
    print(f"\nBy water need category:")
    print(f"  🔴 High ({len(categories['high'])}): {', '.join(categories['high'][:5])}...")
    print(f"  🟡 Medium ({len(categories['medium'])}): {', '.join(categories['medium'][:5])}...")
    print(f"  🟢 Low ({len(categories['low'])}): {', '.join(categories['low'][:5])}...")


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" WATER WALLET MODEL TESTING")
    print(" Testing models, APIs, and predictions")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Test 1: Crop database
    test_crop_database()
    
    # Test 2: API connectivity
    api_ok = await test_api_connectivity()
    if not api_ok:
        print("\n⚠️  API connectivity issues - some tests may fail")
    
    # Test 3: Model loading
    models_ok = test_model_loading()
    if not models_ok:
        print("\n⚠️  Some models not loaded - run: python -m ml.scripts.train_models")
    
    # Test 4: Predictions
    await test_water_status_predictions()
    
    # Test 5: Crop viability
    await test_crop_viability()
    
    # Test 6: Smart Swap
    test_smart_swap()
    
    # Test 7: Profit ranking
    test_profit_per_drop_ranking()
    
    print("\n" + "=" * 70)
    print(" TESTING COMPLETE!")
    print("=" * 70)
    print(f"Finished at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
