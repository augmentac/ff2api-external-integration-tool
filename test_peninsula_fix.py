#!/usr/bin/env python3
"""
Test Peninsula Tracking Fix

This script tests the corrected Peninsula tracking implementation to ensure
it properly extracts the publicly available tracking information without login.
"""

import asyncio
import sys
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import tracking components
sys.path.append('src')
from backend.enhanced_ltl_tracking_client import EnhancedLTLTrackingClient
from backend.zero_cost_carriers import ZeroCostCarrierManager, PeninsulaZeroCostTracker
from backend.zero_cost_anti_scraping import ZeroCostAntiScrapingSystem

async def test_peninsula_tracking():
    """Test Peninsula tracking with the corrected implementation"""
    print("🧪 Testing Peninsula Tracking Fix")
    print("=" * 50)
    
    # Test PRO numbers from your data
    test_pros = [
        '536246546',  # The one shown in the screenshot
        '536246554',  # Another Peninsula PRO
        '537313956'   # Third Peninsula PRO
    ]
    
    # Initialize tracking components
    enhanced_client = EnhancedLTLTrackingClient()
    zero_cost_manager = ZeroCostCarrierManager()
    anti_scraping = ZeroCostAntiScrapingSystem()
    peninsula_tracker = PeninsulaZeroCostTracker(anti_scraping)
    
    results = []
    
    for pro_number in test_pros:
        print(f"\n🚛 Testing Peninsula PRO: {pro_number}")
        print("-" * 30)
        
        # Test 1: Direct Peninsula tracker
        print("  ✓ Testing Direct Peninsula Tracker...")
        try:
            direct_result = await peninsula_tracker.track_pro(pro_number)
            print(f"    Direct Result: {direct_result.get('status')} - {direct_result.get('message', 'N/A')}")
            
            if direct_result.get('status') == 'success':
                print(f"    ✅ SUCCESS: {direct_result.get('tracking_status', 'N/A')}")
                print(f"    📍 Event: {direct_result.get('tracking_event', 'N/A')}")
                results.append(f"✅ Direct Peninsula PRO {pro_number}: SUCCESS")
            else:
                print(f"    ❌ FAILED: {direct_result.get('message', 'Unknown error')}")
                results.append(f"❌ Direct Peninsula PRO {pro_number}: FAILED")
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
            results.append(f"❌ Direct Peninsula PRO {pro_number}: ERROR")
        
        # Test 2: Enhanced client
        print("  ✓ Testing Enhanced Client...")
        try:
            enhanced_result = await enhanced_client.track_shipment(pro_number, 'Peninsula Truck Lines Inc')
            print(f"    Enhanced Result: {enhanced_result.get('status')} - {enhanced_result.get('message', 'N/A')}")
            
            if enhanced_result.get('status') == 'success':
                print(f"    ✅ SUCCESS: Enhanced client working")
                results.append(f"✅ Enhanced Peninsula PRO {pro_number}: SUCCESS")
            else:
                print(f"    ⚠️  PARTIAL: {enhanced_result.get('message', 'Unknown status')}")
                results.append(f"⚠️  Enhanced Peninsula PRO {pro_number}: PARTIAL")
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
            results.append(f"❌ Enhanced Peninsula PRO {pro_number}: ERROR")
        
        # Test 3: Zero-cost manager
        print("  ✓ Testing Zero-Cost Manager...")
        try:
            zero_cost_result = await zero_cost_manager.track_shipment('Peninsula Truck Lines Inc', pro_number)
            print(f"    Zero-Cost Result: {zero_cost_result.get('status')} - {zero_cost_result.get('message', 'N/A')}")
            
            if zero_cost_result.get('status') == 'success':
                print(f"    ✅ SUCCESS: Zero-cost manager working")
                results.append(f"✅ Zero-Cost Peninsula PRO {pro_number}: SUCCESS")
            else:
                print(f"    ⚠️  PARTIAL: {zero_cost_result.get('message', 'Unknown status')}")
                results.append(f"⚠️  Zero-Cost Peninsula PRO {pro_number}: PARTIAL")
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
            results.append(f"❌ Zero-Cost Peninsula PRO {pro_number}: ERROR")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 PENINSULA TRACKING TEST RESULTS")
    print("=" * 50)
    
    for result in results:
        print(f"  {result}")
    
    # Count successes
    successes = len([r for r in results if "SUCCESS" in r])
    total_tests = len(results)
    
    print(f"\n🎯 Overall Success Rate: {successes}/{total_tests} ({(successes/total_tests)*100:.1f}%)")
    
    if successes > 0:
        print("✅ Peninsula tracking fix is working!")
        print("🎉 The system can now extract publicly available tracking data without login.")
    else:
        print("❌ Peninsula tracking fix needs more work.")
        print("🔧 Additional debugging may be required.")
    
    # Cleanup
    enhanced_client.cleanup()
    zero_cost_manager.cleanup()

