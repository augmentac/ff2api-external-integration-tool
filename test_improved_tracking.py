#!/usr/bin/env python3
"""
Test Improved Tracking System
Verify that it now uses the working barrier-breaking methods
"""

import asyncio
from src.backend.improved_cloud_tracking import ImprovedCloudTracker, track_shipment_improved
import time

async def test_improved_tracking():
    """Test the improved tracking system"""
    
    print("🧪 TESTING IMPROVED TRACKING SYSTEM")
    print("=" * 60)
    
    # Create tracker
    tracker = ImprovedCloudTracker()
    
    # Show system status
    status = tracker.get_system_status()
    print("📊 System Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()
    
    # Test tracking numbers
    test_cases = [
        ("0628143046", "Estes Express"),
        ("1282975382", "Estes Express"),
    ]
    
    for tracking_number, carrier in test_cases:
        print(f"📦 Testing: {tracking_number} ({carrier})")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Track the shipment
            result = await tracker.track_shipment(tracking_number, carrier)
            
            processing_time = time.time() - start_time
            
            # Display results
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"✅ Success: {result.get('success', False)}")
            print(f"🔧 System Used: {result.get('system_used', 'N/A')}")
            print(f"🔍 Status: {result.get('status', 'N/A')}")
            print(f"📍 Location: {result.get('location', 'N/A')}")
            print(f"📋 Events: {len(result.get('events', []))}")
            print(f"💪 Barrier Solved: {result.get('barrier_solved', 'N/A')}")
            
            if result.get('success'):
                print("🎉 SUCCESS - TRACKING DATA RETRIEVED!")
                
                # Show events if any
                events = result.get('events', [])
                if events:
                    print(f"📊 Sample Event: {events[0].get('description', 'N/A')[:100]}...")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                print(f"💡 Recommendation: {result.get('recommendation', 'N/A')}")
                
            print()
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            print()

if __name__ == "__main__":
    print("🚀 Starting improved tracking system tests...")
    print("This should now use the working barrier-breaking methods!")
    print()
    
    # Run the test
    asyncio.run(test_improved_tracking())
    
    print("✅ Testing complete!")
    print("\nExpected improvements:")
    print("1. ✅ Uses barrier-breaking system when available")
    print("2. ✅ Falls back to Apple Silicon system for local environments")
    print("3. ✅ Uses cloud browser system for cloud environments")
    print("4. ✅ Provides detailed system status and recommendations")
    print("5. ✅ Actually retrieves tracking data instead of just explaining failures") 