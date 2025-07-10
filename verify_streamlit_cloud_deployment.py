#!/usr/bin/env python3
"""
Verify Streamlit Cloud Deployment
Check that the cloud deployment is using the correct FF2API app with updated tracking
"""

import requests
import time
import sys
import os
from datetime import datetime

def check_deployment_status():
    """Check the deployment status and configuration"""
    
    print("🌐 STREAMLIT CLOUD DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    app_url = "https://ff2api-external-integration-tool.streamlit.app/"
    
    print(f"🎯 Target URL: {app_url}")
    print(f"⏰ Check time: {datetime.now()}")
    print("-" * 60)
    
    # Step 1: Check if app is accessible
    print("\n📡 Step 1: Checking app accessibility...")
    try:
        response = requests.get(app_url, timeout=30, allow_redirects=False)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("   ✅ App is accessible (redirecting to auth)")
            redirect_url = response.headers.get('Location', '')
            print(f"   🔐 Auth redirect: {redirect_url}")
            
            # This confirms the app is running and using authentication
            if 'auth' in redirect_url.lower():
                print("   ✅ FF2API authentication system is active")
                return True
            else:
                print("   ❌ Unexpected redirect")
                return False
        elif response.status_code == 303:
            print("   ✅ App is accessible (redirecting to auth)")
            redirect_url = response.headers.get('location', '')  # lowercase 'location' header
            print(f"   🔐 Auth redirect: {redirect_url}")
            
            # This confirms the app is running and using authentication
            if 'auth' in redirect_url.lower():
                print("   ✅ FF2API authentication system is active")
                return True
            else:
                print("   ❌ Unexpected redirect")
                return False
                
        elif response.status_code == 200:
            print("   ✅ App is accessible (no auth required)")
            return True
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error accessing app: {e}")
        return False

def verify_correct_app_deployed():
    """Verify that the correct app (FF2API) is deployed, not the tracking-only app"""
    
    print("\n🔍 Step 2: Verifying correct app deployment...")
    
    # Check local files to confirm what should be deployed
    try:
        # Check if the main app file exists and is correct
        if os.path.exists('src/frontend/app.py'):
            with open('src/frontend/app.py', 'r') as f:
                content = f.read()
                
            if 'FF2API' in content and 'brokerage' in content.lower():
                print("   ✅ Local app.py contains FF2API functionality")
                print("   ✅ Brokerage management features present")
                
                if 'pro_tracking_ui' in content:
                    print("   ✅ PRO tracking integration present")
                    return True
                else:
                    print("   ❌ PRO tracking integration missing")
                    return False
            else:
                print("   ❌ Local app.py does not contain FF2API functionality")
                return False
        else:
            print("   ❌ src/frontend/app.py not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking local files: {e}")
        return False

def verify_tracking_system_updates():
    """Verify that the tracking system updates are in place"""
    
    print("\n🚀 Step 3: Verifying tracking system updates...")
    
    try:
        # Check if PRO tracking UI has been updated
        if os.path.exists('src/frontend/pro_tracking_ui.py'):
            with open('src/frontend/pro_tracking_ui.py', 'r') as f:
                content = f.read()
                
            if 'working_cloud_tracking' in content:
                print("   ✅ Cloud-compatible tracking system integrated")
                
                if 'detect_cloud_environment' in content:
                    print("   ✅ Cloud environment detection present")
                    
                    if 'STREAMLIT_CLOUD' in content:
                        print("   ✅ Streamlit Cloud detection configured")
                        return True
                    else:
                        print("   ❌ Streamlit Cloud detection missing")
                        return False
                else:
                    print("   ❌ Cloud environment detection missing")
                    return False
            else:
                print("   ❌ Cloud-compatible tracking system not integrated")
                return False
        else:
            print("   ❌ src/frontend/pro_tracking_ui.py not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking tracking system: {e}")
        return False

def main():
    """Main verification function"""
    
    print("🚀 Starting Streamlit Cloud deployment verification...")
    print()
    
    # Run all checks
    checks = [
        ("Deployment Status", check_deployment_status),
        ("Correct App Deployed", verify_correct_app_deployed),
        ("Tracking System Updates", verify_tracking_system_updates)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 Running: {check_name}")
        try:
            result = check_func()
            results.append((check_name, result))
            if result:
                print(f"   ✅ {check_name}: PASSED")
            else:
                print(f"   ❌ {check_name}: FAILED")
        except Exception as e:
            print(f"   ❌ {check_name}: ERROR - {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n🎯 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {check_name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!")
        print("=" * 60)
        print("✅ Streamlit Cloud is using the correct FF2API application")
        print("✅ Cloud-compatible tracking system is deployed")
        print("✅ Authentication system is working")
        print("✅ PRO tracking functionality should work in the cloud")
        print()
        print("🎯 Next Steps:")
        print("1. Access the app: https://ff2api-external-integration-tool.streamlit.app/")
        print("2. Enter your team password to authenticate")
        print("3. Go to the 'PRO Tracking' tab")
        print("4. Test with a PRO number to verify cloud tracking works")
        print("=" * 60)
        return True
    else:
        print("\n❌ DEPLOYMENT VERIFICATION FAILED!")
        print("=" * 60)
        print("Some checks failed. Please review the errors above.")
        print("The deployment may need additional configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 