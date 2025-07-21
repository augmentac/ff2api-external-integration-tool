#!/usr/bin/env python3
"""
Debug Estes JavaScript files to find API endpoints
"""

import asyncio
import aiohttp
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_estes_js():
    """Debug Estes JavaScript files for API endpoints"""
    
    async with aiohttp.ClientSession() as session:
        try:
            # Get the Angular app page to find JavaScript files
            main_url = 'https://www.estes-express.com/myestes/shipment-tracking/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            print(f"Getting Angular app page: {main_url}")
            async with session.get(main_url, headers=headers) as response:
                if response.status != 200:
                    print(f"❌ App page failed: {response.status}")
                    return
                
                content = await response.text()
                print(f"✅ App page loaded")
                
                # Extract JavaScript file URLs
                js_files = re.findall(r'src="([^"]*\.js[^"]*)"', content)
                print(f"Found {len(js_files)} JavaScript files")
                
                base_url = 'https://www.estes-express.com/myestes/shipment-tracking/'
                
                for js_file in js_files:
                    if js_file.startswith('/'):
                        js_url = f"https://www.estes-express.com{js_file}"
                    elif js_file.startswith('http'):
                        js_url = js_file
                    else:
                        js_url = f"{base_url}{js_file}"
                    
                    print(f"\nAnalyzing: {js_url}")
                    
                    try:
                        async with session.get(js_url, headers=headers) as js_response:
                            if js_response.status == 200:
                                js_content = await js_response.text()
                                
                                # Look for API endpoint patterns
                                api_patterns = [
                                    r'[\'"`]([^\'"`]*(?:api|service|track)[^\'"`]*)[\'"`]',
                                    r'endpoint[\'"`\s]*[:=][\'"`\s]*([^\'"`\s]+)',
                                    r'url[\'"`\s]*[:=][\'"`\s]*([^\'"`\s]*(?:api|track|search)[^\'"`\s]*)',
                                    r'/[a-zA-Z0-9/_-]*(?:api|track|search|shipment)[a-zA-Z0-9/_-]*',
                                ]
                                
                                api_urls = set()
                                for pattern in api_patterns:
                                    matches = re.findall(pattern, js_content, re.IGNORECASE)
                                    for match in matches:
                                        if isinstance(match, str) and len(match) > 5:
                                            if any(keyword in match.lower() for keyword in ['api', 'track', 'search', 'shipment']):
                                                api_urls.add(match)
                                
                                if api_urls:
                                    print(f"  Found API URLs: {list(api_urls)[:10]}")  # First 10
                                    
                                    # Test a few promising ones
                                    for api_url in list(api_urls)[:3]:
                                        if api_url.startswith('/'):
                                            full_api_url = f"https://www.estes-express.com{api_url}"
                                        elif api_url.startswith('http'):
                                            full_api_url = api_url
                                        else:
                                            continue
                                        
                                        print(f"    Testing API: {full_api_url}")
                                        
                                        # Try with PRO number
                                        test_urls = [
                                            f"{full_api_url}?query=1642457961",
                                            f"{full_api_url}?pro=1642457961",
                                            f"{full_api_url}/1642457961",
                                            f"{full_api_url}?trackingNumber=1642457961"
                                        ]
                                        
                                        for test_url in test_urls[:2]:  # Test first 2 only
                                            try:
                                                async with session.get(test_url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as api_response:
                                                    if api_response.status == 200:
                                                        api_result = await api_response.text()
                                                        if '1642457961' in api_result or 'memphis' in api_result.lower():
                                                            print(f"      ✅ SUCCESS! Found data in {test_url}")
                                                            print(f"      Sample: {api_result[:500]}")
                                                            
                                                            # Save full result
                                                            with open('/Users/augiecon2025/Documents/Solutions Engineering Dev/CSV->LTL Action/estes_api_result.json', 'w') as f:
                                                                f.write(api_result)
                                                            print(f"      Full result saved to estes_api_result.json")
                                                            return
                                                    else:
                                                        print(f"      HTTP {api_response.status}")
                                            except Exception as e:
                                                print(f"      Error: {e}")
                                else:
                                    print("  No API URLs found")
                            else:
                                print(f"  ❌ HTTP {js_response.status}")
                    except Exception as e:
                        print(f"  Error loading JS: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_estes_js())