#!/usr/bin/env python3
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
