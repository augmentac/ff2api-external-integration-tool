#!/usr/bin/env python3
"""
Test comprehensive tracking system with anti-bot bypass and alternative data sources
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.cloud_native_tracker import CloudNativeTracker
import asyncio

async def test_comprehensive_tracking():
    """Test the comprehensive tracking system"""
    tracker = CloudNativeTracker()
    
    # Test with a timeout to prevent hanging
    test_cases = [
        ('1642457961', 'Estes Express', 'MEMPHIS, TN US'),
        ('536246554', 'Peninsula Truck Lines Inc', 'PORT ANGELES, WA'),
        ('5939747181', 'FedEx Freight Economy', 'LEESBURG, FL US')
    ]
    
    results = []
    
    for pro_number, carrier, expected_location in test_cases:
        print(f"Testing {carrier} PRO {pro_number}...")
        
        try:
            # Use a timeout to prevent hanging
            result = await asyncio.wait_for(
                tracker.track_shipment(pro_number, carrier),
                timeout=30  # 30 second timeout
            )
            
            print(f"  Status: {result.get('tracking_status', 'N/A')}")
            print(f"  Location: {result.get('tracking_location', 'N/A')}")
            print(f"  Method: {result.get('extracted_from', 'N/A')}")
            print(f"  Success: {result.get('status', 'N/A')}")
            print()
            
            results.append({
                'pro': pro_number,
                'carrier': carrier,
                'success': result.get('status') == 'success',
                'method': result.get('extracted_from', 'unknown'),
                'location': result.get('tracking_location', 'N/A'),
                'expected': expected_location
            })
            
        except asyncio.TimeoutError:
            print(f"  ⏱️ Timeout for {carrier} PRO {pro_number}")
            results.append({
                'pro': pro_number,
                'carrier': carrier,
                'success': False,
                'method': 'timeout',
                'location': 'Timeout',
                'expected': expected_location
            })
        except Exception as e:
            print(f"  ❌ Error for {carrier} PRO {pro_number}: {e}")
            results.append({
                'pro': pro_number,
                'carrier': carrier,
                'success': False,
                'method': 'error',
                'location': f'Error: {e}',
                'expected': expected_location
            })
    
    # Analyze results
    print("="*50)
    print("COMPREHENSIVE TRACKING ANALYSIS")
    print("="*50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    print()
    
    # Method breakdown
    methods = {}
    for result in results:
        method = result['method']
        if method not in methods:
            methods[method] = {'count': 0, 'success': 0}
        methods[method]['count'] += 1
        if result['success']:
            methods[method]['success'] += 1
    
    print("Method breakdown:")
    for method, stats in methods.items():
        success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
        print(f"  {method}: {stats['success']}/{stats['count']} ({success_rate:.1f}%)")
    
    # Check for actual data extraction
    advanced_methods = [r for r in results if 'advanced_anti_bot_bypass' in r['method'] or 'alternative_data_sources' in r['method']]
    
    if advanced_methods:
        print(f"\n✅ Advanced tracking methods working: {len(advanced_methods)} successful extractions")
        print("Advanced methods used:")
        for r in advanced_methods:
            print(f"  - {r['carrier']} PRO {r['pro']}: {r['method']}")
        return True
    else:
        print(f"\n⚠️  Advanced tracking methods not successful - all using fallback")
        print("All results:")
        for r in results:
            print(f"  - {r['carrier']} PRO {r['pro']}: {r['method']} -> {r['location']}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_comprehensive_tracking())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)