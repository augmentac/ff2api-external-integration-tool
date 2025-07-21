#!/usr/bin/env python3
"""
Debug Estes form submission
"""

import asyncio
import aiohttp
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from urllib.parse import urlencode

async def debug_estes_form():
    """Debug Estes form submission"""
    
    pro_number = '1642457961'
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Get the main page with the form
            main_url = 'https://www.estes-express.com'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            print(f"Getting main page: {main_url}")
            async with session.get(main_url, headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Main page failed: {response.status}")
                    return
                
                content = await response.text()
                print(f"✅ Main page loaded, length: {len(content)}")
                
                # Find the form that goes to myestes/shipment-tracking
                soup = BeautifulSoup(content, 'html.parser')
                tracking_form = None
                
                forms = soup.find_all('form')
                for form in forms:
                    action = form.get('action', '')
                    if 'myestes' in action and 'shipment-tracking' in action:
                        tracking_form = form
                        break
                
                if not tracking_form:
                    print("❌ Tracking form not found")
                    return
                
                print(f"✅ Found tracking form with action: {tracking_form.get('action')}")
                
                # Step 2: Submit the form with our PRO number
                form_action = tracking_form.get('action')
                method = tracking_form.get('method', 'GET').upper()
                
                # Find the query input
                query_input = tracking_form.find('input', {'name': 'query'})
                if not query_input:
                    print("❌ Query input not found in form")
                    return
                
                print(f"✅ Found query input")
                
                # Prepare form data
                if method == 'GET':
                    # For GET, add query as URL parameter
                    tracking_url = f"{form_action}?query={pro_number}"
                    print(f"Submitting GET request to: {tracking_url}")
                    
                    async with session.get(tracking_url, headers=headers) as form_response:
                        print(f"Form response status: {form_response.status}")
                        
                        if form_response.status == 200:
                            result_content = await form_response.text()
                            print(f"Result content length: {len(result_content)}")
                            
                            # Look for the PRO number in the result
                            if pro_number in result_content:
                                print(f"✅ PRO number {pro_number} found in result!")
                                
                                # Extract context around PRO number
                                pro_pos = result_content.find(pro_number)
                                start = max(0, pro_pos - 1000)
                                end = min(len(result_content), pro_pos + 1000)
                                context = result_content[start:end]
                                
                                print(f"Context around PRO number:")
                                print("-" * 60)
                                print(context)
                                print("-" * 60)
                                
                                # Look for status and location in the context
                                import re
                                
                                status_patterns = [
                                    r'(delivered|in transit|out for delivery|picked up|exception|completed)',
                                ]
                                
                                location_patterns = [
                                    r'MEMPHIS[^<]*TN[^<]*US',
                                    r'([A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2,3}(?:\s+US)?)',
                                    r'([A-Z]{3,}\s*,\s*[A-Z]{2,3}(?:\s+US)?)',
                                ]
                                
                                for pattern in status_patterns:
                                    matches = re.findall(pattern, context, re.IGNORECASE)
                                    if matches:
                                        print(f"Status found: {matches}")
                                
                                for pattern in location_patterns:
                                    matches = re.findall(pattern, context, re.IGNORECASE)
                                    if matches:
                                        print(f"Location found: {matches}")
                                        
                                # Save result to file for inspection
                                with open('/Users/augiecon2025/Documents/Solutions Engineering Dev/CSV->LTL Action/estes_result.html', 'w') as f:
                                    f.write(result_content)
                                print("✅ Result saved to estes_result.html")
                                
                            else:
                                print(f"❌ PRO number {pro_number} NOT found in result")
                                # Still save for inspection
                                with open('/Users/augiecon2025/Documents/Solutions Engineering Dev/CSV->LTL Action/estes_result.html', 'w') as f:
                                    f.write(result_content)
                                print("Result saved to estes_result.html for inspection")
                        else:
                            print(f"❌ Form submission failed: {form_response.status}")
                else:
                    print(f"❌ Unsupported form method: {method}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_estes_form())