async def test_peninsula_html_extraction():
    """Test Peninsula HTML extraction with sample data"""
    print("\n🧪 Testing Peninsula HTML Extraction Logic")
    print("=" * 50)
    
    # Sample HTML content based on the screenshot
    sample_html = """
    <html>
    <body>
        <div class="warning">You are not logged in. Please login to view parties to the shipment.</div>
        <div class="shipment-info">
            <h2>Shipment Status Information</h2>
            <table>
                <tr><td>Pro Number</td><td>536246546</td></tr>
                <tr><td>Pro Date</td><td>06/26/2025</td></tr>
                <tr><td>PO Number</td><td>1212110508</td></tr>
                <tr><td>Shipment Status</td><td>DELIVERED TO SHANE ON 2025-07-01</td></tr>
            </table>
        </div>
        <div class="shipment-log">
            <h2>Shipment Log</h2>
            <table>
                <tr><td>06/26/2025</td><td>04:04pm</td><td>PICKUP</td><td>PORTLAND</td></tr>
                <tr><td>06/26/2025</td><td>06:37pm</td><td>LINE MFST</td><td>PORTLAND</td></tr>
                <tr><td>06/30/2025</td><td>02:43am</td><td>ASG ROUTE</td><td>BREMEN</td></tr>
                <tr><td>06/30/2025</td><td>05:16am</td><td>DEL MFST</td><td>BREMEN</td></tr>
                <tr><td>06/30/2025</td><td>03:41pm</td><td>Not Delivered</td><td>BREMEN</td></tr>
                <tr><td>07/01/2025</td><td>12:12pm</td><td>DOCK MFST</td><td>BREMEN</td></tr>
                <tr><td>07/01/2025</td><td>02:14pm</td><td>Delivered</td><td>PORT ANGELES</td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    
    # Test HTML extraction
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Initialize Peninsula tracker
    anti_scraping = ZeroCostAntiScrapingSystem()
    peninsula_tracker = PeninsulaZeroCostTracker(anti_scraping)
    
    # Test extraction
    result = peninsula_tracker._extract_from_html(soup, '536246546')
    
    if result:
        print("✅ HTML Extraction Test: SUCCESS")
        print(f"  Status: {result.get('status')}")
        print(f"  Tracking Status: {result.get('tracking_status')}")
        print(f"  Tracking Event: {result.get('tracking_event')}")
        print(f"  Notes: {result.get('notes')}")
    else:
        print("❌ HTML Extraction Test: FAILED")
        print("  No tracking information extracted from sample HTML")

async def main():
    """Main test function"""
    print("🔧 PENINSULA TRACKING FIX VERIFICATION")
    print("=" * 60)
    print("This script tests the corrected Peninsula tracking implementation.")
    print("Expected: Extract publicly available tracking data without login.")
    print("=" * 60)
    
    # Test HTML extraction logic first
    await test_peninsula_html_extraction()
    
    # Test live Peninsula tracking
    await test_peninsula_tracking()
    
    print("\n🎉 Peninsula tracking fix verification complete!")

if __name__ == "__main__":
    asyncio.run(main()) 