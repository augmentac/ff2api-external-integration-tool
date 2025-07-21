#!/usr/bin/env python3
"""
Test script to check actual Peninsula Truck Lines website data
"""

import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime

class PeninsulaRealDataTester:
    """Test Peninsula website for actual tracking data"""
    
    def __init__(self):
        self.base_url = "https://www.peninsulatrucklines.com"
        
    async def test_real_peninsula_data(self, pro_number: str):
        """Test actual Peninsula website tracking"""
        
        print(f"\n🔍 Testing Peninsula tracking for PRO: {pro_number}")
        
        async with aiohttp.ClientSession() as session:
            # Test multiple potential Peninsula tracking methods
            
            # Method 1: Direct tracking page
            result1 = await self._test_tracking_page(session, pro_number)
            if result1:
                print(f"✅ Method 1 (Tracking Page): {result1}")
                return result1
            
            # Method 2: Potential API endpoint
            result2 = await self._test_api_endpoint(session, pro_number)
            if result2:
                print(f"✅ Method 2 (API): {result2}")
                return result2
            
            # Method 3: Form submission
            result3 = await self._test_form_submission(session, pro_number)
            if result3:
                print(f"✅ Method 3 (Form): {result3}")
                return result3
            
            # Method 4: Search functionality
            result4 = await self._test_search_functionality(session, pro_number)
            if result4:
                print(f"✅ Method 4 (Search): {result4}")
                return result4
                
            print("❌ All Peninsula tracking methods failed")
            return None
    
    async def _test_tracking_page(self, session: aiohttp.ClientSession, pro_number: str):
        """Test tracking page approach"""
        
        tracking_urls = [
            f"{self.base_url}/tracking",
            f"{self.base_url}/track",
            f"{self.base_url}/shipment-tracking",
            f"{self.base_url}/tracking?pro={pro_number}",
            f"{self.base_url}/track/{pro_number}"
        ]
        
        for url in tracking_urls:
            try:
                print(f"  🔗 Trying: {url}")
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        print(f"    ✅ Status 200 - Content length: {len(content)}")
                        
                        # Look for tracking forms or data
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Check for existing tracking results
                        tracking_results = self._extract_tracking_results(soup, pro_number)
                        if tracking_results:
                            return tracking_results
                        
                        # Check for tracking forms
                        forms = soup.find_all('form')
                        for form in forms:
                            form_text = form.get_text().lower()
                            if any(keyword in form_text for keyword in ['track', 'pro', 'shipment', 'bill']):
                                print(f"    📋 Found potential tracking form")
                                
                        # Look for input fields
                        inputs = soup.find_all('input', attrs={'name': re.compile(r'(track|pro|bill|shipment)', re.I)})
                        if inputs:
                            print(f"    📝 Found {len(inputs)} tracking input fields")
                            
                    else:
                        print(f"    ❌ Status {response.status}")
                        
            except Exception as e:
                print(f"    ❌ Error: {e}")
                
        return None
    
    async def _test_api_endpoint(self, session: aiohttp.ClientSession, pro_number: str):
        """Test potential API endpoints"""
        
        api_urls = [
            f"{self.base_url}/api/tracking",
            f"{self.base_url}/api/track",
            f"{self.base_url}/api/shipment/track",
            f"{self.base_url}/tracking/api",
            f"{self.base_url}/services/tracking"
        ]
        
        for url in api_urls:
            try:
                print(f"  🔗 API Test: {url}")
                
                # Test GET
                async with session.get(url, params={'pro': pro_number}) as response:
                    if response.status == 200:
                        try:
                            result = await response.json()
                            print(f"    ✅ GET API response: {result}")
                            return self._parse_api_response(result, pro_number)
                        except:
                            content = await response.text()
                            if content and len(content) < 10000:  # Reasonable content
                                print(f"    📄 GET response (not JSON): {content[:200]}...")
                
                # Test POST
                post_data = {
                    'proNumber': pro_number,
                    'pro': pro_number,
                    'trackingNumber': pro_number
                }
                
                async with session.post(url, json=post_data) as response:
                    if response.status == 200:
                        try:
                            result = await response.json()
                            print(f"    ✅ POST API response: {result}")
                            return self._parse_api_response(result, pro_number)
                        except:
                            pass
                            
            except Exception as e:
                print(f"    ❌ API Error: {e}")
                
        return None
    
    async def _test_form_submission(self, session: aiohttp.ClientSession, pro_number: str):
        """Test form submission"""
        
        try:
            # Get main tracking page first
            async with session.get(f"{self.base_url}/tracking") as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find forms
                    forms = soup.find_all('form')
                    for form in forms:
                        action = form.get('action', '/tracking')
                        method = form.get('method', 'post').lower()
                        
                        if not action.startswith('http'):
                            action = f"{self.base_url}{action}"
                        
                        print(f"  📋 Form found: {method.upper()} {action}")
                        
                        # Extract form data
                        form_data = {}
                        
                        # Get all input fields
                        inputs = form.find_all(['input', 'select', 'textarea'])
                        for inp in inputs:
                            name = inp.get('name')
                            value = inp.get('value', '')
                            inp_type = inp.get('type', 'text').lower()
                            
                            if name:
                                if inp_type in ['hidden', 'csrf']:
                                    form_data[name] = value
                                elif any(keyword in name.lower() for keyword in ['track', 'pro', 'bill']):
                                    form_data[name] = pro_number
                                elif inp_type == 'submit':
                                    form_data[name] = value or 'Track'
                        
                        if form_data:
                            print(f"    📝 Submitting form data: {form_data}")
                            
                            if method == 'post':
                                async with session.post(action, data=form_data) as form_response:
                                    if form_response.status == 200:
                                        result_content = await form_response.text()
                                        return self._extract_tracking_results(BeautifulSoup(result_content, 'html.parser'), pro_number)
                            else:
                                async with session.get(action, params=form_data) as form_response:
                                    if form_response.status == 200:
                                        result_content = await form_response.text()
                                        return self._extract_tracking_results(BeautifulSoup(result_content, 'html.parser'), pro_number)
                        
        except Exception as e:
            print(f"    ❌ Form submission error: {e}")
            
        return None
    
    async def _test_search_functionality(self, session: aiohttp.ClientSession, pro_number: str):
        """Test search functionality"""
        
        search_urls = [
            f"{self.base_url}/search",
            f"{self.base_url}/?q={pro_number}",
            f"{self.base_url}/?search={pro_number}",
            f"{self.base_url}/search?query={pro_number}"
        ]
        
        for url in search_urls:
            try:
                print(f"  🔍 Search test: {url}")
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        result = self._extract_tracking_results(BeautifulSoup(content, 'html.parser'), pro_number)
                        if result:
                            return result
                            
            except Exception as e:
                print(f"    ❌ Search error: {e}")
                
        return None
    
    def _extract_tracking_results(self, soup: BeautifulSoup, pro_number: str):
        """Extract tracking results from HTML"""
        
        # Look for tracking information in the HTML
        text_content = soup.get_text()
        
        # Check if PRO number appears in results
        if pro_number in text_content:
            print(f"    📍 PRO {pro_number} found in page content!")
            
            # Look for status information near the PRO number
            status_keywords = ['delivered', 'in transit', 'picked up', 'out for delivery', 'complete', 'pending']
            location_pattern = r'([A-Z]{2,}(?:\s+[A-Z]{2,})*)\s*,\s*([A-Z]{2})'
            
            # Find text around PRO number
            pro_context = self._get_text_around_pro(text_content, pro_number)
            if pro_context:
                print(f"    📄 Context around PRO: {pro_context}")
                
                # Extract status
                status = None
                for keyword in status_keywords:
                    if keyword.lower() in pro_context.lower():
                        status = keyword.title()
                        break
                
                # Extract location
                location_match = re.search(location_pattern, pro_context)
                location = location_match.group(0) if location_match else None
                
                if status or location:
                    return {
                        'status': status or 'Unknown',
                        'location': location or 'Unknown',
                        'event': f'Tracking information found for {pro_number}',
                        'timestamp': datetime.now().isoformat(),
                        'source': 'Real Peninsula Website',
                        'raw_context': pro_context
                    }
        
        return None
    
    def _get_text_around_pro(self, text: str, pro_number: str, context_chars: int = 300):
        """Get text around PRO number occurrence"""
        
        pro_index = text.find(pro_number)
        if pro_index == -1:
            return None
            
        start = max(0, pro_index - context_chars)
        end = min(len(text), pro_index + len(pro_number) + context_chars)
        
        return text[start:end].strip()
    
    def _parse_api_response(self, response: dict, pro_number: str):
        """Parse API response for tracking data"""
        
        # Look for tracking data in various response structures
        if 'tracking' in response:
            tracking_data = response['tracking']
            return {
                'status': tracking_data.get('status', 'Unknown'),
                'location': tracking_data.get('location', 'Unknown'),
                'event': tracking_data.get('description', 'Tracking information found'),
                'timestamp': tracking_data.get('timestamp', datetime.now().isoformat()),
                'source': 'Peninsula API'
            }
        
        # Check for shipment data
        if 'shipment' in response:
            shipment_data = response['shipment']
            return {
                'status': shipment_data.get('status', 'Unknown'),
                'location': shipment_data.get('currentLocation', 'Unknown'),
                'event': 'Shipment information found',
                'timestamp': datetime.now().isoformat(),
                'source': 'Peninsula API'
            }
        
        return None

async def main():
    """Test Peninsula tracking with real PRO numbers"""
    
    tester = PeninsulaRealDataTester()
    
    # Test PRO numbers from the issue report
    test_pros = [
        "536246546",  # User reports shows "VANCOUVER, WA" but should be different
        "536246554",  # User reports shows "VANCOUVER, WA" but should be different
        "537313956",  # User reports shows "SPOKANE, WA" but should be different
        "62263246"    # User reports shows "TACOMA, WA" but should be different
    ]
    
    print("🚛 Testing Peninsula Truck Lines Real Data Extraction")
    print("=" * 60)
    
    for pro in test_pros:
        result = await tester.test_real_peninsula_data(pro)
        if result:
            print(f"\n📊 REAL DATA FOUND for PRO {pro}:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"\n❌ No real data found for PRO {pro}")
        
        print("-" * 40)
        
        # Small delay between requests
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())