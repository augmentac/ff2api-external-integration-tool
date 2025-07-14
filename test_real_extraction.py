#!/usr/bin/env python3
"""
Test real data extraction system - NO SIMULATION
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.cloud_native_tracker import CloudNativeTracker
import asyncio

async def test_real_extraction():
    """Test the real data extraction system"""
    tracker = CloudNativeTracker()
    
    # Test cases with known PRO numbers
    test_cases = [
        ('1642457961', 'Estes Express', 'Should be delivered in MEMPHIS, TN US'),
        ('536246554', 'Peninsula Truck Lines Inc', 'Should be delivered in PORT ANGELES, WA'),
        ('5939747181', 'FedEx Freight Economy', 'Should be delivered in LEESBURG, FL US')
    ]
    
    results = []
    
    for pro_number, carrier, expected in test_cases:
        print(f"Testing {carrier} PRO {pro_number} (timeout: 45s)...")
        print(f"Expected: {expected}")
        
        try:
            # Use a longer timeout for real extraction
            result = await asyncio.wait_for(
                tracker.track_shipment(pro_number, carrier),
                timeout=45  # 45 second timeout for real extraction
            )
            
            print(f"  Status: {result.get('tracking_status', 'N/A')}")
            print(f"  Location: {result.get('tracking_location', 'N/A')}")
            print(f"  Event: {result.get('tracking_event', 'N/A')}")
            print(f"  Method: {result.get('extracted_from', 'N/A')}")
            print(f"  Success: {result.get('status', 'N/A')}")
            print()
            
            results.append({
                'pro': pro_number,
                'carrier': carrier,
                'success': result.get('status') == 'success',
                'method': result.get('extracted_from', 'unknown'),
                'location': result.get('tracking_location', 'N/A'),
                'status': result.get('tracking_status', 'N/A'),
                'real_extraction': 'real_data_extraction' in result.get('extracted_from', '')
            })
            
        except asyncio.TimeoutError:
            print(f"  ⏱️ Timeout for {carrier} PRO {pro_number}")
            results.append({
                'pro': pro_number,
                'carrier': carrier,
                'success': False,
                'method': 'timeout',
                'location': 'Timeout',
                'status': 'Timeout',
                'real_extraction': False
            })
        except Exception as e:
            print(f"  ❌ Error for {carrier} PRO {pro_number}: {e}")
            results.append({
                'pro': pro_number,
                'carrier': carrier,
                'success': False,
                'method': 'error',
                'location': f'Error: {e}',
                'status': 'Error',
                'real_extraction': False
            })
    
    # Analyze results
    print("="*60)
    print("REAL DATA EXTRACTION ANALYSIS")
    print("="*60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    real_extraction_tests = sum(1 for r in results if r['real_extraction'])
    
    print(f"Total tests: {total_tests}")
    print(f"Successful extractions: {successful_tests}")
    print(f"Real data extractions: {real_extraction_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    print(f"Real extraction rate: {(real_extraction_tests/total_tests)*100:.1f}%")
    print()
    
    # Method breakdown
    methods = {}
    for result in results:
        method = result['method']
        if method not in methods:
            methods[method] = {'count': 0, 'success': 0, 'real': 0}
        methods[method]['count'] += 1
        if result['success']:
            methods[method]['success'] += 1
        if result['real_extraction']:
            methods[method]['real'] += 1
    
    print("Method breakdown:")
    for method, stats in methods.items():
        success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
        real_rate = (stats['real'] / stats['count']) * 100 if stats['count'] > 0 else 0
        print(f"  {method}: {stats['success']}/{stats['count']} success ({success_rate:.1f}%), {stats['real']}/{stats['count']} real ({real_rate:.1f}%)")
    
    # Detailed results
    print(\"\\nDetailed results:\")
    for r in results:
        extraction_type = \"🔍 REAL\" if r['real_extraction'] else \"🔁 FALLBACK\"
        status_indicator = \"✅\" if r['success'] else \"❌\"
        print(f\"  {status_indicator} {extraction_type} {r['carrier']} PRO {r['pro']}: {r['status']} at {r['location']}\")
    
    # Check if we're getting real data extraction
    if real_extraction_tests > 0:
        print(f\"\\n🎯 SUCCESS: {real_extraction_tests} real data extractions achieved!\")
        print(\"Real extraction methods working:\")
        for r in results:
            if r['real_extraction']:
                print(f\"  - {r['carrier']} PRO {r['pro']}: {r['method']}\")
        return True
    else:
        print(f\"\\n❌ FAILURE: No real data extractions achieved\")
        print(\"All results are from fallback/simulation methods\")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Starting Real Data Extraction Test")
        print("This test will attempt to extract actual tracking data from carrier websites")
        print("NO SIMULATION - Only real data extraction")
        print()
        
        success = asyncio.run(test_real_extraction())
        
        if success:
            print("\\n🎉 REAL DATA EXTRACTION SUCCESSFUL!")
        else:
            print("\\n💔 REAL DATA EXTRACTION FAILED - Need to enhance extraction methods")
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(\"\\n⏹️  Test interrupted by user\")
        sys.exit(1)
    except Exception as e:
        print(f\"\\n💥 Test failed with error: {e}\")
        sys.exit(1)