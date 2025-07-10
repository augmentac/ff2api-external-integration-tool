#!/usr/bin/env python3
"""
Test Working Tracking System
Verify that it actually retrieves tracking data instead of just explaining failures
"""

import asyncio
import pandas as pd
from src.backend.working_cloud_tracking import WorkingCloudTracker
from src.backend.cloud_compatible_tracking import CloudCompatibleTracker
import time

async def test_working_tracking_system():
    """Test the working tracking system"""
    
    print("🧪 TESTING WORKING TRACKING SYSTEM")
    print("=" * 60)
    
    # Test tracking numbers
    test_cases = [
        ("0628143046", "Estes Express"),
        ("1282975382", "Estes Express"),
        ("690879689", "Estes Express"),
        ("750773321", "Estes Express"),
    ]
    
    tracker = WorkingCloudTracker()
    
    for tracking_number, carrier in test_cases:
        print(f"\n📦 Testing: {tracking_number} ({carrier})")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Track the shipment
            result = await tracker.track_shipment(tracking_number, carrier)
            
            processing_time = time.time() - start_time
            
            # Display results
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"✅ Success: {result.get('success', False)}")
            print(f"🔍 Status: {result.get('status', 'N/A')}")
            print(f"📍 Location: {result.get('location', 'N/A')}")
            print(f"📋 Events: {len(result.get('events', []))}")
            
            if result.get('success'):
                print("🎉 TRACKING DATA SUCCESSFULLY RETRIEVED!")
                
                # Show events if any
                events = result.get('events', [])
                if events:
                    print(f"📊 Tracking Events ({len(events)}):")
                    for i, event in enumerate(events[:3], 1):  # Show first 3 events
                        print(f"  {i}. {event.get('date', 'N/A')}: {event.get('description', 'N/A')}")
                        if event.get('location'):
                            print(f"     📍 {event['location']}")
                        if event.get('status'):
                            print(f"     🔍 {event['status']}")
                    
                    if len(events) > 3:
                        print(f"  ... and {len(events) - 3} more events")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return True

async def test_cloud_compatible_integration():
    """Test the cloud compatible tracker integration"""
    
    print("\n🌐 TESTING CLOUD COMPATIBLE INTEGRATION")
    print("=" * 60)
    
    tracker = CloudCompatibleTracker()
    tracking_number = "0628143046"
    carrier = "Estes Express"
    
    print(f"📦 Testing: {tracking_number} ({carrier})")
    
    try:
        result = await tracker.track_shipment(tracking_number, carrier)
        
        print(f"✅ Success: {result.get('success', False)}")
        print(f"🔍 Status: {result.get('status', 'N/A')}")
        print(f"📍 Location: {result.get('location', 'N/A')}")
        print(f"📋 Events: {len(result.get('events', []))}")
        print(f"🌐 Cloud Compatible: {result.get('cloud_compatible', False)}")
        
        if result.get('success'):
            print("🎉 CLOUD INTEGRATION SUCCESSFUL!")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting working tracking system tests...")
    
    # Run working tracker tests
    asyncio.run(test_working_tracking_system())
    
    # Run cloud compatible integration tests
    asyncio.run(test_cloud_compatible_integration())
    
    print("\n✅ Testing complete!")
    print("\nExpected improvements:")
    print("1. ✅ Actual tracking data retrieval instead of error messages")
    print("2. ✅ Status and location information extracted")
    print("3. ✅ Tracking events parsed from responses")
    print("4. ✅ Multiple fallback methods for reliability")
    print("5. ✅ Cloud-compatible implementation") 