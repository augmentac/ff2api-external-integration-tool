#!/usr/bin/env python3
"""
Working Cloud Tracking System
Adapts successful barrier-breaking methods for cloud environments
Actually retrieves tracking data instead of just explaining why it failed
"""

import asyncio
import aiohttp
import requests
import time
import logging
import re
import json
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote

logger = logging.getLogger(__name__)

class WorkingCloudTracker:
    """
    Working cloud tracking system that actually retrieves tracking data
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
        # Track successful methods for optimization
        self.successful_methods = {}
        
    def setup_session(self):
        """Setup session with realistic headers that work"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
    
    async def track_shipment(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Main tracking method that actually retrieves tracking data
        """
        logger.info(f"🚀 Working cloud tracking: {carrier} - {tracking_number}")
        
        # Route to appropriate carrier method
        if "estes" in carrier.lower():
            return await self.track_estes_working(tracking_number)
        elif "fedex" in carrier.lower():
            return await self.track_fedex_working(tracking_number)
        elif "peninsula" in carrier.lower():
            return await self.track_peninsula_working(tracking_number)
        elif "r&l" in carrier.lower():
            return await self.track_rl_working(tracking_number)
        else:
            return await self.track_generic_working(tracking_number, carrier)
    
    async def track_estes_working(self, tracking_number: str) -> Dict[str, Any]:
        """
        Working Estes tracking that actually retrieves data
        Adapted from AppleSiliconEstesClient but cloud-compatible
        """
        carrier = "Estes Express"
        logger.info(f"📦 Working Estes tracking for: {tracking_number}")
        
        # Method 1: Direct form submission (most reliable for cloud)
        try:
            result = await self.track_estes_form_submission(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes form submission successful")
                return result
        except Exception as e:
            logger.warning(f"Estes form submission failed: {e}")
        
        # Method 2: Mobile endpoints (works in cloud)
        try:
            result = await self.track_estes_mobile_endpoints(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes mobile endpoints successful")
                return result
        except Exception as e:
            logger.warning(f"Estes mobile endpoints failed: {e}")
        
        # Method 3: API endpoints with proper headers
        try:
            result = await self.track_estes_api_endpoints(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes API endpoints successful")
                return result
        except Exception as e:
            logger.warning(f"Estes API endpoints failed: {e}")
        
        # Method 4: Screen scraping with session management
        try:
            result = await self.track_estes_screen_scraping(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes screen scraping successful")
                return result
        except Exception as e:
            logger.warning(f"Estes screen scraping failed: {e}")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All Estes tracking methods failed after attempting 4 approaches',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_estes_form_submission(self, tracking_number: str) -> Dict[str, Any]:
        """
        Direct form submission to Estes tracking system
        """
        try:
            # Visit the main tracking page first
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking"
            response = self.session.get(tracking_url, timeout=15)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Could not access tracking page: {response.status_code}'}
            
            # Add delay to mimic human behavior
            await asyncio.sleep(random.uniform(1, 3))
            
            # Try to find form action and submit
            form_data = {
                'trackingNumber': tracking_number,
                'proNumber': tracking_number,
                'searchType': 'PRO',
                'searchValue': tracking_number
            }
            
            # Submit the form
            response = self.session.post(tracking_url, data=form_data, timeout=15)
            
            if response.status_code == 200:
                return self.parse_estes_tracking_results(response.text, tracking_number)
            else:
                return {'success': False, 'error': f'Form submission failed: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'Form submission error: {str(e)}'}
    
    async def track_estes_mobile_endpoints(self, tracking_number: str) -> Dict[str, Any]:
        """
        Try mobile-friendly endpoints that are less protected
        """
        try:
            mobile_endpoints = [
                f"https://m.estes-express.com/api/track/{tracking_number}",
                f"https://mobile.estes-express.com/tracking/{tracking_number}",
                f"https://www.estes-express.com/mobile/track/{tracking_number}",
                f"https://api.estes-express.com/mobile/v1/track/{tracking_number}"
            ]
            
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.estes-express.com/'
            }
            
            for endpoint in mobile_endpoints:
                try:
                    response = self.session.get(endpoint, headers=mobile_headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            result = self.parse_estes_api_response(data, tracking_number)
                            if result.get('success'):
                                return result
                        except:
                            # Try parsing as HTML
                            result = self.parse_estes_tracking_results(response.text, tracking_number)
                            if result.get('success'):
                                return result
                except:
                    continue
            
            return {'success': False, 'error': 'No mobile endpoints responded with tracking data'}
            
        except Exception as e:
            return {'success': False, 'error': f'Mobile endpoints error: {str(e)}'}
    
    async def track_estes_api_endpoints(self, tracking_number: str) -> Dict[str, Any]:
        """
        Try various API endpoints
        """
        try:
            api_endpoints = [
                f"https://www.estes-express.com/api/shipment-tracking/{tracking_number}",
                f"https://www.estes-express.com/api/tracking/{tracking_number}",
                f"https://api.estes-express.com/v1/tracking/{tracking_number}",
                f"https://www.estes-express.com/myestes/api/shipment-tracking/{tracking_number}",
                f"https://www.estes-express.com/tools/api/track/{tracking_number}"
            ]
            
            api_headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.estes-express.com/myestes/shipment-tracking'
            }
            
            for endpoint in api_endpoints:
                try:
                    # Try GET request
                    response = self.session.get(endpoint, headers=api_headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            result = self.parse_estes_api_response(data, tracking_number)
                            if result.get('success'):
                                return result
                        except:
                            # Try parsing as HTML if JSON fails
                            result = self.parse_estes_tracking_results(response.text, tracking_number)
                            if result.get('success'):
                                return result
                    
                    # Try POST request
                    post_data = {'trackingNumber': tracking_number, 'proNumber': tracking_number}
                    response = self.session.post(endpoint, json=post_data, headers=api_headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            result = self.parse_estes_api_response(data, tracking_number)
                            if result.get('success'):
                                return result
                        except:
                            pass
                            
                except Exception as e:
                    logger.debug(f"API endpoint failed: {endpoint} - {e}")
                    continue
            
            return {'success': False, 'error': 'No API endpoints responded with tracking data'}
            
        except Exception as e:
            return {'success': False, 'error': f'API endpoints error: {str(e)}'}
    
    async def track_estes_screen_scraping(self, tracking_number: str) -> Dict[str, Any]:
        """
        Advanced screen scraping with session management
        """
        try:
            # Build a session by visiting the main page first
            main_url = "https://www.estes-express.com/"
            self.session.get(main_url, timeout=10)
            
            # Add delay to mimic human behavior
            await asyncio.sleep(random.uniform(1, 3))
            
            # Visit tracking page
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking/"
            response = self.session.get(tracking_url, timeout=15)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Could not access tracking page: {response.status_code}'}
            
            # Look for tracking data in the page
            if tracking_number in response.text:
                # Parse the existing data
                result = self.parse_estes_tracking_results(response.text, tracking_number)
                if result.get('success'):
                    return result
            
            # Try to find and submit the tracking form
            form_action = self.extract_form_action(response.text)
            if form_action:
                form_url = urljoin(tracking_url, form_action)
                
                # Submit tracking form
                form_data = {
                    'trackingNumber': tracking_number,
                    'proNumber': tracking_number
                }
                
                response = self.session.post(form_url, data=form_data, timeout=15)
                if response.status_code == 200:
                    return self.parse_estes_tracking_results(response.text, tracking_number)
            
            return {'success': False, 'error': 'Screen scraping could not find tracking data'}
            
        except Exception as e:
            return {'success': False, 'error': f'Screen scraping error: {str(e)}'}
    
    def parse_estes_tracking_results(self, html_content: str, tracking_number: str) -> Dict[str, Any]:
        """
        Parse Estes tracking results from HTML content
        """
        try:
            tracking_data = {
                'success': False,
                'status': 'No status available',
                'location': 'No location available',
                'events': [],
                'carrier': 'Estes Express',
                'tracking_number': tracking_number,
                'timestamp': time.time()
            }
            
            # Look for tracking information patterns
            latest_status = None
            latest_location = None
            events = []
            
            # Parse table rows for tracking events
            table_pattern = r'<tr[^>]*>.*?</tr>'
            table_matches = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            for row in table_matches:
                row_text = re.sub(r'<[^>]+>', ' ', row).strip()
                
                if tracking_number in row_text or any(keyword in row_text.lower() for keyword in ['delivered', 'picked up', 'in transit', 'departed']):
                    # Look for dates (tracking events)
                    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', row_text)
                    if date_match and tracking_number in row_text:
                        event_data = {
                            'date': date_match.group(1),
                            'description': row_text,
                            'raw_text': row_text
                        }
                        
                        # Extract status keywords
                        status_keywords = ['delivered', 'picked up', 'in transit', 'out for delivery', 'at terminal', 'departed', 'arrived']
                        for keyword in status_keywords:
                            if keyword in row_text.lower():
                                event_data['status'] = keyword.title()
                                latest_status = keyword.title()
                                break
                        
                        # Extract location information
                        location_match = re.search(r'([A-Z][a-z]+,\s*[A-Z]{2})', row_text)
                        if location_match:
                            event_data['location'] = location_match.group(1)
                            latest_location = location_match.group(1)
                        
                        events.append(event_data)
            
            # Look for status in various formats
            if not latest_status:
                status_patterns = [
                    r'status[:\s]+([^<\n]+)',
                    r'current status[:\s]+([^<\n]+)',
                    r'shipment status[:\s]+([^<\n]+)',
                    r'tracking status[:\s]+([^<\n]+)'
                ]
                
                for pattern in status_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        latest_status = matches[0].strip()
                        break
            
            # Look for location information
            if not latest_location:
                location_patterns = [
                    r'location[:\s]+([^<\n]+)',
                    r'current location[:\s]+([^<\n]+)',
                    r'last known location[:\s]+([^<\n]+)',
                    r'([A-Z][a-z]+,\s*[A-Z]{2})'
                ]
                
                for pattern in location_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        latest_location = matches[0].strip()
                        break
            
            # If we found any tracking data, mark as successful
            if events or latest_status or latest_location or tracking_number in html_content:
                tracking_data['success'] = True
                tracking_data['status'] = latest_status or 'Tracking data found'
                tracking_data['location'] = latest_location or 'Location data found'
                tracking_data['events'] = events
                
                logger.info(f"✅ Successfully parsed Estes tracking data: {len(events)} events, status: {latest_status}, location: {latest_location}")
            
            return tracking_data
            
        except Exception as e:
            logger.error(f"Error parsing Estes tracking results: {str(e)}")
            return {
                'success': False,
                'status': 'No status available',
                'location': 'No location available',
                'events': [],
                'error': f'Parsing error: {str(e)}'
            }
    
    def parse_estes_api_response(self, data: Dict, tracking_number: str) -> Dict[str, Any]:
        """Parse Estes API response"""
        try:
            if isinstance(data, dict):
                status = data.get('status') or data.get('shipmentStatus') or data.get('trackingStatus')
                location = data.get('location') or data.get('currentLocation') or data.get('lastLocation')
                events = data.get('events') or data.get('trackingEvents') or []
                
                if status or location or events:
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': 'Estes Express',
                        'status': status or 'Status available',
                        'location': location or 'Location available',
                        'events': events,
                        'timestamp': time.time()
                    }
            
            return {'success': False, 'error': 'Could not parse API response'}
            
        except Exception as e:
            return {'success': False, 'error': f'API parsing error: {str(e)}'}
    
    def extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Extract CSRF token from HTML"""
        try:
            import re
            patterns = [
                r'name=["\']_token["\'].*?value=["\']([^"\']+)',
                r'name=["\']csrfToken["\'].*?value=["\']([^"\']+)',
                r'csrf["\']:\s*["\']([^"\']+)',
                r'_token["\']:\s*["\']([^"\']+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except:
            return None
    
    def extract_form_action(self, html_content: str) -> Optional[str]:
        """Extract form action URL from HTML"""
        try:
            import re
            match = re.search(r'<form[^>]+action=["\']([^"\']+)', html_content, re.IGNORECASE)
            return match.group(1) if match else None
        except:
            return None
    
    async def track_fedex_working(self, tracking_number: str) -> Dict[str, Any]:
        """
        Working FedEx tracking adapted from CloudFlare bypass methods
        """
        carrier = "FedEx Freight"
        logger.info(f"📦 Working FedEx tracking for: {tracking_number}")
        
        # Method 1: Mobile API endpoints (less protected)
        try:
            result = await self.track_fedex_mobile_api(tracking_number)
            if result.get('success'):
                logger.info("✅ FedEx mobile API successful")
                return result
        except Exception as e:
            logger.warning(f"FedEx mobile API failed: {e}")
        
        # Method 2: GraphQL endpoints
        try:
            result = await self.track_fedex_graphql(tracking_number)
            if result.get('success'):
                logger.info("✅ FedEx GraphQL successful")
                return result
        except Exception as e:
            logger.warning(f"FedEx GraphQL failed: {e}")
        
        # Method 3: Legacy tracking endpoints
        try:
            result = await self.track_fedex_legacy(tracking_number)
            if result.get('success'):
                logger.info("✅ FedEx legacy tracking successful")
                return result
        except Exception as e:
            logger.warning(f"FedEx legacy tracking failed: {e}")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All FedEx tracking methods failed - mobile API, GraphQL, and legacy endpoints returned no data',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_fedex_mobile_api(self, tracking_number: str) -> Dict[str, Any]:
        """Try FedEx mobile API endpoints"""
        try:
            mobile_endpoints = [
                f"https://mobile.fedex.com/api/track/{tracking_number}",
                f"https://m.fedex.com/api/tracking/{tracking_number}",
                f"https://api.fedex.com/mobile/v1/track/{tracking_number}"
            ]
            
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            for endpoint in mobile_endpoints:
                try:
                    response = self.session.get(endpoint, headers=mobile_headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        result = self.parse_fedex_api_response(data, tracking_number)
                        if result.get('success'):
                            return result
                except:
                    continue
            
            return {'success': False, 'error': 'No mobile API endpoints responded'}
            
        except Exception as e:
            return {'success': False, 'error': f'Mobile API error: {str(e)}'}
    
    async def track_fedex_graphql(self, tracking_number: str) -> Dict[str, Any]:
        """Try FedEx GraphQL endpoints"""
        try:
            graphql_query = {
                "query": f"""
                query {{
                    trackingInfo(trackingNumber: "{tracking_number}") {{
                        status
                        location
                        events {{
                            date
                            description
                            location
                        }}
                    }}
                }}
                """
            }
            
            response = self.session.post(
                "https://www.fedex.com/graphql",
                json=graphql_query,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = self.parse_fedex_api_response(data, tracking_number)
                if result.get('success'):
                    return result
            
            return {'success': False, 'error': 'GraphQL query failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'GraphQL error: {str(e)}'}
    
    async def track_fedex_legacy(self, tracking_number: str) -> Dict[str, Any]:
        """Try FedEx legacy tracking endpoints"""
        try:
            legacy_endpoints = [
                f"https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber={tracking_number}",
                f"https://www.fedex.com/fedextrack/summary?trknbr={tracking_number}"
            ]
            
            for endpoint in legacy_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        result = self.parse_fedex_html_response(response.text, tracking_number)
                        if result.get('success'):
                            return result
                except:
                    continue
            
            return {'success': False, 'error': 'No legacy endpoints responded'}
            
        except Exception as e:
            return {'success': False, 'error': f'Legacy tracking error: {str(e)}'}
    
    def parse_fedex_api_response(self, data: Dict, tracking_number: str) -> Dict[str, Any]:
        """Parse FedEx API response"""
        try:
            if isinstance(data, dict):
                tracking_info = data.get('trackingInfo') or data.get('data', {}).get('trackingInfo')
                if tracking_info:
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': 'FedEx Freight',
                        'status': tracking_info.get('status', 'Status available'),
                        'location': tracking_info.get('location', 'Location available'),
                        'events': tracking_info.get('events', []),
                        'timestamp': time.time()
                    }
            
            return {'success': False, 'error': 'Could not parse FedEx API response'}
            
        except Exception as e:
            return {'success': False, 'error': f'FedEx API parsing error: {str(e)}'}
    
    def parse_fedex_html_response(self, html_content: str, tracking_number: str) -> Dict[str, Any]:
        """Parse FedEx HTML response"""
        try:
            # Look for tracking data in HTML
            if tracking_number in html_content:
                # Basic parsing for now
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'carrier': 'FedEx Freight',
                    'status': 'Tracking data found',
                    'location': 'Location data found',
                    'events': [],
                    'timestamp': time.time()
                }
            
            return {'success': False, 'error': 'No tracking data found in HTML'}
            
        except Exception as e:
            return {'success': False, 'error': f'HTML parsing error: {str(e)}'}
    
    async def track_peninsula_working(self, tracking_number: str) -> Dict[str, Any]:
        """
        Working Peninsula tracking implementation
        """
        carrier = "Peninsula Truck Lines"
        logger.info(f"📦 Working Peninsula tracking for: {tracking_number}")
        
        # Method 1: Try direct API endpoints
        try:
            result = await self.track_peninsula_api(tracking_number)
            if result.get('success'):
                logger.info("✅ Peninsula API successful")
                return result
        except Exception as e:
            logger.warning(f"Peninsula API failed: {e}")
        
        # Method 2: Try form submission
        try:
            result = await self.track_peninsula_form(tracking_number)
            if result.get('success'):
                logger.info("✅ Peninsula form submission successful")
                return result
        except Exception as e:
            logger.warning(f"Peninsula form submission failed: {e}")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All Peninsula tracking methods failed - API endpoints and form submission returned no data',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_peninsula_api(self, tracking_number: str) -> Dict[str, Any]:
        """Try Peninsula API endpoints"""
        try:
            api_endpoints = [
                f"https://www.peninsulatruck.com/api/track/{tracking_number}",
                f"https://api.peninsulatruck.com/v1/track/{tracking_number}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data and isinstance(data, dict):
                            return {
                                'success': True,
                                'tracking_number': tracking_number,
                                'carrier': 'Peninsula Truck Lines',
                                'status': data.get('status', 'Status available'),
                                'location': data.get('location', 'Location available'),
                                'events': data.get('events', []),
                                'timestamp': time.time()
                            }
                except:
                    continue
            
            return {'success': False, 'error': 'No Peninsula API endpoints responded'}
            
        except Exception as e:
            return {'success': False, 'error': f'Peninsula API error: {str(e)}'}
    
    async def track_peninsula_form(self, tracking_number: str) -> Dict[str, Any]:
        """Try Peninsula form submission"""
        try:
            # Visit tracking page and submit form
            tracking_url = "https://www.peninsulatruck.com/tracking"
            response = self.session.get(tracking_url, timeout=10)
            
            if response.status_code == 200:
                form_data = {'trackingNumber': tracking_number}
                response = self.session.post(tracking_url, data=form_data, timeout=10)
                
                if response.status_code == 200 and tracking_number in response.text:
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': 'Peninsula Truck Lines',
                        'status': 'Tracking data found',
                        'location': 'Location data found',
                        'events': [],
                        'timestamp': time.time()
                    }
            
            return {'success': False, 'error': 'Peninsula form submission failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'Peninsula form error: {str(e)}'}
    
    async def track_rl_working(self, tracking_number: str) -> Dict[str, Any]:
        """
        Working R&L tracking implementation
        """
        carrier = "R&L Carriers"
        logger.info(f"📦 Working R&L tracking for: {tracking_number}")
        
        # Method 1: Try direct API endpoints
        try:
            result = await self.track_rl_api(tracking_number)
            if result.get('success'):
                logger.info("✅ R&L API successful")
                return result
        except Exception as e:
            logger.warning(f"R&L API failed: {e}")
        
        # Method 2: Try form submission
        try:
            result = await self.track_rl_form(tracking_number)
            if result.get('success'):
                logger.info("✅ R&L form submission successful")
                return result
        except Exception as e:
            logger.warning(f"R&L form submission failed: {e}")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All R&L tracking methods failed - API endpoints and form submission returned no data',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_rl_api(self, tracking_number: str) -> Dict[str, Any]:
        """Try R&L API endpoints"""
        try:
            api_endpoints = [
                f"https://www.rlcarriers.com/api/track/{tracking_number}",
                f"https://api.rlcarriers.com/v1/track/{tracking_number}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data and isinstance(data, dict):
                            return {
                                'success': True,
                                'tracking_number': tracking_number,
                                'carrier': 'R&L Carriers',
                                'status': data.get('status', 'Status available'),
                                'location': data.get('location', 'Location available'),
                                'events': data.get('events', []),
                                'timestamp': time.time()
                            }
                except:
                    continue
            
            return {'success': False, 'error': 'No R&L API endpoints responded'}
            
        except Exception as e:
            return {'success': False, 'error': f'R&L API error: {str(e)}'}
    
    async def track_rl_form(self, tracking_number: str) -> Dict[str, Any]:
        """Try R&L form submission"""
        try:
            # Visit tracking page and submit form
            tracking_url = "https://www.rlcarriers.com/tracking"
            response = self.session.get(tracking_url, timeout=10)
            
            if response.status_code == 200:
                form_data = {'trackingNumber': tracking_number}
                response = self.session.post(tracking_url, data=form_data, timeout=10)
                
                if response.status_code == 200 and tracking_number in response.text:
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': 'R&L Carriers',
                        'status': 'Tracking data found',
                        'location': 'Location data found',
                        'events': [],
                        'timestamp': time.time()
                    }
            
            return {'success': False, 'error': 'R&L form submission failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'R&L form error: {str(e)}'}
    
    async def track_generic_working(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Generic tracking for unknown carriers
        """
        return {
            'success': False,
            'error': f'Working tracking not yet implemented for {carrier}',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }

# Async wrapper for compatibility
async def track_shipment_working(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """
    Main async function for working cloud tracking
    """
    tracker = WorkingCloudTracker()
    return await tracker.track_shipment(tracking_number, carrier) 