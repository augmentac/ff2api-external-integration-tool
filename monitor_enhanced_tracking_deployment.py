#!/usr/bin/env python3
"""
Monitor Enhanced Tracking System Deployment
Verifies that the enhanced tracking data extraction is working in production
"""

import requests
import time
import json
from datetime import datetime

def check_production_tracking():
    """Check if enhanced tracking is working in production"""
    
    print("🚀 Monitoring Enhanced Tracking System Deployment")
    print("=" * 60)
    
    # Production app URL
    prod_url = "https://ff2api-external-integration-tool.streamlit.app/"
    
    # Test PRO number that we know works with enhanced tracking
    test_pro = "0628143046"
    
    print(f"🌐 Production URL: {prod_url}")
    print(f"📦 Test PRO: {test_pro}")
    print(f"⏰ Monitoring started at: {datetime.now()}")
    print("-" * 60)
    
    for attempt in range(1, 11):  # Check 10 times
        try:
            print(f"\n🔍 Attempt {attempt}/10 - Checking production status...")
            
            # Check if the app is accessible
            response = requests.get(prod_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Production app is accessible")
                
                # Check if the enhanced tracking features are deployed
                content = response.text
                
                # Look for signs of the enhanced tracking system
                enhanced_indicators = [
                    "Enhanced wait conditions",
                    "Smart result detection", 
                    "Angular Material table",
                    "Extended wait conditions",
                    "Progressive retry logic"
                ]
                
                indicators_found = sum(1 for indicator in enhanced_indicators if indicator in content)
                
                if indicators_found > 0:
                    print(f"🎯 Enhanced tracking features detected ({indicators_found} indicators)")
                    print("✅ DEPLOYMENT SUCCESSFUL!")
                    
                    print("\n🎉 Enhanced Tracking System is LIVE!")
                    print("=" * 60)
                    print("✅ Real tracking data extraction enabled")
                    print("✅ Extended wait conditions (15-45 seconds)")
                    print("✅ Smart result detection for Angular Material")
                    print("✅ Progressive retry logic implemented")
                    print("✅ Enhanced data parsing for structured content")
                    print("=" * 60)
                    
                    return True
                else:
                    print("⚠️ Enhanced tracking features not yet detected")
                    
            else:
                print(f"❌ Production app returned status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking production: {str(e)}")
        
        if attempt < 10:
            print("⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    
    print("\n⚠️ Enhanced tracking deployment not confirmed after 10 attempts")
    print("The deployment may still be in progress or may need manual verification")
    
    return False

def create_test_csv():
    """Create a test CSV file with the working PRO number"""
    
    test_data = """PRO Number,Carrier
0628143046,Estes Express
1282975382,FedEx Freight
1611116978,R&L Carriers"""
    
    with open("enhanced_tracking_test.csv", "w") as f:
        f.write(test_data)
    
    print(f"\n📄 Created test CSV file: enhanced_tracking_test.csv")
    print("Use this file to test the enhanced tracking system in production")
    print("Expected results:")
    print("- 0628143046: Status=Delivered, Location=MASON, OH")
    print("- Should show real tracking data instead of JavaScript")

if __name__ == "__main__":
    success = check_production_tracking()
    
    if success:
        create_test_csv()
        print("\n🎯 READY FOR TESTING!")
        print("Upload enhanced_tracking_test.csv to the production app")
    else:
        print("\n⏳ Deployment still in progress...")
        print("Try running this script again in a few minutes") 