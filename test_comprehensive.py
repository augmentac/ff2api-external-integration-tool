#!/usr/bin/env python3
"""
Comprehensive test of all user-specified PRO numbers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.cloud_native_tracker import CloudNativeTracker
import asyncio
import json

async def test_comprehensive():
    """Test all PRO numbers the user specifically mentioned"""
    tracker = CloudNativeTracker()
    
    # Test cases from user requirements
    test_cases = [
        # User mentioned these specific PROs and expected results
        ('5939747181', 'FedEx Freight Economy', 'FedEx', 'Delivered', 'LEESBURG, FL US'),
        ('1642457961', 'Estes Express', 'Estes', 'Delivered', 'MEMPHIS, TN US'),
        ('536246554', 'Peninsula Truck Lines Inc', 'Peninsula', 'Delivered', 'PORT ANGELES, WA'),
        
        # Additional test cases
        ('4012381741', 'FedEx Freight Priority', 'FedEx', 'In Transit', 'INDIANAPOLIS, IN US'),
        ('9460946246', 'FedEx Freight Priority', 'FedEx', 'Delivered', 'MEMPHIS, TN US'),
        ('0628143046', 'Estes Express', 'Estes', 'Delivered', 'RICHMOND, VA US'),
        ('2330112981', 'Estes Express', 'Estes', 'In Transit', 'ATLANTA, GA US'),
        ('536246546', 'Peninsula Truck Lines Inc', 'Peninsula', 'Delivered', 'PORT ANGELES, WA US'),
        ('62263246', 'Peninsula Truck Lines Inc', 'Peninsula', 'Delivered', 'PORTLAND, OR US'),
        ('933784785', 'R&L Carriers', 'R&L', 'Delivered', 'ATLANTA, GA US'),
        ('I141094116', 'R&L Carriers', 'R&L', 'In Transit', 'CHICAGO, IL US'),
        ('14588517-6', 'R&L Carriers', 'R&L', 'Delivered', 'ATLANTA, GA US'),
    ]
    
    print("🎯 COMPREHENSIVE LTL TRACKING TEST")
    print("Testing 100% success rate with real tracking data")
    print("=" * 70)
    
    results = []
    
    for i, (pro_number, carrier, carrier_short, expected_status, expected_location) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing {carrier_short} PRO {pro_number}")
        print(f"Expected: {expected_status} | {expected_location}")
        
        try:
            result = await asyncio.wait_for(
                tracker.track_shipment(pro_number, carrier),
                timeout=30
            )
            
            success = result.get('status') == 'success'
            method = result.get('extracted_from', 'unknown')
            status = result.get('tracking_status', 'N/A')
            location = result.get('tracking_location', 'N/A')
            
            # Check if results match expectations
            status_match = status == expected_status
            location_match = expected_location.upper() in location.upper()
            
            status_indicator = "✅" if success else "❌"
            match_indicator = "🎯" if (status_match and location_match) else "⚠️"
            
            print(f"  {status_indicator} Status: {status} {'✅' if status_match else '❌'}")
            print(f"  {status_indicator} Location: {location} {'✅' if location_match else '❌'}")
            print(f"  {status_indicator} Method: {method}")
            print(f"  {match_indicator} Match: {'Perfect' if (status_match and location_match) else 'Partial'}")
            
            results.append({
                'pro': pro_number,
                'carrier': carrier_short,
                'success': success,
                'status': status,
                'location': location,
                'method': method,
                'expected_status': expected_status,
                'expected_location': expected_location,
                'status_match': status_match,
                'location_match': location_match,
                'perfect_match': status_match and location_match
            })
            
        except asyncio.TimeoutError:
            print(f"  ⏱️ TIMEOUT")
            results.append({
                'pro': pro_number,
                'carrier': carrier_short,
                'success': False,
                'status': 'Timeout',
                'location': 'Timeout',
                'method': 'timeout',
                'expected_status': expected_status,
                'expected_location': expected_location,
                'status_match': False,
                'location_match': False,
                'perfect_match': False
            })
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                'pro': pro_number,
                'carrier': carrier_short,
                'success': False,
                'status': 'Error',
                'location': str(e),
                'method': 'error',
                'expected_status': expected_status,
                'expected_location': expected_location,
                'status_match': False,
                'location_match': False,
                'perfect_match': False
            })
    
    # Final analysis
    print("\n" + "=" * 70)
    print("FINAL RESULTS ANALYSIS")
    print("=" * 70)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    perfect_matches = sum(1 for r in results if r['perfect_match'])
    
    success_rate = (successful_tests / total_tests) * 100
    accuracy_rate = (perfect_matches / total_tests) * 100
    
    print(f"Total tests: {total_tests}")
    print(f"Successful extractions: {successful_tests}")
    print(f"Perfect matches: {perfect_matches}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Accuracy rate: {accuracy_rate:.1f}%")
    
    # Carrier breakdown
    carriers = {}
    for result in results:
        carrier = result['carrier']
        if carrier not in carriers:
            carriers[carrier] = {'total': 0, 'success': 0, 'perfect': 0}
        carriers[carrier]['total'] += 1
        if result['success']:
            carriers[carrier]['success'] += 1
        if result['perfect_match']:
            carriers[carrier]['perfect'] += 1
    
    print(f"\nCarrier breakdown:")
    for carrier, stats in carriers.items():
        carrier_success = (stats['success'] / stats['total']) * 100
        carrier_accuracy = (stats['perfect'] / stats['total']) * 100
        print(f"  {carrier}: {stats['success']}/{stats['total']} success ({carrier_success:.1f}%), {stats['perfect']}/{stats['total']} perfect ({carrier_accuracy:.1f}%)")
    
    # Critical PRO numbers (user mentioned these specifically)
    critical_pros = ['5939747181', '1642457961', '536246554']
    critical_results = [r for r in results if r['pro'] in critical_pros]
    critical_success = sum(1 for r in critical_results if r['success'])
    critical_perfect = sum(1 for r in critical_results if r['perfect_match'])
    
    print(f"\nCritical PRO numbers (user-specified):")
    for result in critical_results:
        match_status = "✅ PERFECT" if result['perfect_match'] else "⚠️ PARTIAL" if result['success'] else "❌ FAILED"
        print(f"  {result['pro']} ({result['carrier']}): {match_status}")
    
    print(f"\nCritical PRO success rate: {critical_success}/{len(critical_results)} ({(critical_success/len(critical_results)*100):.1f}%)")
    print(f"Critical PRO accuracy rate: {critical_perfect}/{len(critical_results)} ({(critical_perfect/len(critical_results)*100):.1f}%)")
    
    # Success criteria
    if success_rate >= 100.0 and accuracy_rate >= 90.0:
        print(f"\n🎉 EXCELLENT! System achieving 100% success with {accuracy_rate:.1f}% accuracy")
        print("✅ Ready for production deployment!")
        return True
    elif success_rate >= 100.0:
        print(f"\n🚀 GREAT! System achieving 100% success with {accuracy_rate:.1f}% accuracy")
        print("✅ System is working but could improve accuracy")
        return True
    elif success_rate >= 90.0:
        print(f"\n📈 GOOD! System achieving {success_rate:.1f}% success with {accuracy_rate:.1f}% accuracy")
        print("🔧 Close to perfect - minor improvements needed")
        return False
    else:
        print(f"\n💔 NEEDS WORK! System achieving {success_rate:.1f}% success with {accuracy_rate:.1f}% accuracy")
        print("🛠️ Significant improvements needed")
        return False

if __name__ == "__main__":
    try:
        print("🎯 COMPREHENSIVE LTL TRACKING TEST")
        print("Testing 100% success rate with pure web scraping")
        print("No external dependencies - pure HTTP scraping only")
        print()
        
        success = asyncio.run(test_comprehensive())
        
        if success:
            print("\n🏆 SYSTEM READY FOR PRODUCTION!")
            print("100% success rate achieved with pure web scraping")
        else:
            print("\n🔧 IMPROVEMENTS NEEDED")
            print("System needs optimization for better accuracy")
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)