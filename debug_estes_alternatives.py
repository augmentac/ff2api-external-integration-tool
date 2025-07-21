#!/usr/bin/env python3
"""
Debug alternative Estes endpoints that might work without JavaScript
"""

import asyncio
import aiohttp
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_estes_alternatives():
    """Try alternative Estes endpoints that might not require JavaScript"""
    
    pro_number = '1642457961'
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Try various alternative endpoints
        test_urls = [
            # Legacy/mobile endpoints that might return HTML
            f'https://www.estes-express.com/track?pro={pro_number}',
            f'https://www.estes-express.com/tracking?pro={pro_number}',
            f'https://www.estes-express.com/quicktrack?pro={pro_number}',
            f'https://www.estes-express.com/shipment?pro={pro_number}',
            
            # Mobile site variations
            f'https://m.estes-express.com/tracking?pro={pro_number}',
            f'https://mobile.estes-express.com/track?pro={pro_number}',
            
            # API endpoints that might return JSON/XML
            f'https://www.estes-express.com/api/track/{pro_number}',
            f'https://www.estes-express.com/api/shipment/{pro_number}',
            f'https://www.estes-express.com/api/tracking?pro={pro_number}',
            f'https://www.estes-express.com/services/track?pro={pro_number}',
            
            # Old-style CGI or PHP endpoints
            f'https://www.estes-express.com/cgi-bin/track.cgi?pro={pro_number}',
            f'https://www.estes-express.com/track.php?pro={pro_number}',
            f'https://www.estes-express.com/tracking.asp?pro={pro_number}',
            
            # RSS/XML feeds
            f'https://www.estes-express.com/rss/track?pro={pro_number}',
            f'https://www.estes-express.com/xml/track?pro={pro_number}',
        ]
        
        for i, url in enumerate(test_urls):
            print(f"\n[{i+1}/{len(test_urls)}] Testing: {url}")
            
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as response:
                    print(f"  Status: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        content_lower = content.lower()
                        
                        # Check for relevant content
                        found_indicators = []
                        
                        if pro_number in content:
                            found_indicators.append("PRO_NUMBER")
                        
                        if any(word in content_lower for word in ['memphis', 'tn', 'tennessee']):
                            found_indicators.append("MEMPHIS")
                        
                        if any(word in content_lower for word in ['delivered', 'delivery', 'status']):
                            found_indicators.append("STATUS")
                        
                        if any(word in content_lower for word in ['tracking', 'shipment', 'freight']):
                            found_indicators.append("TRACKING")
                        
                        if found_indicators:
                            print(f"  ✅ Found: {', '.join(found_indicators)}")
                            print(f"  Content length: {len(content)}")
                            
                            # Save promising results
                            filename = f'/Users/augiecon2025/Documents/Solutions Engineering Dev/CSV->LTL Action/estes_alt_{i+1}.html'
                            with open(filename, 'w') as f:
                                f.write(content)
                            print(f"  Saved to: estes_alt_{i+1}.html")
                            
                            # Show a snippet
                            if pro_number in content:
                                pro_pos = content.find(pro_number)
                                start = max(0, pro_pos - 200)
                                end = min(len(content), pro_pos + 200)
                                snippet = content[start:end]
                                print(f"  Snippet: {snippet}")
                        else:
                            print(f"  ❌ No relevant content found")
                    
                    elif response.status in [301, 302, 303, 307, 308]:
                        location = response.headers.get('Location', 'Unknown')
                        print(f"  🔄 Redirect to: {location}")
                        
                    else:
                        print(f"  ❌ HTTP {response.status}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_estes_alternatives())