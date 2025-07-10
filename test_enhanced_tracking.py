#!/usr/bin/env python3
"""
Comprehensive test for enhanced tracking system with anti-scraping bypass
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import time
from typing import Dict, List

try:
    from backend.enhanced_tracking_client import EnhancedTrackingClient
    from backend.anti_scraping_bypass import ProxyConfig
    from backend.carrier_detection import detect_carrier_from_pro
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_enhanced_tracking():
    """Test enhanced tracking with anti-scraping bypass"""
    
    # Test cases with expected results
    test_cases = [
        {
            'pro_number': '536246546',
            'carrier': 'Peninsula Truck Lines',
            'expected_status': 'Delivered',
            'expected_timestamp': '07/01/2025 02:14pm',
            'expected_location': 'PORT ANGELES, WA'
        },
        {
            'pro_number': '9460946246',
            'carrier': 'FedEx Freight',
            'expected_status': 'Delivered',
            'expected_timestamp': 'Real-time data',
            'expected_location': 'FedEx Network'
        },
        {
            'pro_number': '2121121288',
            'carrier': 'Estes Express',
            'expected_status': 'Delivery',
            'expected_timestamp': '07/08/2025 10:57 AM',
            'expected_location': 'WOODBURN, OR US'
        }
    ]
    
    print("=" * 60)
    print("ENHANCED TRACKING SYSTEM TEST")
    print("=" * 60)
    
    # Initialize enhanced client
    client = EnhancedTrackingClient()
    
    # Add some test proxies (you would add real proxies here)
    # client.bypass_system.add_proxy(ProxyConfig(
    #     host='proxy.example.com',
    #     port=8080,
    #     username='user',
    #     password='pass'
    # ))
    
    results = []
    
    for test_case in test_cases:
        pro_number = test_case['pro_number']
        expected_carrier = test_case['carrier']
        
        print(f"\nTesting PRO: {pro_number}")
        print(f"Expected Carrier: {expected_carrier}")
        print("-" * 40)
        
        # Test carrier detection first
        carrier_info = detect_carrier_from_pro(pro_number)
        if carrier_info:
            print(f"✅ Carrier Detection: {carrier_info['carrier_name']}")
        else:
            print("❌ Carrier Detection: FAILED")
            continue
        
        # Test enhanced tracking
        start_time = time.time()
        result = client.track_pro_number(pro_number)
        end_time = time.time()
        
        print(f"⏱️  Processing Time: {end_time - start_time:.2f} seconds")
        print(f"🎯 Success: {result.scrape_success}")
        print(f"📊 Status: {result.tracking_status}")
        print(f"🎬 Event: {result.tracking_event}")
        print(f"⏰ Timestamp: {result.tracking_timestamp}")
        print(f"📍 Location: {result.tracking_location}")
        
        if result.error_message:
            print(f"❌ Error: {result.error_message}")
        
        # Validate results
        validation_results = validate_tracking_result(result, test_case)
        print(f"✅ Validation: {validation_results['overall_score']:.1f}%")
        
        results.append({
            'pro_number': pro_number,
            'carrier': expected_carrier,
            'success': result.scrape_success,
            'validation_score': validation_results['overall_score'],
            'processing_time': end_time - start_time,
            'result': result
        })
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY RESULTS")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    avg_validation_score = sum(r['validation_score'] for r in results) / total_tests
    avg_processing_time = sum(r['processing_time'] for r in results) / total_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"Average Validation Score: {avg_validation_score:.1f}%")
    print(f"Average Processing Time: {avg_processing_time:.2f} seconds")
    
    # Detailed results
    print("\nDetailed Results:")
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {result['pro_number']} ({result['carrier']}): "
              f"{result['validation_score']:.1f}% in {result['processing_time']:.2f}s")
    
    # Cleanup
    client.cleanup()
    
    return results


def validate_tracking_result(result, expected: Dict) -> Dict:
    """
    Validate tracking result against expected values
    
    Args:
        result: TrackingResult object
        expected: Dictionary with expected values
        
    Returns:
        Dictionary with validation scores
    """
    validation = {
        'success_score': 100 if result.scrape_success else 0,
        'status_score': 0,
        'timestamp_score': 0,
        'location_score': 0,
        'overall_score': 0
    }
    
    if result.scrape_success:
        # Check status
        if result.tracking_status and expected.get('expected_status'):
            if expected['expected_status'].lower() in result.tracking_status.lower():
                validation['status_score'] = 100
            elif any(keyword in result.tracking_status.lower() for keyword in ['delivered', 'delivery', 'transit']):
                validation['status_score'] = 75
        
        # Check timestamp
        if result.tracking_timestamp and expected.get('expected_timestamp'):
            if expected['expected_timestamp'] in result.tracking_timestamp:
                validation['timestamp_score'] = 100
            elif any(keyword in result.tracking_timestamp.lower() for keyword in ['2025', 'am', 'pm']):
                validation['timestamp_score'] = 75
            elif result.tracking_timestamp != 'Real-time data requires account access':
                validation['timestamp_score'] = 50
        
        # Check location
        if result.tracking_location and expected.get('expected_location'):
            if expected['expected_location'].lower() in result.tracking_location.lower():
                validation['location_score'] = 100
            elif any(keyword in result.tracking_location.lower() for keyword in ['network', 'terminal', 'hub']):
                validation['location_score'] = 50
    
    # Calculate overall score
    scores = [validation['success_score'], validation['status_score'], 
              validation['timestamp_score'], validation['location_score']]
    validation['overall_score'] = sum(scores) / len(scores)
    
    return validation


def test_bypass_strategies():
    """Test individual bypass strategies"""
    
    print("\n" + "=" * 60)
    print("BYPASS STRATEGY TESTING")
    print("=" * 60)
    
    client = EnhancedTrackingClient()
    
    # Test Peninsula strategies
    peninsula_pro = '536246546'
    carrier_info = detect_carrier_from_pro(peninsula_pro)
    
    if carrier_info:
        strategies = client.bypass_system.get_carrier_specific_strategy('peninsula')
        
        print(f"\nTesting Peninsula PRO {peninsula_pro}")
        print(f"Strategies: {[s.value for s in strategies]}")
        
        for strategy in strategies:
            try:
                print(f"\n🔄 Testing {strategy.value}...")
                result = client._execute_strategy(strategy, peninsula_pro, carrier_info)
                
                if result and result.scrape_success:
                    print(f"✅ {strategy.value}: SUCCESS")
                    print(f"   Status: {result.tracking_status}")
                    print(f"   Event: {result.tracking_event}")
                    print(f"   Timestamp: {result.tracking_timestamp}")
                    print(f"   Location: {result.tracking_location}")
                else:
                    print(f"❌ {strategy.value}: FAILED")
                    
            except Exception as e:
                print(f"❌ {strategy.value}: ERROR - {e}")
    
    client.cleanup()


def test_session_management():
    """Test session management and fingerprinting"""
    
    print("\n" + "=" * 60)
    print("SESSION MANAGEMENT TESTING")
    print("=" * 60)
    
    client = EnhancedTrackingClient()
    
    # Test fingerprint generation
    fingerprints = client.bypass_system.browser_fingerprints[:3]
    
    print(f"Generated {len(fingerprints)} browser fingerprints")
    
    for i, fp in enumerate(fingerprints):
        print(f"\nFingerprint {i+1}:")
        print(f"  User Agent: {fp.user_agent[:50]}...")
        print(f"  Platform: {fp.platform}")
        print(f"  Viewport: {fp.viewport}")
        print(f"  Timezone: {fp.timezone}")
        print(f"  Language: {fp.language}")
    
    # Test session creation
    print("\nTesting session creation...")
    
    carriers = ['peninsula', 'fedex', 'estes']
    
    for carrier in carriers:
        try:
            session = client.bypass_system.create_stealth_session(carrier)
                     print(f"✅ {carrier.title()} session created successfully")
         print(f"   User-Agent: {session.headers.get('User-Agent', 'Not set')[:50]}...")
         
         # Test session warming
         domain_map: Dict[str, str] = {
             'peninsula': 'peninsulatruck.com',
             'fedex': 'fedex.com',
             'estes': 'estes-express.com'
         }
            
            if carrier in domain_map:
                warmed = client.bypass_system.warm_session(session, domain_map[carrier])
                print(f"   Session warming: {'✅ SUCCESS' if warmed else '❌ FAILED'}")
            
        except Exception as e:
            print(f"❌ {carrier.title()} session creation failed: {e}")
    
    client.cleanup()


if __name__ == "__main__":
    print("Starting Enhanced Tracking System Tests...")
    
    # Run main tracking tests
    results = test_enhanced_tracking()
    
    # Run bypass strategy tests
    test_bypass_strategies()
    
    # Run session management tests
    test_session_management()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    
    # Final summary
    if results:
        success_rate = sum(1 for r in results if r['success']) / len(results) * 100
        print(f"\nFinal Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Anti-scraping bypass system is highly effective!")
        elif success_rate >= 70:
            print("✅ GOOD: Anti-scraping bypass system is working well")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Anti-scraping bypass system needs improvement")
        else:
            print("❌ POOR: Anti-scraping bypass system requires significant work")
    
    print("\nTest completed successfully!") 