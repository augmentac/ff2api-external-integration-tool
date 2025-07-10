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
        """Try Estes API endpoints"""
        try:
            # Common API endpoints to try
            api_urls = [
                f"https://www.estes-express.com/api/shipment-tracking/{tracking_number}",
                f"https://www.estes-express.com/api/tracking/{tracking_number}",
                f"https://api.estes-express.com/tracking/{tracking_number}",
                f"https://www.estes-express.com/myestes/api/tracking/{tracking_number}"
            ]
            
            for url in api_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data and isinstance(data, dict):
                            parsed = self.parse_api_response(data, tracking_number)
                            if parsed.get('success'):
                                logger.info(f"✅ API success: {url}")
                                return parsed
                except Exception as e:
                    logger.debug(f"API endpoint failed: {url} - {str(e)}")
                    continue
            
            return {'success': False, 'error': 'No API endpoints responded'}
            
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
        """Try form submission with session handling"""
        try:
            # Get the tracking page first
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking/"
            response = self.session.get(tracking_url, timeout=15)
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Could not access tracking page'}
            
            # Parse the page for form data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for form elements
            form = soup.find('form')
            if not form:
                return {'success': False, 'error': 'No form found on tracking page'}
            
            # Extract form data
            form_data = {}
            for input_field in form.find_all(['input', 'textarea']):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value
            
            # Add tracking number
            form_data['trackingNumber'] = tracking_number
            form_data['pro'] = tracking_number
            form_data['proNumber'] = tracking_number
            
            # Submit form
            form_action = form.get('action', tracking_url)
            if not form_action.startswith('http'):
                form_action = f"https://www.estes-express.com{form_action}"
            
            response = self.session.post(form_action, data=form_data, timeout=15)
            
            if response.status_code == 200:
                parsed = self.parse_html_response(response.text, tracking_number)
                if parsed.get('success'):
                    logger.info("✅ Form submission success")
                    return parsed
            
            return {'success': False, 'error': 'Form submission failed'}
            
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
        """Parse HTML response for tracking data"""
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
            
            # Look for status information
            status_selectors = [
                '.status', '.tracking-status', '.shipment-status',
                '[class*="status"]', '[data-testid*="status"]'
            ]
            
            for selector in status_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and any(keyword in text.lower() for keyword in ['delivered', 'transit', 'pickup']):
                        tracking_data['status'] = text
                        break
                if tracking_data['status']:
                    break
            
            # Look for location information
            location_selectors = [
                '.location', '.current-location', '.facility',
                '[class*="location"]', '[data-testid*="location"]'
            ]
            
            for selector in location_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and re.search(r'[A-Z][a-z]+,?\s*[A-Z]{2}', text):
                        tracking_data['location'] = text
                        break
                if tracking_data['location']:
                    break
            
            # Look for events in table rows
            rows = soup.find_all('tr')
            events = []
            for row in rows:
                row_text = row.get_text(strip=True)
                if tracking_number in row_text or any(keyword in row_text.lower() for keyword in ['delivered', 'transit', 'pickup']):
                    # Extract date if present
                    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', row_text)
                    if date_match:
                        events.append({
                            'date': date_match.group(1),
                            'description': row_text
                        })
            
            tracking_data['events'] = events
            
            # Mark as successful if we found any data
            if tracking_data['status'] or tracking_data['location'] or tracking_data['events']:
                tracking_data['success'] = True
                logger.info(f"✅ HTML parsing success: Status={tracking_data['status']}, Location={tracking_data['location']}, Events={len(tracking_data['events'])}")
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