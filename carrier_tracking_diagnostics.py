#!/usr/bin/env python3
"""
Carrier Tracking Diagnostics and Enhancement Tool

This tool diagnoses and resolves specific tracking issues with Estes, FedEx, and Peninsula.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, List, Any
from datetime import datetime

# Import your tracking components
sys.path.append('src')
from backend.enhanced_ltl_tracking_client import EnhancedLTLTrackingClient
from backend.zero_cost_carriers import ZeroCostCarrierManager
from backend.zero_cost_anti_scraping import ZeroCostAntiScrapingSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CarrierTrackingDiagnostics:
    """Comprehensive diagnostics for carrier tracking issues"""
    
    def __init__(self):
        self.enhanced_client = EnhancedLTLTrackingClient()
        self.zero_cost_manager = ZeroCostCarrierManager()
        self.anti_scraping = ZeroCostAntiScrapingSystem()
        
    async def run_comprehensive_diagnostics(self):
        """Run complete diagnostic suite"""
        print("🔍 Starting Comprehensive Carrier Tracking Diagnostics\n")
        
        # Test PRO numbers from your data
        test_cases = [
            {'pro': '0628143046', 'carrier': 'Estes Express'},
            {'pro': '1751027634', 'carrier': 'FedEx Freight Economy'},
            {'pro': '4012381741', 'carrier': 'FedEx Freight Priority'},
            {'pro': '536246546', 'carrier': 'Peninsula Truck Lines Inc'},
            {'pro': '536246554', 'carrier': 'Peninsula Truck Lines Inc'}
        ]
        
        results = {}
        
        for test_case in test_cases:
            pro = test_case['pro']
            carrier = test_case['carrier']
            
            print(f"🚛 Testing {carrier} PRO: {pro}")
            print("-" * 50)
            
            # Run diagnostic for this PRO
            result = await self.diagnose_pro_tracking(pro, carrier)
            results[pro] = result
            
            # Display results
            self.display_diagnostic_result(pro, carrier, result)
            print("\n")
        
        # Generate summary report
        self.generate_summary_report(results)
        
        # Provide specific recommendations
        self.provide_recommendations(results)
        
    async def diagnose_pro_tracking(self, pro_number: str, carrier: str) -> Dict[str, Any]:
        """Diagnose tracking issues for a specific PRO"""
        diagnosis = {
            'pro_number': pro_number,
            'carrier': carrier,
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'issues_found': [],
            'recommendations': []
        }
        
        # Test 1: Enhanced Client
        print("  ✓ Testing Enhanced LTL Client...")
        try:
            enhanced_result = await self.enhanced_client.track_shipment(pro_number, carrier)
            diagnosis['tests']['enhanced_client'] = {
                'status': enhanced_result.get('status'),
                'message': enhanced_result.get('message'),
                'method': enhanced_result.get('tracking_method'),
                'success': enhanced_result.get('status') == 'success'
            }
        except Exception as e:
            diagnosis['tests']['enhanced_client'] = {
                'status': 'error',
                'message': str(e),
                'success': False
            }
        
        # Test 2: Zero-Cost Direct
        print("  ✓ Testing Zero-Cost Direct Access...")
        try:
            zero_cost_result = await self.zero_cost_manager.track_shipment(carrier, pro_number)
            diagnosis['tests']['zero_cost_direct'] = {
                'status': zero_cost_result.get('status'),
                'message': zero_cost_result.get('message'),
                'success': zero_cost_result.get('status') == 'success'
            }
        except Exception as e:
            diagnosis['tests']['zero_cost_direct'] = {
                'status': 'error',
                'message': str(e),
                'success': False
            }
        
        # Test 3: Anti-Scraping System Status
        print("  ✓ Testing Anti-Scraping System...")
        diagnosis['tests']['anti_scraping'] = self.test_anti_scraping_system()
        
        # Test 4: Carrier-Specific Tests
        print("  ✓ Running Carrier-Specific Tests...")
        if 'estes' in carrier.lower():
            diagnosis['tests']['carrier_specific'] = await self.test_estes_specific(pro_number)
        elif 'fedex' in carrier.lower():
            diagnosis['tests']['carrier_specific'] = await self.test_fedex_specific(pro_number)
        elif 'peninsula' in carrier.lower():
            diagnosis['tests']['carrier_specific'] = await self.test_peninsula_specific(pro_number)
        
        # Analyze results and identify issues
        self.analyze_test_results(diagnosis)
        
        return diagnosis
    
    def test_anti_scraping_system(self) -> Dict[str, Any]:
        """Test anti-scraping system capabilities"""
        status = {
            'pyppeteer_available': False,
            'requests_html_available': False,
            'captcha_solving_available': False,
            'tor_available': False,
            'session_creation': False
        }
        
        try:
            import pyppeteer
            status['pyppeteer_available'] = True
        except ImportError:
            pass
        
        try:
            from requests_html import HTMLSession
            status['requests_html_available'] = True
        except ImportError:
            pass
        
        try:
            import pytesseract
            import cv2
            status['captcha_solving_available'] = True
        except ImportError:
            pass
        
        try:
            import stem
            status['tor_available'] = True
        except ImportError:
            pass
        
        try:
            session = self.anti_scraping.create_stealth_session("test")
            status['session_creation'] = session is not None
        except Exception:
            pass
        
        return status
    
    async def test_estes_specific(self, pro_number: str) -> Dict[str, Any]:
        """Test Estes-specific tracking issues"""
        estes_test = {
            'javascript_rendering': False,
            'api_endpoints_accessible': False,
            'mobile_version_accessible': False,
            'specific_issues': []
        }
        
        # Test JavaScript rendering capability
        try:
            html_content = await self.anti_scraping.render_javascript_page(
                f"https://www.estes-express.com/shipment-tracking?pro={pro_number}"
            )
            estes_test['javascript_rendering'] = html_content is not None
            if not html_content:
                estes_test['specific_issues'].append("JavaScript rendering failed - Estes requires JS execution")
        except Exception as e:
            estes_test['specific_issues'].append(f"JavaScript rendering error: {str(e)}")
        
        # Test API endpoint accessibility
        try:
            session = self.anti_scraping.create_stealth_session("estes")
            response = session.get("https://www.estes-express.com/api/shipment-tracking/track/" + pro_number, timeout=10)
            estes_test['api_endpoints_accessible'] = response.status_code in [200, 404, 405]
        except Exception as e:
            estes_test['specific_issues'].append(f"API endpoint test failed: {str(e)}")
        
        return estes_test
    
    async def test_fedex_specific(self, pro_number: str) -> Dict[str, Any]:
        """Test FedEx-specific tracking issues"""
        fedex_test = {
            'tracking_api_accessible': False,
            'mobile_api_accessible': False,
            'graphql_accessible': False,
            'specific_issues': []
        }
        
        # Test main tracking API
        try:
            session = self.anti_scraping.create_stealth_session("fedex")
            response = session.get(f"https://www.fedex.com/trackingCal/track", timeout=10)
            fedex_test['tracking_api_accessible'] = response.status_code in [200, 400, 405]
        except Exception as e:
            fedex_test['specific_issues'].append(f"Main API test failed: {str(e)}")
        
        # Test mobile API
        try:
            mobile_headers = {'User-Agent': 'FedEx/8.2.1 (iPhone; iOS 17.5; Scale/3.00)'}
            session.headers.update(mobile_headers)
            response = session.get(f"https://mobile.fedex.com/api/track/{pro_number}", timeout=10)
            fedex_test['mobile_api_accessible'] = response.status_code in [200, 404, 405]
        except Exception as e:
            fedex_test['specific_issues'].append(f"Mobile API test failed: {str(e)}")
        
        return fedex_test
    
    async def test_peninsula_specific(self, pro_number: str) -> Dict[str, Any]:
        """Test Peninsula-specific tracking issues"""
        peninsula_test = {
            'main_site_accessible': False,
            'tracking_page_accessible': False,
            'requires_authentication': False,
            'specific_issues': []
        }
        
        # Test main site
        try:
            session = self.anti_scraping.create_stealth_session("peninsula")
            response = session.get("https://www.peninsulatrucklines.com", timeout=10)
            peninsula_test['main_site_accessible'] = response.status_code == 200
        except Exception as e:
            peninsula_test['specific_issues'].append(f"Main site test failed: {str(e)}")
        
        # Test tracking page
        try:
            response = session.get("https://www.peninsulatrucklines.com/tracking", timeout=10)
            peninsula_test['tracking_page_accessible'] = response.status_code == 200
            
            # Check for authentication requirements
            if 'login' in response.text.lower() or 'signin' in response.text.lower():
                peninsula_test['requires_authentication'] = True
                peninsula_test['specific_issues'].append("Peninsula requires customer login for tracking")
        except Exception as e:
            peninsula_test['specific_issues'].append(f"Tracking page test failed: {str(e)}")
        
        return peninsula_test
    
    def analyze_test_results(self, diagnosis: Dict[str, Any]):
        """Analyze test results and identify issues"""
        issues = []
        recommendations = []
        
        # Check enhanced client results
        enhanced_test = diagnosis['tests'].get('enhanced_client', {})
        if not enhanced_test.get('success'):
            issues.append(f"Enhanced client failed: {enhanced_test.get('message')}")
        
        # Check zero-cost results
        zero_cost_test = diagnosis['tests'].get('zero_cost_direct', {})
        if not zero_cost_test.get('success'):
            issues.append(f"Zero-cost tracking failed: {zero_cost_test.get('message')}")
        
        # Check anti-scraping system
        anti_scraping_test = diagnosis['tests'].get('anti_scraping', {})
        if not anti_scraping_test.get('pyppeteer_available'):
            issues.append("Pyppeteer not available - JavaScript rendering limited")
            recommendations.append("Install pyppeteer: pip3 install pyppeteer")
        
        if not anti_scraping_test.get('captcha_solving_available'):
            issues.append("CAPTCHA solving not available")
            recommendations.append("Install OpenCV and Tesseract: pip3 install opencv-python pytesseract")
        
        # Carrier-specific analysis
        carrier_test = diagnosis['tests'].get('carrier_specific', {})
        if carrier_test:
            issues.extend(carrier_test.get('specific_issues', []))
        
        diagnosis['issues_found'] = issues
        diagnosis['recommendations'] = recommendations
    
    def display_diagnostic_result(self, pro_number: str, carrier: str, diagnosis: Dict[str, Any]):
        """Display diagnostic results"""
        print(f"  📊 Results for {carrier} PRO {pro_number}:")
        
        # Enhanced client test
        enhanced_test = diagnosis['tests'].get('enhanced_client', {})
        status_icon = "✅" if enhanced_test.get('success') else "❌"
        print(f"    {status_icon} Enhanced Client: {enhanced_test.get('status')} - {enhanced_test.get('message', 'N/A')}")
        
        # Zero-cost test
        zero_cost_test = diagnosis['tests'].get('zero_cost_direct', {})
        status_icon = "✅" if zero_cost_test.get('success') else "❌"
        print(f"    {status_icon} Zero-Cost Direct: {zero_cost_test.get('status')} - {zero_cost_test.get('message', 'N/A')}")
        
        # Issues found
        if diagnosis['issues_found']:
            print("    🚨 Issues Found:")
            for issue in diagnosis['issues_found']:
                print(f"      • {issue}")
        
        # Recommendations
        if diagnosis['recommendations']:
            print("    💡 Recommendations:")
            for rec in diagnosis['recommendations']:
                print(f"      • {rec}")
    
    def generate_summary_report(self, results: Dict[str, Any]):
        """Generate summary report"""
        print("=" * 70)
        print("📋 SUMMARY REPORT")
        print("=" * 70)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() 
                             if r['tests'].get('enhanced_client', {}).get('success'))
        
        print(f"Total PRO numbers tested: {total_tests}")
        print(f"Successful tracking: {successful_tests}")
        print(f"Failed tracking: {total_tests - successful_tests}")
        print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Carrier breakdown
        carrier_stats = {}
        for result in results.values():
            carrier = result['carrier']
            if carrier not in carrier_stats:
                carrier_stats[carrier] = {'total': 0, 'success': 0}
            carrier_stats[carrier]['total'] += 1
            if result['tests'].get('enhanced_client', {}).get('success'):
                carrier_stats[carrier]['success'] += 1
        
        print("\n📊 Carrier Performance:")
        for carrier, stats in carrier_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100
            print(f"  {carrier}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    def provide_recommendations(self, results: Dict[str, Any]):
        """Provide specific recommendations"""
        print("\n💡 SPECIFIC RECOMMENDATIONS")
        print("=" * 70)
        
        # Collect all unique recommendations
        all_recommendations = set()
        for result in results.values():
            all_recommendations.update(result.get('recommendations', []))
        
        if all_recommendations:
            for i, rec in enumerate(sorted(all_recommendations), 1):
                print(f"{i}. {rec}")
        else:
            print("No specific recommendations at this time.")
        
        print("\n🔧 GENERAL RECOMMENDATIONS:")
        print("1. Ensure all dependencies are installed: pip3 install -r requirements_zero_cost.txt")
        print("2. For Estes: JavaScript rendering is critical - ensure browser dependencies work")
        print("3. For FedEx: Consider using official FedEx Developer API for reliable access")
        print("4. For Peninsula: Authentication requirements are correctly detected")
        print("5. Monitor carrier websites for structural changes that may affect tracking")

async def main():
    """Main diagnostic function"""
    diagnostics = CarrierTrackingDiagnostics()
    await diagnostics.run_comprehensive_diagnostics()

if __name__ == "__main__":
    asyncio.run(main()) 