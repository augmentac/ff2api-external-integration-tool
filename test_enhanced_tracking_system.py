#!/usr/bin/env python3
"""
Test Enhanced Tracking System

This script tests the new enhanced tracking system with advanced browser automation
for Estes Express and FedEx Freight to overcome CPU architecture and CloudFlare barriers.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('enhanced_tracking_test.log')
    ]
)

logger = logging.getLogger(__name__)

class EnhancedTrackingSystemTest:
    """Test suite for enhanced tracking system"""
    
    def __init__(self):
        self.test_results = []
        self.logger = logging.getLogger(__name__)
        
        # Test PRO numbers (using the same ones from our previous tests)
        self.test_data = {
            'estes': [
                '0331234567',  # Sample Estes PRO
                '0331234568',  # Sample Estes PRO
                '0331234569'   # Sample Estes PRO
            ],
            'fedex': [
                '1234567890',  # Sample FedEx PRO
                '1234567891',  # Sample FedEx PRO
                '1234567892'   # Sample FedEx PRO
            ]
        }
    
    async def run_all_tests(self):
        """Run all enhanced tracking tests"""
        
        print("=" * 80)
        print("ENHANCED TRACKING SYSTEM TEST SUITE")
        print("=" * 80)
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Browser automation availability
        await self._test_browser_automation_availability()
        
        # Test 2: Enhanced Estes tracking
        await self._test_enhanced_estes_tracking()
        
        # Test 3: Enhanced FedEx tracking
        await self._test_enhanced_fedex_tracking()
        
        # Test 4: Fallback system integration
        await self._test_fallback_system()
        
        # Test 5: Performance comparison
        await self._test_performance_comparison()
        
        # Generate summary report
        self._generate_summary_report()
    
    async def _test_browser_automation_availability(self):
        """Test browser automation system availability"""
        
        print("🔧 Testing Browser Automation Availability...")
        print("-" * 50)
        
        try:
            from backend.enhanced_browser_automation import EnhancedBrowserAutomation
            
            automation = EnhancedBrowserAutomation()
            
            # Test session creation for different targets
            for target in ['estes', 'fedex', 'generic']:
                try:
                    session = await automation.create_stealth_session(target)
                    session_type = session.get('type', 'unknown')
                    
                    print(f"✅ {target.upper()} session created: {session_type}")
                    
                    # Test basic navigation
                    test_url = "https://httpbin.org/user-agent"
                    try:
                        content = await automation.navigate_with_stealth(session, test_url)
                        if content and len(content) > 0:
                            print(f"✅ {target.upper()} navigation successful")
                        else:
                            print(f"❌ {target.upper()} navigation failed - no content")
                    except Exception as e:
                        print(f"❌ {target.upper()} navigation failed: {e}")
                    
                    # Cleanup
                    await automation.cleanup_session(session)
                    
                except Exception as e:
                    print(f"❌ {target.upper()} session creation failed: {e}")
            
            self.test_results.append({
                'test': 'browser_automation_availability',
                'status': 'success',
                'message': 'Browser automation system is available'
            })
            
        except Exception as e:
            print(f"❌ Browser automation system unavailable: {e}")
            self.test_results.append({
                'test': 'browser_automation_availability',
                'status': 'error',
                'message': f'Browser automation system unavailable: {e}'
            })
        
        print()
    
    async def _test_enhanced_estes_tracking(self):
        """Test enhanced Estes Express tracking"""
        
        print("🚛 Testing Enhanced Estes Express Tracking...")
        print("-" * 50)
        
        try:
            from backend.enhanced_estes_client import EnhancedEstesClient
            
            client = EnhancedEstesClient()
            
            for pro_number in self.test_data['estes']:
                print(f"Testing Estes PRO: {pro_number}")
                
                try:
                    result = await client.track_shipment(pro_number)
                    
                    if result.get('status') == 'success':
                        print(f"✅ SUCCESS: {result.get('tracking_status', 'Unknown status')}")
                        print(f"   Event: {result.get('tracking_event', 'No event')[:100]}...")
                        print(f"   Source: {result.get('extracted_from', 'Unknown source')}")
                    elif result.get('status') == 'error':
                        print(f"❌ ERROR: {result.get('error_message', 'Unknown error')}")
                    else:
                        print(f"⚠️  UNKNOWN: {result}")
                    
                    self.test_results.append({
                        'test': 'enhanced_estes_tracking',
                        'pro_number': pro_number,
                        'status': result.get('status', 'unknown'),
                        'result': result
                    })
                    
                except Exception as e:
                    print(f"❌ EXCEPTION: {e}")
                    self.test_results.append({
                        'test': 'enhanced_estes_tracking',
                        'pro_number': pro_number,
                        'status': 'exception',
                        'error': str(e)
                    })
                
                print()
                
        except Exception as e:
            print(f"❌ Enhanced Estes client unavailable: {e}")
            self.test_results.append({
                'test': 'enhanced_estes_tracking',
                'status': 'error',
                'message': f'Enhanced Estes client unavailable: {e}'
            })
        
        print()
    
    async def _test_enhanced_fedex_tracking(self):
        """Test enhanced FedEx Freight tracking"""
        
        print("📦 Testing Enhanced FedEx Freight Tracking...")
        print("-" * 50)
        
        try:
            from backend.enhanced_fedex_client import EnhancedFedExClient
            
            client = EnhancedFedExClient()
            
            for pro_number in self.test_data['fedex']:
                print(f"Testing FedEx PRO: {pro_number}")
                
                try:
                    result = await client.track_shipment(pro_number)
                    
                    if result.get('status') == 'success':
                        print(f"✅ SUCCESS: {result.get('tracking_status', 'Unknown status')}")
                        print(f"   Event: {result.get('tracking_event', 'No event')[:100]}...")
                        print(f"   Source: {result.get('extracted_from', 'Unknown source')}")
                    elif result.get('status') == 'error':
                        print(f"❌ ERROR: {result.get('error_message', 'Unknown error')}")
                    else:
                        print(f"⚠️  UNKNOWN: {result}")
                    
                    self.test_results.append({
                        'test': 'enhanced_fedex_tracking',
                        'pro_number': pro_number,
                        'status': result.get('status', 'unknown'),
                        'result': result
                    })
                    
                except Exception as e:
                    print(f"❌ EXCEPTION: {e}")
                    self.test_results.append({
                        'test': 'enhanced_fedex_tracking',
                        'pro_number': pro_number,
                        'status': 'exception',
                        'error': str(e)
                    })
                
                print()
                
        except Exception as e:
            print(f"❌ Enhanced FedEx client unavailable: {e}")
            self.test_results.append({
                'test': 'enhanced_fedex_tracking',
                'status': 'error',
                'message': f'Enhanced FedEx client unavailable: {e}'
            })
        
        print()
    
    async def _test_fallback_system(self):
        """Test fallback system integration"""
        
        print("🔄 Testing Fallback System Integration...")
        print("-" * 50)
        
        try:
            # Test that enhanced clients can fall back to legacy systems
            from backend.enhanced_estes_client import EnhancedEstesClient
            from backend.enhanced_fedex_client import EnhancedFedExClient
            
            # Test Estes fallback
            estes_client = EnhancedEstesClient()
            try:
                result = await estes_client._track_with_legacy_fallback('0331234567')
                if result:
                    print("✅ Estes legacy fallback available")
                else:
                    print("⚠️  Estes legacy fallback returned None")
            except Exception as e:
                print(f"❌ Estes legacy fallback failed: {e}")
            
            # Test FedEx fallback
            fedex_client = EnhancedFedExClient()
            try:
                result = await fedex_client._track_with_legacy_fallback('1234567890')
                if result:
                    print("✅ FedEx legacy fallback available")
                else:
                    print("⚠️  FedEx legacy fallback returned None")
            except Exception as e:
                print(f"❌ FedEx legacy fallback failed: {e}")
            
            self.test_results.append({
                'test': 'fallback_system',
                'status': 'success',
                'message': 'Fallback system integration tested'
            })
            
        except Exception as e:
            print(f"❌ Fallback system test failed: {e}")
            self.test_results.append({
                'test': 'fallback_system',
                'status': 'error',
                'message': f'Fallback system test failed: {e}'
            })
        
        print()
    
    async def _test_performance_comparison(self):
        """Test performance comparison between enhanced and legacy systems"""
        
        print("⚡ Testing Performance Comparison...")
        print("-" * 50)
        
        try:
            import time
            
            # Test enhanced system performance
            enhanced_times = []
            
            from backend.enhanced_estes_client import EnhancedEstesClient
            client = EnhancedEstesClient()
            
            for pro_number in self.test_data['estes'][:1]:  # Test just one for performance
                start_time = time.time()
                try:
                    result = await client.track_shipment(pro_number)
                    end_time = time.time()
                    enhanced_times.append(end_time - start_time)
                    print(f"Enhanced Estes tracking time: {end_time - start_time:.2f}s")
                except Exception as e:
                    print(f"Enhanced tracking failed: {e}")
            
            # Test legacy system performance (if available)
            try:
                from backend.zero_cost_carriers import ZeroCostCarrierTracking
                legacy_client = ZeroCostCarrierTracking()
                
                legacy_times = []
                for pro_number in self.test_data['estes'][:1]:
                    start_time = time.time()
                    try:
                        result = legacy_client.track_estes_express(pro_number)
                        end_time = time.time()
                        legacy_times.append(end_time - start_time)
                        print(f"Legacy Estes tracking time: {end_time - start_time:.2f}s")
                    except Exception as e:
                        print(f"Legacy tracking failed: {e}")
                
                # Compare performance
                if enhanced_times and legacy_times:
                    avg_enhanced = sum(enhanced_times) / len(enhanced_times)
                    avg_legacy = sum(legacy_times) / len(legacy_times)
                    
                    print(f"Average enhanced time: {avg_enhanced:.2f}s")
                    print(f"Average legacy time: {avg_legacy:.2f}s")
                    
                    if avg_enhanced < avg_legacy:
                        print("✅ Enhanced system is faster")
                    elif avg_enhanced > avg_legacy:
                        print("⚠️  Enhanced system is slower (expected due to stealth techniques)")
                    else:
                        print("➡️  Performance is similar")
                
            except ImportError:
                print("⚠️  Legacy system not available for comparison")
            
            self.test_results.append({
                'test': 'performance_comparison',
                'status': 'success',
                'enhanced_times': enhanced_times,
                'message': 'Performance comparison completed'
            })
            
        except Exception as e:
            print(f"❌ Performance comparison failed: {e}")
            self.test_results.append({
                'test': 'performance_comparison',
                'status': 'error',
                'message': f'Performance comparison failed: {e}'
            })
        
        print()
    
    def _generate_summary_report(self):
        """Generate summary report of all tests"""
        
        print("=" * 80)
        print("ENHANCED TRACKING SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.get('status') == 'success'])
        error_tests = len([r for r in self.test_results if r.get('status') == 'error'])
        exception_tests = len([r for r in self.test_results if r.get('status') == 'exception'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Errors: {error_tests}")
        print(f"Exceptions: {exception_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        print()
        
        # Detailed results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result.get('test', 'unknown')
            if test_type not in test_types:
                test_types[test_type] = {'success': 0, 'error': 0, 'exception': 0, 'unknown': 0}
            
            status = result.get('status', 'unknown')
            test_types[test_type][status] = test_types[test_type].get(status, 0) + 1
        
        print("Results by Test Type:")
        for test_type, counts in test_types.items():
            total = sum(counts.values())
            success_rate = (counts.get('success', 0) / total) * 100 if total > 0 else 0
            print(f"  {test_type}: {counts} ({success_rate:.1f}% success)")
        
        print()
        
        # Tracking-specific results
        estes_results = [r for r in self.test_results if r.get('test') == 'enhanced_estes_tracking']
        fedex_results = [r for r in self.test_results if r.get('test') == 'enhanced_fedex_tracking']
        
        if estes_results:
            estes_success = len([r for r in estes_results if r.get('status') == 'success'])
            estes_total = len(estes_results)
            print(f"Enhanced Estes Express: {estes_success}/{estes_total} ({(estes_success/estes_total)*100:.1f}% success)")
        
        if fedex_results:
            fedex_success = len([r for r in fedex_results if r.get('status') == 'success'])
            fedex_total = len(fedex_results)
            print(f"Enhanced FedEx Freight: {fedex_success}/{fedex_total} ({(fedex_success/fedex_total)*100:.1f}% success)")
        
        print()
        print("=" * 80)
        print(f"Test completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Save detailed results to file
        self._save_detailed_results()
    
    def _save_detailed_results(self):
        """Save detailed test results to file"""
        
        try:
            import json
            
            with open('enhanced_tracking_test_results.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': self.test_results,
                    'summary': {
                        'total_tests': len(self.test_results),
                        'successful_tests': len([r for r in self.test_results if r.get('status') == 'success']),
                        'error_tests': len([r for r in self.test_results if r.get('status') == 'error']),
                        'exception_tests': len([r for r in self.test_results if r.get('status') == 'exception'])
                    }
                }, f, indent=2)
            
            print("📄 Detailed results saved to: enhanced_tracking_test_results.json")
            
        except Exception as e:
            print(f"❌ Failed to save detailed results: {e}")

async def main():
    """Main test function"""
    
    print("🚀 Starting Enhanced Tracking System Test Suite...")
    print()
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required for async/await support")
        sys.exit(1)
    
    # Run tests
    test_suite = EnhancedTrackingSystemTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 