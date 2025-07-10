#!/usr/bin/env python3
"""
Monitor Production Deployment of JavaScript Validation Fixes

This script monitors the production Streamlit Cloud app to detect when
the JavaScript validation fixes have been successfully deployed.
"""

import time
import asyncio
import requests
from datetime import datetime
from src.backend.barrier_breaking_tracking_system import BarrierBreakingTrackingSystem

def check_app_status():
    """Check if the production app is accessible"""
    try:
        response = requests.get("https://ff2api-external-integration-tool.streamlit.app/_stcore/health", timeout=10)
        return response.status_code == 200
    except:
        return False

async def test_javascript_validation():
    """Test if JavaScript validation fixes are working"""
    try:
        system = BarrierBreakingTrackingSystem()
        result = await system.track_single_shipment('0628143046')
        
        # Check if we get JavaScript code (OLD VERSION)
        status = result.get('status', '')
        if 'gtm.js' in str(status):
            return False, "OLD VERSION - Still returning JavaScript code"
        
        # Check if we get proper error (NEW VERSION)
        if result.get('success') == False:
            error_msg = result.get('error', '')
            if 'JavaScript code instead of tracking data' in error_msg or 'All tracking methods failed' in error_msg:
                return True, "NEW VERSION - JavaScript validation working"
            else:
                return False, f"UNKNOWN - Different error: {error_msg}"
        
        return False, "UNEXPECTED - Got success result"
        
    except Exception as e:
        return False, f"ERROR - {str(e)}"

async def monitor_deployment():
    """Monitor deployment status"""
    print("🔍 Monitoring Production Deployment of JavaScript Validation Fixes")
    print("=" * 70)
    print(f"Production App: https://ff2api-external-integration-tool.streamlit.app/")
    print(f"Started monitoring at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_count = 0
    max_checks = 30  # Monitor for 15 minutes (30 checks * 30 seconds)
    
    while check_count < max_checks:
        check_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"🔄 Check #{check_count} at {timestamp}")
        
        # Check app accessibility
        if not check_app_status():
            print("   ❌ App not accessible")
            time.sleep(30)
            continue
        
        print("   ✅ App is accessible")
        
        # Test JavaScript validation
        is_fixed, message = await test_javascript_validation()
        
        if is_fixed:
            print(f"   🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"   ✅ {message}")
            print()
            print("=" * 70)
            print("🚀 PRODUCTION DEPLOYMENT COMPLETE!")
            print("The JavaScript validation fixes are now live in production.")
            print("Users will now see honest error messages instead of JavaScript code.")
            return True
        else:
            print(f"   ⏳ {message}")
        
        print(f"   💤 Waiting 30 seconds before next check...")
        print()
        
        if check_count < max_checks:
            time.sleep(30)
    
    print("⏰ Monitoring timeout reached")
    print("The deployment may take longer than expected.")
    return False

if __name__ == "__main__":
    asyncio.run(monitor_deployment()) 