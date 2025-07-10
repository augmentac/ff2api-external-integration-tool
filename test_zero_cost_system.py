#!/usr/bin/env python3
"""
Test Zero-Cost Anti-Scraping System

Comprehensive test for the zero-cost LTL tracking system with Peninsula PRO 536246546.
Tests all components including TOR rotation, CAPTCHA solving, and JavaScript rendering.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import zero-cost system components
try:
    from src.backend.enhanced_ltl_tracking_client import EnhancedLTLTrackingClient
    from src.backend.zero_cost_anti_scraping import ZeroCostAntiScrapingSystem
    from src.backend.zero_cost_carriers import ZeroCostCarrierManager
    ZERO_COST_AVAILABLE = True
except ImportError as e:
    logger.error(f"Zero-cost system not available: {e}")
    ZERO_COST_AVAILABLE = False


class ZeroCostSystemTester:
    """Test suite for zero-cost anti-scraping system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all zero-cost system tests"""
        self.logger.info("=" * 60)
        self.logger.info("ZERO-COST ANTI-SCRAPING SYSTEM TEST")
        self.logger.info("=" * 60)
        
        if not ZERO_COST_AVAILABLE:
            return {
                'status': 'error',
                'message': 'Zero-cost system not available - check imports',
                'tests': {}
            }
        
        # Test Peninsula PRO 536246546 (user's test case)
        peninsula_result = await self.test_peninsula_tracking()
        self.test_results['peninsula_536246546'] = peninsula_result
        
        # Test system components
        component_results = await self.test_system_components()
        self.test_results.update(component_results)
        
        # Test enhanced client
        enhanced_client_result = await self.test_enhanced_client()
        self.test_results['enhanced_client'] = enhanced_client_result
        
        # Generate summary
        summary = self.generate_test_summary()
        
        return {
            'status': 'completed',
            'test_results': self.test_results,
            'summary': summary,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    async def test_peninsula_tracking(self) -> Dict[str, Any]:
        """Test Peninsula tracking with PRO 536246546"""
        self.logger.info("\n" + "=" * 40)
        self.logger.info("TESTING PENINSULA PRO 536246546")
        self.logger.info("=" * 40)
        
        try:
            # Initialize zero-cost carrier manager
            carrier_manager = ZeroCostCarrierManager()
            
            # Test Peninsula tracking
            self.logger.info("Testing Peninsula zero-cost tracking...")
            result = await carrier_manager.track_shipment('peninsula', '536246546')
            
            # Log result
            self.logger.info(f"Peninsula tracking result: {result}")
            
            # Check if we got expected delivery data
            expected_format = "07/01/2025 02:14pm Delivered PORT ANGELES, WA"
            
            if result.get('status') == 'success':
                delivery_status = result.get('delivery_status', '')
                if 'delivered' in delivery_status.lower() and 'port angeles' in delivery_status.lower():
                    self.logger.info("✅ SUCCESS: Peninsula tracking extracted expected delivery data!")
                    return {
                        'status': 'success',
                        'message': 'Peninsula tracking successful',
                        'delivery_data': delivery_status,
                        'extraction_method': result.get('extracted_from', 'unknown'),
                        'expected_format_match': expected_format in delivery_status
                    }
                else:
                    self.logger.info(f"⚠️  PARTIAL: Peninsula tracking worked but data format differs")
                    return {
                        'status': 'partial_success',
                        'message': 'Peninsula tracking worked but data format differs',
                        'delivery_data': delivery_status,
                        'extraction_method': result.get('extracted_from', 'unknown'),
                        'expected_format_match': False
                    }
            else:
                self.logger.info(f"❌ FAILED: Peninsula tracking failed - {result.get('message', 'Unknown error')}")
                return {
                    'status': 'failed',
                    'message': result.get('message', 'Peninsula tracking failed'),
                    'error_details': result
                }
                
        except Exception as e:
            self.logger.error(f"Peninsula test error: {e}")
            return {
                'status': 'error',
                'message': f'Peninsula test error: {str(e)}'
            }
        finally:
            try:
                carrier_manager.cleanup()
            except:
                pass
    
    async def test_system_components(self) -> Dict[str, Any]:
        """Test individual system components"""
        self.logger.info("\n" + "=" * 40)
        self.logger.info("TESTING SYSTEM COMPONENTS")
        self.logger.info("=" * 40)
        
        results = {}
        
        # Test anti-scraping system initialization
        try:
            self.logger.info("Testing anti-scraping system initialization...")
            anti_scraping = ZeroCostAntiScrapingSystem()
            
            # Test fingerprint generation
            fingerprint = anti_scraping.fingerprint_gen.generate_fingerprint()
            self.logger.info(f"Generated fingerprint: {fingerprint.user_agent[:50]}...")
            
            # Test session creation
            session = anti_scraping.create_stealth_session('peninsula')
            self.logger.info(f"Created stealth session with User-Agent: {session.headers.get('User-Agent', 'None')[:50]}...")
            
            results['anti_scraping_init'] = {
                'status': 'success',
                'message': 'Anti-scraping system initialized successfully',
                'fingerprint_generated': bool(fingerprint),
                'session_created': bool(session)
            }
            
        except Exception as e:
            self.logger.error(f"Anti-scraping system test failed: {e}")
            results['anti_scraping_init'] = {
                'status': 'error',
                'message': f'Anti-scraping system test failed: {str(e)}'
            }
        
        # Test TOR availability
        try:
            self.logger.info("Testing TOR availability...")
            tor_available = anti_scraping.tor_manager.session is not None
            
            if tor_available:
                current_ip = anti_scraping.tor_manager.get_current_ip()
                self.logger.info(f"TOR available - Current IP: {current_ip}")
                results['tor_system'] = {
                    'status': 'success',
                    'message': 'TOR system available',
                    'current_ip': current_ip
                }
            else:
                self.logger.info("TOR not available - will use regular requests")
                results['tor_system'] = {
                    'status': 'info',
                    'message': 'TOR not available - using regular requests'
                }
                
        except Exception as e:
            self.logger.error(f"TOR test failed: {e}")
            results['tor_system'] = {
                'status': 'error',
                'message': f'TOR test failed: {str(e)}'
            }
        
        # Test CAPTCHA solver
        try:
            self.logger.info("Testing CAPTCHA solver availability...")
            captcha_available = anti_scraping.captcha_solver is not None
            
            if captcha_available:
                self.logger.info("CAPTCHA solver available (computer vision)")
                results['captcha_solver'] = {
                    'status': 'success',
                    'message': 'Local CAPTCHA solver available'
                }
            else:
                self.logger.info("CAPTCHA solver not available")
                results['captcha_solver'] = {
                    'status': 'info',
                    'message': 'CAPTCHA solver not available'
                }
                
        except Exception as e:
            self.logger.error(f"CAPTCHA solver test failed: {e}")
            results['captcha_solver'] = {
                'status': 'error',
                'message': f'CAPTCHA solver test failed: {str(e)}'
            }
        
        # Test JavaScript rendering
        try:
            self.logger.info("Testing JavaScript rendering capabilities...")
            test_url = "https://httpbin.org/html"
            
            # Test with requests-html if available
            rendered_content = await anti_scraping.render_javascript_page(test_url)
            
            if rendered_content:
                self.logger.info("JavaScript rendering successful")
                results['javascript_rendering'] = {
                    'status': 'success',
                    'message': 'JavaScript rendering available',
                    'content_length': len(rendered_content)
                }
            else:
                self.logger.info("JavaScript rendering not available")
                results['javascript_rendering'] = {
                    'status': 'info',
                    'message': 'JavaScript rendering not available'
                }
                
        except Exception as e:
            self.logger.error(f"JavaScript rendering test failed: {e}")
            results['javascript_rendering'] = {
                'status': 'error',
                'message': f'JavaScript rendering test failed: {str(e)}'
            }
        
        return results
    
    async def test_enhanced_client(self) -> Dict[str, Any]:
        """Test enhanced LTL tracking client"""
        self.logger.info("\n" + "=" * 40)
        self.logger.info("TESTING ENHANCED CLIENT")
        self.logger.info("=" * 40)
        
        try:
            # Initialize enhanced client
            client = EnhancedLTLTrackingClient()
            
            # Test system statistics
            stats = client.get_tracking_statistics()
            self.logger.info(f"System statistics: {stats}")
            
            # Test Peninsula PRO with enhanced client
            self.logger.info("Testing Peninsula PRO 536246546 with enhanced client...")
            result = await client.track_shipment('536246546', 'Peninsula Truck Lines')
            
            # Test system configuration
            config_result = client.configure_system({
                'use_zero_cost_first': True,
                'fallback_to_legacy': True
            })
            
            self.logger.info(f"Enhanced client result: {result}")
            
            return {
                'status': 'success',
                'message': 'Enhanced client test completed',
                'tracking_result': result,
                'system_stats': stats,
                'configuration': config_result
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced client test failed: {e}")
            return {
                'status': 'error',
                'message': f'Enhanced client test failed: {str(e)}'
            }
        finally:
            try:
                client.cleanup()
            except:
                pass
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                             if isinstance(result, dict) and result.get('status') == 'success')
        
        # Check Peninsula specific result
        peninsula_result = self.test_results.get('peninsula_536246546', {})
        peninsula_success = peninsula_result.get('status') == 'success'
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': f"{(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
            'peninsula_tracking_success': peninsula_success,
            'peninsula_delivery_data': peninsula_result.get('delivery_data'),
            'expected_format_match': peninsula_result.get('expected_format_match', False),
            'system_ready': peninsula_success and successful_tests >= total_tests * 0.7
        }


async def main():
    """Main test function"""
    tester = ZeroCostSystemTester()
    
    try:
        # Run all tests
        results = await tester.run_all_tests()
        
        # Print results
        print("\n" + "=" * 60)
        print("ZERO-COST SYSTEM TEST RESULTS")
        print("=" * 60)
        
        summary = results.get('summary', {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Successful Tests: {summary.get('successful_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', '0%')}")
        print(f"Peninsula Tracking Success: {summary.get('peninsula_tracking_success', False)}")
        print(f"Expected Format Match: {summary.get('expected_format_match', False)}")
        print(f"System Ready: {summary.get('system_ready', False)}")
        
        if summary.get('peninsula_delivery_data'):
            print(f"Peninsula Delivery Data: {summary['peninsula_delivery_data']}")
        
        # Print detailed results
        print("\n" + "=" * 40)
        print("DETAILED TEST RESULTS")
        print("=" * 40)
        
        for test_name, result in results.get('test_results', {}).items():
            status = result.get('status', 'unknown') if isinstance(result, dict) else 'unknown'
            message = result.get('message', 'No message') if isinstance(result, dict) else str(result)
            print(f"{test_name}: {status.upper()} - {message}")
        
        # Exit with appropriate code
        if summary.get('peninsula_tracking_success', False):
            print("\n🎉 SUCCESS: Peninsula tracking working with zero-cost system!")
            sys.exit(0)
        else:
            print("\n❌ FAILED: Peninsula tracking not working as expected")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 TEST SUITE ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 