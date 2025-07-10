#!/usr/bin/env python3
"""
Test Fixed Estes Tracking with Angular Material Form Handling
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.apple_silicon_estes_client import AppleSiliconEstesClient, track_estes_apple_silicon

async def test_fixed_estes_tracking():
    """Test the fixed Estes tracking with proper Angular Material form handling"""
    print("🧪 TESTING FIXED ESTES TRACKING")
    print("=" * 60)
    
    test_pro = "0628143046"
    print(f"🎯 Test PRO Number: {test_pro}")
    print("=" * 60)
    
    # Test with Apple Silicon client
    client = AppleSiliconEstesClient()
    
    print("\n🔧 Testing Playwright Method (Fixed for Angular Material)")
    print("-" * 50)
    try:
        result = await client.track_with_playwright(test_pro)
        print(f"📊 Result: {result}")
        
        if result.get('success'):
            print("✅ Playwright method succeeded!")
            print(f"   Status: {result.get('status', 'Unknown')}")
            print(f"   Details: {result.get('details', [])}")
        else:
            print(f"❌ Playwright method failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Playwright method error: {e}")
    
    print("\n🔧 Testing Selenium Method (Fixed for Angular Material)")
    print("-" * 50)
    try:
        result = client.track_with_selenium(test_pro)
        print(f"📊 Result: {result}")
        
        if result.get('success'):
            print("✅ Selenium method succeeded!")
            print(f"   Status: {result.get('status', 'Unknown')}")
            print(f"   Details: {result.get('details', [])}")
        else:
            print(f"❌ Selenium method failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Selenium method error: {e}")
    
    print("\n🔧 Testing Full Tracking Method (All layers)")
    print("-" * 50)
    try:
        result = await client.track_shipment(test_pro)
        print(f"📊 Final Result: {result}")
        
        if result.get('success'):
            print("✅ Full tracking succeeded!")
            print(f"   Status: {result.get('status', 'Unknown')}")
            print(f"   Carrier: {result.get('carrier', 'Unknown')}")
            if 'details' in result:
                print(f"   Details: {result['details']}")
        else:
            print(f"❌ Full tracking failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Full tracking error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 FIXED ESTES TRACKING TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fixed_estes_tracking()) 