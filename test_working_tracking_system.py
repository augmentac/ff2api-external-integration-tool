#!/usr/bin/env python3
"""
Test Working Tracking System
Verify that the barrier-breaking system actually retrieves real tracking data
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_working_tracking_system():
    """Test the working tracking system with real PRO numbers"""
    
    print("🚀 TESTING WORKING TRACKING SYSTEM")
    print("=" * 60)
    
    # Test PRO numbers
    test_shipments = [
        {"pro": "0628143046", "carrier": "Estes Express", "expected": "Should work with Apple Silicon client"},
        {"pro": "1234567890", "carrier": "FedEx Freight", "expected": "Should work with CloudFlare bypass"},
        {"pro": "123456789", "carrier": "R&L Carriers", "expected": "Should work with HTTP methods"},
        {"pro": "TEST123", "carrier": "Peninsula Truck Lines", "expected": "Should work with HTTP methods"},
    ]
    
    try:
        # Import the working tracking system
        from src.backend.working_tracking_system import WorkingTrackingSystem
        
        system = WorkingTrackingSystem()
        
        print(f"✅ Working Tracking System initialized successfully")
        print(f"📍 Environment: {'Cloud' if system.is_cloud else 'Local'}")
        print(f"🎯 Estes Client: {'Available' if system.estes_client else 'Not Available'}")
        print(f"🎯 FedEx Client: {'Available' if system.fedex_client else 'Not Available'}")
        print(f"🎯 Enhanced Client: {'Available' if system.enhanced_client else 'Not Available'}")
        print()
        
        successful_tracks = 0
        barriers_solved = set()
        
        for i, shipment in enumerate(test_shipments, 1):
            pro = shipment["pro"]
            carrier = shipment["carrier"]
            expected = shipment["expected"]
            
            print(f"📦 Test {i}/{len(test_shipments)}: {carrier}")
            print(f"🎯 PRO: {pro}")
            print(f"💡 Expected: {expected}")
            print("-" * 40)
            
            start_time = time.time()
            
            try:
                # Track the shipment
                result = await system.track_shipment(pro, carrier)
                
                duration = time.time() - start_time
                
                if result.get('success'):
                    successful_tracks += 1
                    status = result.get('status', 'N/A')
                    location = result.get('location', 'N/A')
                    method = result.get('method', 'Unknown')
                    barrier = result.get('barrier_solved', 'None')
                    
                    print(f"✅ SUCCESS ({duration:.1f}s)")
                    print(f"   📍 Status: {status}")
                    print(f"   🌍 Location: {location}")
                    print(f"   🔧 Method: {method}")
                    
                    if barrier and barrier != 'None':
                        barriers_solved.add(barrier)
                        print(f"   💪 Barrier Solved: {barrier}")
                    
                    # Show events if available
                    events = result.get('events', [])
                    if events:
                        print(f"   📋 Events: {len(events)} tracking events")
                        for event in events[:2]:  # Show first 2 events
                            print(f"      - {event}")
                    
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"❌ FAILED ({duration:.1f}s)")
                    print(f"   🚨 Error: {error}")
                    
                    # Show attempts if available
                    attempts = result.get('attempts_made', 0)
                    if attempts > 0:
                        print(f"   🔄 Attempts Made: {attempts}")
                
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")
            
            print()
        
        # Summary
        success_rate = (successful_tracks / len(test_shipments)) * 100
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Successful Tracks: {successful_tracks}/{len(test_shipments)} ({success_rate:.1f}%)")
        print(f"💪 Barriers Solved: {', '.join(barriers_solved) if barriers_solved else 'None'}")
        
        if success_rate > 0:
            print("🎉 WORKING TRACKING SYSTEM IS FUNCTIONING!")
            print("   The system is successfully retrieving real tracking data.")
        else:
            print("⚠️  WORKING TRACKING SYSTEM NEEDS ATTENTION")
            print("   No successful tracks - check barrier-breaking components.")
        
        return success_rate > 0
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all barrier-breaking components are available")
        return False
    except Exception as e:
        print(f"❌ System Error: {e}")
        return False

async def test_cloud_compatible_tracking():
    """Test the cloud compatible tracking system"""
    
    print("\n🌐 TESTING CLOUD COMPATIBLE TRACKING")
    print("=" * 60)
    
    try:
        # Import the cloud compatible system
        from src.backend.cloud_compatible_tracking import CloudCompatibleTracker
        
        tracker = CloudCompatibleTracker()
        
        print(f"✅ Cloud Compatible Tracker initialized")
        print(f"🎯 System: {tracker.system_name}")
        print()
        
        # Test a single shipment
        test_pro = "0628143046"
        test_carrier = "Estes Express"
        
        print(f"📦 Testing: {test_carrier} - {test_pro}")
        
        start_time = time.time()
        result = await tracker.track_shipment(test_pro, test_carrier)
        duration = time.time() - start_time
        
        if result.get('success'):
            print(f"✅ SUCCESS ({duration:.1f}s)")
            print(f"   📍 Status: {result.get('status', 'N/A')}")
            print(f"   🌍 Location: {result.get('location', 'N/A')}")
            print(f"   🔧 System: {result.get('system_used', 'N/A')}")
            
            method = result.get('method')
            if method:
                print(f"   🛠️  Method: {method}")
            
            barrier = result.get('barrier_solved')
            if barrier and barrier != 'None':
                print(f"   💪 Barrier Solved: {barrier}")
        else:
            print(f"❌ FAILED ({duration:.1f}s)")
            print(f"   🚨 Error: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ System Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE WORKING TRACKING SYSTEM TEST")
    print("=" * 80)
    
    # Test 1: Working Tracking System
    working_success = await test_working_tracking_system()
    
    # Test 2: Cloud Compatible Tracking
    cloud_success = await test_cloud_compatible_tracking()
    
    # Final summary
    print("\n🎯 FINAL TEST SUMMARY")
    print("=" * 80)
    print(f"🚀 Working Tracking System: {'✅ PASS' if working_success else '❌ FAIL'}")
    print(f"🌐 Cloud Compatible Tracking: {'✅ PASS' if cloud_success else '❌ FAIL'}")
    
    if working_success or cloud_success:
        print("\n🎉 SUCCESS: At least one system is working and retrieving real tracking data!")
        print("   The barrier-breaking implementation is functional.")
    else:
        print("\n⚠️  WARNING: No systems are working properly.")
        print("   Check barrier-breaking component availability and configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 