#!/usr/bin/env python3
"""
Cloud-Compatible Tracking System
Works in Streamlit Cloud without browser automation
"""

import requests
import time
import json
import re
import logging
from typing import Dict, List
from bs4 import BeautifulSoup
import cloudscraper

logger = logging.getLogger(__name__)

class CloudCompatibleTracker:
    """Cloud-compatible tracking system that works without browser automation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.scraper = cloudscraper.create_scraper()
        self.setup_headers()
    
    def setup_headers(self):
        """Setup realistic headers for web requests"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(self.headers)
    
    async def track_estes_cloud(self, tracking_number: str) -> Dict:
        """Track Estes shipments using cloud-compatible methods"""
        try:
            logger.info(f"🌐 Cloud tracking Estes: {tracking_number}")
            
            # Method 1: Try direct API endpoints
            api_result = await self.try_estes_api(tracking_number)
            if api_result.get('success'):
                return api_result
            
            # Method 2: Try mobile endpoints
            mobile_result = await self.try_estes_mobile(tracking_number)
            if mobile_result.get('success'):
                return mobile_result
            
            # Method 3: Try form submission with session handling
            form_result = await self.try_estes_form(tracking_number)
            if form_result.get('success'):
                return form_result
            
            # Method 4: Try with CloudScraper
            scraper_result = await self.try_estes_scraper(tracking_number)
            if scraper_result.get('success'):
                return scraper_result
            
            return {
                'success': False,
                'error': 'All cloud tracking methods failed',
                'tracking_number': tracking_number,
                'carrier': 'Estes Express'
            }
            
        except Exception as e:
            logger.error(f"Cloud tracking error: {str(e)}")
            return {
                'success': False,
                'error': f'Cloud tracking error: {str(e)}',
                'tracking_number': tracking_number,
                'carrier': 'Estes Express'
            }
    
    async def try_estes_api(self, tracking_number: str) -> Dict:
        """Try Estes API endpoints with enhanced detection"""
        try:
            # Enhanced API endpoints to try
            api_urls = [
                # Primary API endpoints
                f"https://www.estes-express.com/api/shipment-tracking/{tracking_number}",
                f"https://www.estes-express.com/api/tracking/{tracking_number}",
                f"https://api.estes-express.com/tracking/{tracking_number}",
                f"https://www.estes-express.com/myestes/api/tracking/{tracking_number}",
                
                # Mobile API endpoints
                f"https://m.estes-express.com/api/tracking/{tracking_number}",
                f"https://mobile.estes-express.com/api/tracking/{tracking_number}",
                
                # Alternative API patterns
                f"https://www.estes-express.com/api/v1/tracking/{tracking_number}",
                f"https://www.estes-express.com/api/v2/tracking/{tracking_number}",
                f"https://tracking.estes-express.com/api/{tracking_number}",
                
                # GraphQL and REST variations
                f"https://www.estes-express.com/graphql?query={{trackingInfo(pro:\"{tracking_number}\"){{status,location,events}}}}",
                f"https://www.estes-express.com/rest/tracking/{tracking_number}",
            ]
            
            headers_variations = [
                # Standard headers
                self.headers,
                
                # API-specific headers
                {
                    **self.headers,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                
                # Mobile headers
                {
                    **self.headers,
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'application/json, text/plain, */*'
                },
                
                # AJAX headers
                {
                    **self.headers,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/javascript, */*; q=0.01'
                }
            ]
            
            for url in api_urls:
                for headers in headers_variations:
                    try:
                        response = self.session.get(url, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            # Try to parse as JSON
                            try:
                                data = response.json()
                                if data and isinstance(data, dict):
                                    parsed = self.parse_api_response(data, tracking_number)
                                    if parsed.get('success'):
                                        logger.info(f"✅ API success: {url}")
                                        return parsed
                            except:
                                # Try to parse as HTML if JSON fails
                                if tracking_number in response.text:
                                    parsed = self.parse_html_response(response.text, tracking_number)
                                    if parsed.get('success'):
                                        logger.info(f"✅ API HTML success: {url}")
                                        return parsed
                                        
                    except Exception as e:
                        logger.debug(f"API endpoint failed: {url} - {str(e)}")
                        continue
            
            return {'success': False, 'error': 'No API endpoints responded with tracking data'}
            
        except Exception as e:
            return {'success': False, 'error': f'API error: {str(e)}'}
    
    async def try_estes_mobile(self, tracking_number: str) -> Dict:
        """Try Estes mobile endpoints"""
        try:
            mobile_headers = {
                **self.headers,
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            }
            
            mobile_urls = [
                f"https://m.estes-express.com/tracking/{tracking_number}",
                f"https://www.estes-express.com/m/tracking/{tracking_number}",
                f"https://mobile.estes-express.com/tracking/{tracking_number}"
            ]
            
            for url in mobile_urls:
                try:
                    response = self.session.get(url, headers=mobile_headers, timeout=10)
                    if response.status_code == 200:
                        parsed = self.parse_html_response(response.text, tracking_number)
                        if parsed.get('success'):
                            logger.info(f"✅ Mobile success: {url}")
                            return parsed
                except Exception as e:
                    logger.debug(f"Mobile endpoint failed: {url} - {str(e)}")
                    continue
            
            return {'success': False, 'error': 'No mobile endpoints responded'}
            
        except Exception as e:
            return {'success': False, 'error': f'Mobile error: {str(e)}'}
    
    async def try_estes_form(self, tracking_number: str) -> Dict:
        """Try form submission with enhanced session handling"""
        try:
            # Get the tracking page first
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking/"
            
            # Try multiple form submission approaches
            form_approaches = [
                # Standard form submission
                {
                    'url': tracking_url,
                    'method': 'GET',
                    'follow_redirects': True
                },
                
                # Direct POST to common endpoints
                {
                    'url': 'https://www.estes-express.com/myestes/shipment-tracking/search',
                    'method': 'POST',
                    'data': {'trackingNumber': tracking_number, 'pro': tracking_number}
                },
                
                # AJAX-style submission
                {
                    'url': 'https://www.estes-express.com/api/tracking/search',
                    'method': 'POST',
                    'headers': {'X-Requested-With': 'XMLHttpRequest'},
                    'data': {'proNumber': tracking_number}
                }
            ]
            
            for approach in form_approaches:
                try:
                    if approach['method'] == 'GET':
                        response = self.session.get(approach['url'], timeout=15)
                    else:
                        response = self.session.post(
                            approach['url'], 
                            data=approach.get('data', {}),
                            headers=approach.get('headers', {}),
                            timeout=15
                        )
                    
                    if response.status_code == 200 and tracking_number in response.text:
                        parsed = self.parse_html_response(response.text, tracking_number)
                        if parsed.get('success'):
                            logger.info(f"✅ Form submission success: {approach['url']}")
                            return parsed
                            
                except Exception as e:
                    logger.debug(f"Form approach failed: {approach['url']} - {str(e)}")
                    continue
            
            return {'success': False, 'error': 'Form submission methods failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'Form error: {str(e)}'}
    
    async def try_estes_scraper(self, tracking_number: str) -> Dict:
        """Try with CloudScraper to bypass protection"""
        try:
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking/"
            
            # Use CloudScraper to get the page
            response = self.scraper.get(tracking_url, timeout=15)
            
            if response.status_code == 200:
                parsed = self.parse_html_response(response.text, tracking_number)
                if parsed.get('success'):
                    logger.info("✅ CloudScraper success")
                    return parsed
            
            return {'success': False, 'error': 'CloudScraper failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'Scraper error: {str(e)}'}
    
    def parse_api_response(self, data: Dict, tracking_number: str) -> Dict:
        """Parse API response data"""
        try:
            # Look for tracking data in various formats
            status = None
            location = None
            events = []
            
            # Common API response patterns
            if 'status' in data:
                status = data['status']
            elif 'trackingStatus' in data:
                status = data['trackingStatus']
            elif 'shipmentStatus' in data:
                status = data['shipmentStatus']
            
            if 'location' in data:
                location = data['location']
            elif 'currentLocation' in data:
                location = data['currentLocation']
            elif 'lastLocation' in data:
                location = data['lastLocation']
            
            # Look for events
            if 'events' in data:
                events = data['events']
            elif 'trackingEvents' in data:
                events = data['trackingEvents']
            elif 'history' in data:
                events = data['history']
            
            if status or location or events:
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'carrier': 'Estes Express',
                    'status': status or 'Status available',
                    'location': location or 'Location available',
                    'events': events,
                    'source': 'API'
                }
            
            return {'success': False, 'error': 'No tracking data found in API response'}
            
        except Exception as e:
            return {'success': False, 'error': f'API parsing error: {str(e)}'}
    
    def parse_html_response(self, html_content: str, tracking_number: str) -> Dict:
        """Enhanced HTML response parsing for tracking data"""
        try:
            # Check if tracking number is in content
            if tracking_number not in html_content:
                return {'success': False, 'error': 'Tracking number not found in response'}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for tracking data
            tracking_data = {
                'success': False,
                'tracking_number': tracking_number,
                'carrier': 'Estes Express',
                'status': None,
                'location': None,
                'events': [],
                'source': 'HTML'
            }
            
            # Enhanced status detection
            status_patterns = [
                # Direct text patterns
                r'status[:\s]*([^<\n]{5,50})',
                r'current status[:\s]*([^<\n]{5,50})',
                r'shipment status[:\s]*([^<\n]{5,50})',
                
                # Common status words
                r'(delivered|out for delivery|in transit|picked up|at origin|at destination)[^<\n]*',
                
                # Date + status patterns
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}[^<\n]*(delivered|transit|pickup|origin|destination)[^<\n]*'
            ]
            
            for pattern in status_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    status_text = matches[0] if isinstance(matches[0], str) else str(matches[0][0]) if matches[0] else ""
                    if len(status_text.strip()) > 3:
                        tracking_data['status'] = status_text.strip()
                        break
            
            # Enhanced location detection
            location_patterns = [
                # City, State patterns
                r'([A-Z][a-z]+,\s*[A-Z]{2})',
                r'location[:\s]*([A-Z][a-z]+,\s*[A-Z]{2})',
                r'([A-Z][A-Z\s]+,\s*[A-Z]{2})',  # All caps city names
                
                # ZIP code patterns
                r'([A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5})',
            ]
            
            for pattern in location_patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    location_text = matches[0] if isinstance(matches[0], str) else matches[0]
                    if len(location_text.strip()) > 3:
                        tracking_data['location'] = location_text.strip()
                        break
            
            # Enhanced event detection
            events = []
            
            # Look for table rows with dates and tracking info
            rows = soup.find_all(['tr', 'div', 'p'])
            for row in rows:
                row_text = row.get_text(strip=True)
                
                # Check for date patterns
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', row_text)
                
                if date_match and tracking_number in row_text:
                    event_data = {
                        'date': date_match.group(1),
                        'description': row_text
                    }
                    
                    # Extract status from event
                    for status_word in ['delivered', 'transit', 'pickup', 'origin', 'destination', 'departed', 'arrived']:
                        if status_word in row_text.lower():
                            event_data['status'] = status_word.title()
                            break
                    
                    events.append(event_data)
                    
                    # Use first event for main status if not found
                    if not tracking_data['status'] and 'status' in event_data:
                        tracking_data['status'] = event_data['status']
            
            tracking_data['events'] = events[:10]  # Limit to 10 events
            
            # Mark as successful if we found any meaningful data
            if tracking_data['status'] or tracking_data['location'] or tracking_data['events']:
                tracking_data['success'] = True
                logger.info(f"✅ HTML parsing success: Status={tracking_data['status']}, Location={tracking_data['location']}, Events={len(tracking_data['events'])}")
                return tracking_data
            
            # Even if no structured data, if tracking number is found, it's partial success
            if tracking_number in html_content:
                tracking_data['success'] = True
                tracking_data['status'] = 'Tracking number found in system'
                tracking_data['location'] = 'Data available but requires parsing enhancement'
                logger.info("⚠️ Partial success: Tracking number found but limited data extracted")
                return tracking_data
            
            return {'success': False, 'error': 'No tracking data found in HTML response'}
            
        except Exception as e:
            return {'success': False, 'error': f'HTML parsing error: {str(e)}'}

# Global instance for easy access
cloud_tracker = CloudCompatibleTracker()

async def track_cloud_compatible(tracking_number: str, carrier: str = None) -> Dict:
    """Main cloud-compatible tracking function"""
    try:
        if not carrier or 'estes' in carrier.lower():
            return await cloud_tracker.track_estes_cloud(tracking_number)
        else:
            return {
                'success': False,
                'error': f'Cloud tracking not yet implemented for {carrier}',
                'tracking_number': tracking_number,
                'carrier': carrier
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Cloud tracking error: {str(e)}',
            'tracking_number': tracking_number,
            'carrier': carrier or 'Unknown'
        } 