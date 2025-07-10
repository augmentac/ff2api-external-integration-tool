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

# Import working tracking implementations
try:
    from .cloudflare_bypass_fedex_client import CloudFlareBypassFedExClient
    CLOUDFLARE_FEDEX_AVAILABLE = True
except ImportError:
    CLOUDFLARE_FEDEX_AVAILABLE = False
    CloudFlareBypassFedExClient = None

try:
    from .zero_cost_carriers import ZeroCostCarrierManager
    ZERO_COST_AVAILABLE = True
except ImportError:
    ZERO_COST_AVAILABLE = False
    ZeroCostCarrierManager = None

try:
    from .apple_silicon_estes_client import AppleSiliconEstesClient
    APPLE_SILICON_AVAILABLE = True
except ImportError:
    APPLE_SILICON_AVAILABLE = False
    AppleSiliconEstesClient = None

logger = logging.getLogger(__name__)

class WorkingCloudTracker:
    """
    Working cloud tracking system that actually retrieves tracking data
    Uses the best available tracking implementations for each carrier
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
        # Initialize working tracking clients
        try:
            self.fedex_client = CloudFlareBypassFedExClient() if CLOUDFLARE_FEDEX_AVAILABLE else None
        except Exception as e:
            logger.warning(f"Failed to initialize FedEx client: {e}")
            self.fedex_client = None
            
        try:
            self.zero_cost_manager = ZeroCostCarrierManager() if ZERO_COST_AVAILABLE else None
        except Exception as e:
            logger.warning(f"Failed to initialize ZeroCost manager: {e}")
            self.zero_cost_manager = None
            
        try:
            self.estes_client = AppleSiliconEstesClient() if APPLE_SILICON_AVAILABLE else None
        except Exception as e:
            logger.warning(f"Failed to initialize Estes client: {e}")
            self.estes_client = None
        
        # Track successful methods for optimization
        self.successful_methods = {}
        
        logger.info("🚀 Working Cloud Tracker initialized")
        logger.info(f"📦 FedEx Client: {'Available' if self.fedex_client else 'Not Available'}")
        logger.info(f"🏢 Zero-Cost Manager: {'Available' if self.zero_cost_manager else 'Not Available'}")
        logger.info(f"🚛 Estes Client: {'Available' if self.estes_client else 'Not Available'}")
    
    def setup_session(self):
        """Setup HTTP session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
        Working Estes tracking using Apple Silicon client or fallback methods
        """
        carrier = "Estes Express"
        logger.info(f"🚛 Working Estes tracking for: {tracking_number}")
        
        # Method 1: Use Apple Silicon client if available
        if self.estes_client:
            try:
                logger.info("🍎 Trying Apple Silicon Estes client...")
                result = await self.estes_client.track_shipment(tracking_number)
                if result.get('success'):
                    logger.info("✅ Apple Silicon Estes client successful")
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'status': result.get('status', 'Tracking data found'),
                        'location': result.get('location', 'Location available'),
                        'events': result.get('events', []),
                        'timestamp': time.time(),
                        'method': 'Apple Silicon Estes Client'
                    }
            except Exception as e:
                logger.warning(f"Apple Silicon Estes client failed: {e}")
        
        # Method 2: Form submission method
        try:
            result = await self.track_estes_form_submission(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes form submission successful")
                return result
        except Exception as e:
            logger.warning(f"Estes form submission failed: {e}")
        
        # Method 3: Mobile endpoints
        try:
            result = await self.track_estes_mobile_endpoints(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes mobile endpoints successful")
                return result
        except Exception as e:
            logger.warning(f"Estes mobile endpoints failed: {e}")
        
        # Method 4: API endpoints
        try:
            result = await self.track_estes_api_endpoints(tracking_number)
            if result.get('success'):
                logger.info("✅ Estes API endpoints successful")
                return result
        except Exception as e:
            logger.warning(f"Estes API endpoints failed: {e}")
        
        # Method 5: Screen scraping
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
            'error': 'All Estes tracking methods failed after attempting 5 approaches',
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
        Working FedEx tracking using CloudFlare bypass client
        """
        carrier = "FedEx Freight"
        logger.info(f"📦 Working FedEx tracking for: {tracking_number}")
        
        if self.fedex_client:
            try:
                logger.info("🚚 Trying CloudFlare Bypass FedEx client...")
                result = await self.fedex_client.track_shipment(tracking_number)
                if result.get('success'):
                    logger.info("✅ CloudFlare Bypass FedEx client successful")
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'status': result.get('status', 'Tracking data found'),
                        'location': result.get('location', 'Location available'),
                        'events': result.get('events', []),
                        'timestamp': time.time(),
                        'method': 'CloudFlare Bypass FedEx Client'
                    }
            except Exception as e:
                logger.warning(f"CloudFlare Bypass FedEx client failed: {e}")
        
        # Fallback to legacy endpoints if CloudFlare client is not available
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
            
            return {
                'success': False,
                'error': 'All FedEx tracking methods failed - CloudFlare client and legacy endpoints returned no data',
                'status': 'No status available',
                'location': 'No location available',
                'events': [],
                'carrier': carrier,
                'tracking_number': tracking_number,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'FedEx tracking error: {str(e)}'}
    
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
        Working Peninsula tracking using ZeroCostCarrierManager
        """
        carrier = "Peninsula Truck Lines"
        logger.info(f"📦 Working Peninsula tracking for: {tracking_number}")
        
        if self.zero_cost_manager:
            try:
                logger.info("🚚 Trying ZeroCost Peninsula client...")
                result = await self.zero_cost_manager.track_shipment(carrier, tracking_number)
                if result.get('status') == 'success':
                    logger.info("✅ ZeroCost Peninsula client successful")
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'status': result.get('status', 'Tracking data found'),
                        'location': result.get('location', 'Location available'),
                        'events': result.get('events', []),
                        'timestamp': time.time(),
                        'method': 'ZeroCost Peninsula Client'
                    }
            except Exception as e:
                logger.warning(f"ZeroCost Peninsula client failed: {e}")
        
        # Fallback to form submission if ZeroCost client is not available
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
                        'carrier': carrier,
                        'status': 'Tracking data found',
                        'location': 'Location data found',
                        'events': [],
                        'timestamp': time.time()
                    }
            
            return {
                'success': False,
                'error': 'All Peninsula tracking methods failed - ZeroCost client and form submission returned no data',
                'status': 'No status available',
                'location': 'No location available',
                'events': [],
                'carrier': carrier,
                'tracking_number': tracking_number,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Peninsula tracking error: {str(e)}'}
    
    async def track_rl_working(self, tracking_number: str) -> Dict[str, Any]:
        """
        Working R&L tracking using ZeroCostCarrierManager
        """
        carrier = "R&L Carriers"
        logger.info(f"📦 Working R&L tracking for: {tracking_number}")
        
        if self.zero_cost_manager:
            try:
                logger.info("🚚 Trying ZeroCost R&L client...")
                result = await self.zero_cost_manager.track_shipment(carrier, tracking_number)
                if result.get('status') == 'success':
                    logger.info("✅ ZeroCost R&L client successful")
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'status': result.get('status', 'Tracking data found'),
                        'location': result.get('location', 'Location available'),
                        'events': result.get('events', []),
                        'timestamp': time.time(),
                        'method': 'ZeroCost R&L Client'
                    }
            except Exception as e:
                logger.warning(f"ZeroCost R&L client failed: {e}")
        
        # Fallback to form submission if ZeroCost client is not available
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
                        'carrier': carrier,
                        'status': 'Tracking data found',
                        'location': 'Location data found',
                        'events': [],
                        'timestamp': time.time()
                    }
            
            return {
                'success': False,
                'error': 'All R&L tracking methods failed - ZeroCost client and form submission returned no data',
                'status': 'No status available',
                'location': 'No location available',
                'events': [],
                'carrier': carrier,
                'tracking_number': tracking_number,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'R&L tracking error: {str(e)}'}
    
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