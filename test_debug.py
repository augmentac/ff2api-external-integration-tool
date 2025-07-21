#!/usr/bin/env python3
"""
Debug test for specific PRO number
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.cloud_native_tracker import CloudNativeTracker
import asyncio
import json

async def test_debug():
    """Debug test for specific PRO number"""
    tracker = CloudNativeTracker()
    
    # Test specific PRO that should show MEMPHIS, TN US
    pro_number = '1642457961'
    carrier = 'Estes Express'
    
    print(f"Testing Estes PRO {pro_number}")
    print("Expected: Delivered | MEMPHIS, TN US")
    print("-" * 50)
    
    try:
        result = await asyncio.wait_for(
            tracker.track_shipment(pro_number, carrier),
            timeout=30
        )
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
        status = result.get('tracking_status', 'N/A')
        location = result.get('tracking_location', 'N/A')
        method = result.get('extracted_from', 'unknown')
        
        print(f"\nStatus: {status}")
        print(f"Location: {location}")
        print(f"Method: {method}")
        
        if status == 'Delivered' and 'MEMPHIS, TN US' in location:
            print("\n✅ SUCCESS! Result matches expected output")
        else:
            print("\n❌ FAILED! Result does not match expected output")
            
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()
    finally:
        # Clean up sessions
        try:
            await tracker.session_manager.close_all_sessions()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")

if __name__ == "__main__":
    asyncio.run(test_debug())