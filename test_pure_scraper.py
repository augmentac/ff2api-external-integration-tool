#!/usr/bin/env python3
"""
Quick test of the pure web scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.cloud_native_tracker import CloudNativeTracker
import asyncio
import json

async def test_pure_scraper():
    """Test the pure web scraper"""
    tracker = CloudNativeTracker()
    
    # Test cases for specific PROs mentioned by the user
    test_cases = [
        ('5939747181', 'FedEx Freight Economy', 'FedEx'),
        ('1642457961', 'Estes Express', 'Estes'),
        ('536246554', 'Peninsula Truck Lines Inc', 'Peninsula'),
    ]
    
    print("🚀 Testing Pure Web Scraper Implementation")
    print("=" * 50)
    
    for pro_number, carrier, carrier_short in test_cases:
        print(f"\nTesting {carrier_short} PRO {pro_number}...")
        
        try:
            result = await asyncio.wait_for(
                tracker.track_shipment(pro_number, carrier),
                timeout=30
            )
            
            success = result.get('status') == 'success'
            method = result.get('extracted_from', 'unknown')
            status = result.get('tracking_status', 'N/A')
            location = result.get('tracking_location', 'N/A')
            
            status_indicator = "✅" if success else "❌"
            print(f"  {status_indicator} Status: {status}")
            print(f"  {status_indicator} Location: {location}")
            print(f"  {status_indicator} Method: {method}")
            
            if success:
                print(f"  ✅ SUCCESS for {carrier_short} PRO {pro_number}")
            else:
                print(f"  ❌ FAILED for {carrier_short} PRO {pro_number}")
                
        except asyncio.TimeoutError:
            print(f"  ⏱️ TIMEOUT for {carrier_short} PRO {pro_number}")
        except Exception as e:
            print(f"  ❌ ERROR for {carrier_short} PRO {pro_number}: {e}")
    
    print("\n" + "=" * 50)
    print("Pure web scraper test complete")

if __name__ == "__main__":
    asyncio.run(test_pure_scraper())