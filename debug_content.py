#!/usr/bin/env python3
"""
Debug content scraper to see what we're actually getting from carrier websites
"""

import asyncio
import aiohttp
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from src.backend.cloud_native_tracker import CloudNativeTracker

async def debug_content():
    """Debug what content we're actually getting"""
    
    # Test Estes PRO number that should show MEMPHIS, TN US
    pro_number = '1642457961'
    
    # Get a session
    tracker = CloudNativeTracker()
    session = await tracker.session_manager.get_session('estes')
    
    try:
        # Test different Estes URLs
        urls = [
            f'https://www.estes-express.com/shipment-tracking?pro={pro_number}',
            f'https://www.estes-express.com/myestes/shipment-tracking?pro={pro_number}',
            'https://www.estes-express.com/shipment-tracking',
            'https://www.estes-express.com'
        ]
        
        for i, url in enumerate(urls):
            print(f"\n{'='*60}")
            print(f"Testing URL {i+1}: {url}")
            print('='*60)
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"Status: {response.status}")
                    print(f"Headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        content = await response.text()
                        print(f"Content length: {len(content)}")
                        
                        # Look for the PRO number in content
                        if pro_number in content:
                            print(f"✅ PRO number {pro_number} found in content!")
                            
                            # Extract a section around the PRO number
                            pro_pos = content.find(pro_number)
                            start = max(0, pro_pos - 500)
                            end = min(len(content), pro_pos + 500)
                            context = content[start:end]
                            
                            print(f"Context around PRO number:")
                            print("-" * 40)
                            print(context)
                            print("-" * 40)
                        else:
                            print(f"❌ PRO number {pro_number} NOT found in content")
                        
                        # Look for any location-like patterns
                        import re
                        location_patterns = [
                            r'MEMPHIS',
                            r'[A-Z]{3,}\s*,\s*[A-Z]{2,3}',
                            r'[A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2,3}',
                        ]
                        
                        locations_found = []
                        for pattern in location_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            locations_found.extend(matches)
                        
                        if locations_found:
                            print(f"Location patterns found: {locations_found[:10]}")  # First 10
                        else:
                            print("❌ No location patterns found")
                        
                        # Check if there are any forms
                        soup = BeautifulSoup(content, 'html.parser')
                        forms = soup.find_all('form')
                        if forms:
                            print(f"Found {len(forms)} forms:")
                            for j, form in enumerate(forms):
                                action = form.get('action', 'No action')
                                method = form.get('method', 'GET')
                                print(f"  Form {j+1}: {method} to {action}")
                                
                                inputs = form.find_all('input')
                                if inputs:
                                    print(f"    Inputs: {[inp.get('name') for inp in inputs if inp.get('name')]}")
                        else:
                            print("❌ No forms found")
                            
                    else:
                        print(f"❌ HTTP {response.status}")
                        
            except Exception as e:
                print(f"❌ Error with {url}: {e}")
                
    finally:
        await tracker.session_manager.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(debug_content())