#!/usr/bin/env python3
"""
Test script to verify tracking fixes for failing carriers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from backend.ltl_tracking_client import LTLTrackingClient
from backend.carrier_detection import detect_carrier_from_pro
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_carrier_detection():
    """Test carrier detection for failing PROs"""
    
    test_cases = [
        # Estes Express (currently failing)
        '0628143046',
        '1282975382', 
        '1611116978',
        '2121121287',
        '750773321',
        
        # Peninsula (currently failing)
        '536246546',
        '537313956',
        '62263246',
        
        # FedEx (some failing)
        '885614735-5',
        '761607932-1',
        '1751027634',
        '4012381741',
        
        # R+L (working but let's verify)
        'I942130827',
        '14588517-6',
        '933784722',
    ]
    
    print("=== CARRIER DETECTION TEST ===")
    for pro_number in test_cases:
        carrier_info = detect_carrier_from_pro(pro_number)
        if carrier_info:
            print(f"✅ {pro_number} -> {carrier_info['carrier_name']} ({carrier_info['carrier_code']})")
            print(f"   URL: {carrier_info['tracking_url']}")
        else:
            print(f"❌ {pro_number} -> NOT DETECTED")
        print()

def test_tracking_specific_cases():
    """Test tracking for specific failing cases"""
    
    client = LTLTrackingClient(delay_between_requests=1, timeout=15)
    
    # Test specific failing cases
    test_cases = [
        ('0628143046', 'Estes Express'),
        ('536246546', 'Peninsula Truck Lines'),
        ('885614735-5', 'FedEx Freight'),
        ('I942130827', 'R&L Carriers'),  # This should work
    ]
    
    print("=== TRACKING TEST ===")
    for pro_number, expected_carrier in test_cases:
        print(f"\nTesting {pro_number} ({expected_carrier})...")
        try:
            result = client.track_pro_number(pro_number)
            print(f"Carrier: {result.carrier_name}")
            print(f"Status: {result.tracking_status}")
            print(f"Location: {result.tracking_location}")
            print(f"Timestamp: {result.tracking_timestamp}")
            print(f"Success: {result.scrape_success}")
            if result.error_message:
                print(f"Error: {result.error_message}")
        except Exception as e:
            print(f"Exception: {e}")
    
    client.close()

def debug_estes_tracking():
    """Debug Estes tracking to see actual HTML content"""
    
    from backend.ltl_tracking_client import LTLTrackingClient
    import requests
    from bs4 import BeautifulSoup
    
    # Test one Estes PRO
    pro_number = '0628143046'
    url = f'https://www.estes-express.com/myestes/tracking/shipment?searchValue={pro_number}'
    
    print(f"=== DEBUGGING ESTES TRACKING FOR {pro_number} ===")
    print(f"URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.estes-express.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Print first 1000 characters of text
            page_text = soup.get_text()
            print(f"\nPage Text (first 1000 chars):")
            print(page_text[:1000])
            
            # Look for forms
            forms = soup.find_all('form')
            print(f"\nForms found: {len(forms)}")
            for i, form in enumerate(forms):
                print(f"Form {i}: {form.get('action', 'No action')} - {form.get('method', 'No method')}")
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f"  Input: {inp.get('name', 'No name')} = {inp.get('value', 'No value')}")
            
            # Look for tables
            tables = soup.find_all('table')
            print(f"\nTables found: {len(tables)}")
            for i, table in enumerate(tables):
                print(f"Table {i} classes: {table.get('class', 'No class')}")
                rows = table.find_all('tr')
                print(f"  Rows: {len(rows)}")
                if rows:
                    for j, row in enumerate(rows[:3]):  # First 3 rows
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [cell.get_text().strip() for cell in cells]
                        print(f"    Row {j}: {cell_texts}")
            
            # Look for divs with tracking-related classes
            tracking_divs = soup.find_all('div', class_=lambda x: x and ('track' in str(x).lower() or 'status' in str(x).lower() or 'shipment' in str(x).lower()))
            print(f"\nTracking-related divs found: {len(tracking_divs)}")
            for i, div in enumerate(tracking_divs):
                print(f"Div {i}: class='{div.get('class')}' text='{div.get_text().strip()[:100]}'")
            
        else:
            print(f"Failed to fetch page: {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_alternative_estes_urls():
    """Test alternative Estes URLs to find non-JavaScript options"""
    
    import requests
    from bs4 import BeautifulSoup
    
    pro_number = '0628143046'
    
    # Alternative Estes URLs to try
    alternative_urls = [
        f'https://www.estes-express.com/myestes/shipment-tracking/?searchValue={pro_number}',
        f'https://www.estes-express.com/tracking?pro={pro_number}',
        f'https://www.estes-express.com/track?searchValue={pro_number}',
        f'https://www.estes-express.com/myestes/tracking/shipment/{pro_number}',
        f'https://www.estes-express.com/api/tracking/{pro_number}',
        f'https://www.estes-express.com/api/shipment/{pro_number}',
        f'https://www.estes-express.com/tracking/api?pro={pro_number}',
        f'https://www.estes-express.com/shipment/tracking/{pro_number}',
        f'https://www.estes-express.com/tools/tracking?pro={pro_number}',
        f'https://www.estes-express.com/services/tracking?pro={pro_number}',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.estes-express.com/',
    }
    
    print("=== TESTING ALTERNATIVE ESTES URLS ===")
    
    for url in alternative_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"\n{url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()
                
                # Check if it's a JavaScript-only page
                if 'Please enable JavaScript' in page_text:
                    print("❌ JavaScript required")
                # Check if it contains tracking data
                elif any(keyword in page_text.lower() for keyword in ['delivered', 'in transit', 'tracking', 'shipment', 'status']):
                    print("✅ Potential tracking data found")
                    print(f"Preview: {page_text[:200]}...")
                else:
                    print("⚠️  No tracking data detected")
                    
            elif response.status_code == 404:
                print("❌ Not found")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def discover_estes_api_endpoints():
    """Discover Estes API endpoints by testing common patterns"""
    
    import requests
    from urllib.parse import urljoin
    
    pro_number = '0628143046'
    base_urls = [
        'https://www.estes-express.com',
        'https://api.estes-express.com',
        'https://tracking.estes-express.com',
        'https://www.estesexpress.com'
    ]
    
    # Common API endpoint patterns
    api_patterns = [
        '/api/tracking/{pro}',
        '/api/shipment/{pro}',
        '/api/track/{pro}',
        '/tracking/api/{pro}',
        '/shipment/api/{pro}',
        '/_/api/tracking/{pro}',
        '/_/api/shipment/{pro}',
        '/rest/tracking/{pro}',
        '/rest/shipment/{pro}',
        '/services/tracking/{pro}',
        '/v1/tracking/{pro}',
        '/v2/tracking/{pro}',
        '/api/v1/tracking/{pro}',
        '/api/v2/tracking/{pro}',
        '/myestes/api/tracking/{pro}',
        '/myestes/api/shipment/{pro}'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.estes-express.com/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    print("=== DISCOVERING ESTES API ENDPOINTS ===")
    print(f"Testing PRO: {pro_number}")
    print()
    
    found_endpoints = []
    
    for base_url in base_urls:
        print(f"Testing base URL: {base_url}")
        
        for pattern in api_patterns:
            endpoint = urljoin(base_url, pattern.format(pro=pro_number))
            
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'json' in content_type:
                        try:
                            json_data = response.json()
                            if json_data and any(key in str(json_data).lower() for key in ['track', 'status', 'shipment', 'delivery']):
                                print(f"✅ FOUND JSON API: {endpoint}")
                                print(f"   Response: {json_data}")
                                found_endpoints.append({
                                    'endpoint': endpoint,
                                    'type': 'json',
                                    'data': json_data
                                })
                        except:
                            pass
                    
                    elif any(keyword in response.text.lower() for keyword in ['delivered', 'transit', 'status', 'tracking']):
                        print(f"✅ FOUND TEXT API: {endpoint}")
                        print(f"   Response: {response.text[:200]}...")
                        found_endpoints.append({
                            'endpoint': endpoint,
                            'type': 'text',
                            'data': response.text
                        })
                
                elif response.status_code == 404:
                    pass  # Expected for most endpoints
                else:
                    print(f"⚠️  {endpoint} -> {response.status_code}")
                    
            except Exception as e:
                pass  # Expected for most endpoints
        
        print()
    
    if found_endpoints:
        print("=== SUMMARY OF FOUND ENDPOINTS ===")
        for endpoint in found_endpoints:
            print(f"Type: {endpoint['type']}")
            print(f"URL: {endpoint['endpoint']}")
            print(f"Data: {str(endpoint['data'])[:100]}...")
            print()
    else:
        print("❌ No API endpoints found. May need to analyze JavaScript calls.")
    
    return found_endpoints

def analyze_estes_javascript():
    """Analyze JavaScript in Estes tracking page to find API calls"""
    
    import requests
    from bs4 import BeautifulSoup
    import re
    import json
    
    pro_number = '0628143046'
    url = f'https://www.estes-express.com/myestes/tracking/shipment?searchValue={pro_number}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.estes-express.com/',
    }
    
    print("=== ANALYZING ESTES JAVASCRIPT ===")
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all script tags
        script_tags = soup.find_all('script')
        print(f"Found {len(script_tags)} script tags")
        
        api_endpoints = []
        embedded_data = []
        
        for i, script in enumerate(script_tags):
            script_content = script.get_text() if script.get_text() else ""
            
            if not script_content.strip():
                continue
                
            print(f"\n--- Script {i+1} ---")
            print(f"Length: {len(script_content)} characters")
            
            # Look for API endpoint patterns
            api_patterns = [
                r'["\']([^"\']*api[^"\']*track[^"\']*)["\']',
                r'["\']([^"\']*track[^"\']*api[^"\']*)["\']',
                r'["\']([^"\']*\/api\/[^"\']*)["\']',
                r'["\']([^"\']*\/rest\/[^"\']*)["\']',
                r'["\']([^"\']*\/services\/[^"\']*)["\']',
                r'baseUrl["\']?\s*:\s*["\']([^"\']+)["\']',
                r'apiUrl["\']?\s*:\s*["\']([^"\']+)["\']',
                r'trackingUrl["\']?\s*:\s*["\']([^"\']+)["\']',
                r'endpoint["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    if 'api' in match.lower() or 'track' in match.lower() or 'rest' in match.lower():
                        api_endpoints.append(match)
                        print(f"   API endpoint found: {match}")
            
            # Look for embedded tracking data
            data_patterns = [
                r'trackingData["\']?\s*[:=]\s*(\{[^}]*\}|\[[^\]]*\])',
                r'shipmentData["\']?\s*[:=]\s*(\{[^}]*\}|\[[^\]]*\])',
                r'trackingStatus["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'shipmentStatus["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                r'window\.__DATA__\s*=\s*(\{.*?\});',
                r'var\s+trackingInfo\s*=\s*(\{.*?\});',
                r'var\s+shipmentInfo\s*=\s*(\{.*?\});'
            ]
            
            for pattern in data_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    try:
                        # Try to parse as JSON
                        if match.startswith('{') or match.startswith('['):
                            json_data = json.loads(match)
                            embedded_data.append(json_data)
                            print(f"   JSON data found: {json_data}")
                        else:
                            embedded_data.append(match)
                            print(f"   Data found: {match}")
                    except:
                        embedded_data.append(match)
                        print(f"   Raw data found: {match}")
            
            # Look for fetch/xhr calls
            xhr_patterns = [
                r'fetch\s*\(\s*["\']([^"\']+)["\']',
                r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)["\']',
                r'\$\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
                r'\$\.get\s*\(\s*["\']([^"\']+)["\']',
                r'\$\.post\s*\(\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in xhr_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    if 'track' in match.lower() or 'api' in match.lower():
                        api_endpoints.append(match)
                        print(f"   XHR endpoint found: {match}")
        
        # Summary
        print("\n=== SUMMARY ===")
        if api_endpoints:
            print("API Endpoints found:")
            for endpoint in set(api_endpoints):
                print(f"  - {endpoint}")
        else:
            print("No API endpoints found")
        
        if embedded_data:
            print("Embedded data found:")
            for data in embedded_data:
                print(f"  - {str(data)[:100]}...")
        else:
            print("No embedded data found")
        
        return {
            'api_endpoints': list(set(api_endpoints)),
            'embedded_data': embedded_data
        }
        
    except Exception as e:
        print(f"Error analyzing JavaScript: {e}")
        return None

if __name__ == "__main__":
    print("Testing tracking fixes...\n")
    
    debug_estes_tracking()
    print("\n" + "="*50 + "\n")
    
    test_alternative_estes_urls()
    print("\n" + "="*50 + "\n")
    
    test_carrier_detection()
    test_tracking_specific_cases()
    
    print("\nTest complete!") 