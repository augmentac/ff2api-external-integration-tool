#!/usr/bin/env python3
"""
Troubleshoot Production Deployment
Comprehensive diagnosis of why enhanced tracking isn't working in production
"""

import requests
import time
import json
from datetime import datetime

def diagnose_production_issue():
    """Diagnose why enhanced tracking isn't working in production"""
    
    print("🔍 TROUBLESHOOTING PRODUCTION DEPLOYMENT")
    print("=" * 60)
    
    # Production app URL
    prod_url = "https://ff2api-external-integration-tool.streamlit.app/"
    
    print(f"🌐 Production URL: {prod_url}")
    print(f"⏰ Diagnosis started at: {datetime.now()}")
    print("-" * 60)
    
    # Step 1: Check if app is accessible
    print("\n🔍 Step 1: Checking app accessibility...")
    try:
        response = requests.get(prod_url, timeout=30)
        if response.status_code == 200:
            print("✅ Production app is accessible")
            print(f"📄 Response size: {len(response.text)} characters")
        else:
            print(f"❌ Production app returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing production app: {str(e)}")
        return False
    
    # Step 2: Check for enhanced tracking code
    print("\n🔍 Step 2: Checking for enhanced tracking code...")
    content = response.text
    
    # Look for specific enhanced tracking indicators
    enhanced_indicators = [
        "Extended wait conditions",
        "Smart result detection",
        "Angular Material table",
        "Progressive retry logic",
        "Enhanced wait conditions",
        "wait_for_tracking_data",
        "wait_for_ajax_completion",
        "parse_tracking_results"
    ]
    
    indicators_found = []
    for indicator in enhanced_indicators:
        if indicator in content:
            indicators_found.append(indicator)
    
    if indicators_found:
        print(f"✅ Found {len(indicators_found)} enhanced tracking indicators:")
        for indicator in indicators_found:
            print(f"  - {indicator}")
    else:
        print("❌ No enhanced tracking indicators found")
        print("🔧 This suggests the deployment hasn't taken effect yet")
    
    # Step 3: Check GitHub repository status
    print("\n🔍 Step 3: Checking GitHub repository status...")
    try:
        github_api_url = "https://api.github.com/repos/augmentac/ff2api-external-integration-tool/commits/main"
        github_response = requests.get(github_api_url, timeout=10)
        
        if github_response.status_code == 200:
            commit_data = github_response.json()
            latest_commit = commit_data['sha'][:7]
            commit_message = commit_data['commit']['message']
            commit_date = commit_data['commit']['author']['date']
            
            print(f"✅ Latest commit: {latest_commit}")
            print(f"📝 Message: {commit_message[:100]}...")
            print(f"📅 Date: {commit_date}")
            
            # Check if it's our enhanced tracking commit
            if "Enhanced tracking" in commit_message or "BREAKTHROUGH" in commit_message:
                print("✅ Enhanced tracking commit is the latest")
            else:
                print("⚠️ Latest commit doesn't appear to be enhanced tracking")
        else:
            print(f"❌ GitHub API returned status: {github_response.status_code}")
    except Exception as e:
        print(f"❌ Error checking GitHub: {str(e)}")
    
    # Step 4: Test local vs production behavior
    print("\n🔍 Step 4: Comparing local vs production behavior...")
    
    # Create a test to see what's actually happening
    test_pro = "0628143046"
    print(f"📦 Testing PRO: {test_pro}")
    
    # Test locally first
    print("\n🏠 Testing locally...")
    try:
        import asyncio
        from src.backend.apple_silicon_estes_client import AppleSiliconEstesClient
        
        async def test_local():
            client = AppleSiliconEstesClient()
            result = await client.track_shipment(test_pro)
            return result
        
        local_result = asyncio.run(test_local())
        print(f"✅ Local result: Success={local_result.get('success')}, Status={local_result.get('status')}")
        
        if local_result.get('success'):
            print("✅ Local enhanced tracking is working")
        else:
            print("❌ Local enhanced tracking failed")
            
    except Exception as e:
        print(f"❌ Local test failed: {str(e)}")
    
    # Step 5: Check Streamlit Cloud deployment logs
    print("\n🔍 Step 5: Streamlit Cloud deployment analysis...")
    print("📋 Common issues and solutions:")
    print("1. 🕐 Deployment delay: Streamlit Cloud can take 5-15 minutes")
    print("2. 🔄 Cache issues: Old code may be cached")
    print("3. 📦 Dependencies: New packages may not be installed")
    print("4. 🔧 Configuration: Environment variables may be missing")
    
    # Step 6: Provide specific troubleshooting steps
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("=" * 60)
    
    if not indicators_found:
        print("❌ ISSUE: Enhanced tracking code not found in production")
        print("\n🔧 SOLUTIONS:")
        print("1. Wait 10-15 minutes for Streamlit Cloud deployment")
        print("2. Check Streamlit Cloud app logs for deployment errors")
        print("3. Verify all dependencies are in requirements.txt")
        print("4. Force restart the Streamlit Cloud app")
        print("5. Check if there are any import errors in the enhanced code")
        
        # Check for potential import issues
        print("\n🔍 Checking for potential import issues...")
        import_issues = [
            "from playwright.async_api import async_playwright",
            "from bs4 import BeautifulSoup",
            "import asyncio"
        ]
        
        for import_line in import_issues:
            if import_line in content:
                print(f"✅ Found: {import_line}")
            else:
                print(f"⚠️ Missing: {import_line}")
    
    else:
        print("✅ Enhanced tracking code found in production")
        print("❌ ISSUE: Code is deployed but not working properly")
        print("\n🔧 SOLUTIONS:")
        print("1. Check if browser automation is disabled in Streamlit Cloud")
        print("2. Verify ChromeDriver/Playwright work in cloud environment")
        print("3. Check for ARM64 vs x86 architecture issues")
        print("4. Test with headless=True for cloud deployment")
        print("5. Add more detailed logging to identify failure points")
    
    # Step 7: Create a simplified test
    print("\n🧪 CREATING SIMPLIFIED TEST...")
    create_simplified_test()
    
    return True

def create_simplified_test():
    """Create a simplified test to verify basic functionality"""
    
    test_content = '''#!/usr/bin/env python3
"""
Simplified Production Test
Tests basic functionality without complex browser automation
"""

import requests
import time

def test_basic_functionality():
    """Test basic functionality that should work in any environment"""
    
    print("🧪 Testing Basic Functionality")
    print("=" * 40)
    
    # Test 1: Basic imports
    try:
        from src.backend.apple_silicon_estes_client import AppleSiliconEstesClient
        print("✅ Import successful")
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False
    
    # Test 2: Class instantiation
    try:
        client = AppleSiliconEstesClient()
        print("✅ Class instantiation successful")
    except Exception as e:
        print(f"❌ Class instantiation failed: {str(e)}")
        return False
    
    # Test 3: Basic parsing logic
    try:
        test_html = """
        <html>
        <body>
        <div>0628143046</div>
        <div>Delivered</div>
        <div>MASON, OH</div>
        </body>
        </html>
        """
        
        result = client.parse_tracking_results(test_html, "0628143046")
        print(f"✅ Parsing test: Success={result.get('success')}")
        return True
        
    except Exception as e:
        print(f"❌ Parsing test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_basic_functionality()
'''
    
    with open("simplified_production_test.py", "w") as f:
        f.write(test_content)
    
    print("📄 Created simplified_production_test.py")
    print("🔧 Run this test to verify basic functionality")

if __name__ == "__main__":
    diagnose_production_issue() 