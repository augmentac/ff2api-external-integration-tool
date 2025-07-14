#!/usr/bin/env python3
"""
Cloud-Native LTL Tracking System

Pure HTTP-based tracking system designed for Streamlit Cloud deployment.
No browser automation dependencies - uses advanced HTTP techniques for carrier tracking.
"""

import asyncio
import aiohttp
import json
import logging
import random
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib.parse
import ssl

logger = logging.getLogger(__name__)


class CloudNativeFingerprinter:
    """Advanced browser fingerprinting without selenium"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.device_profiles = {
            'desktop_chrome': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'viewport': {'width': 1920, 'height': 1080},
                'platform': 'Win32',
                'webgl_vendor': 'Google Inc. (Intel)',
                'webgl_renderer': 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'languages': ['en-US', 'en'],
                'timezone': 'America/New_York'
            },
            'desktop_firefox': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'viewport': {'width': 1920, 'height': 1080},
                'platform': 'Win32',
                'webgl_vendor': 'Intel Inc.',
                'webgl_renderer': 'Intel(R) UHD Graphics 620',
                'languages': ['en-US', 'en'],
                'timezone': 'America/New_York'
            },
            'mobile_chrome': {
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'viewport': {'width': 390, 'height': 844},
                'platform': 'iPhone',
                'webgl_vendor': 'Apple Inc.',
                'webgl_renderer': 'Apple GPU',
                'languages': ['en-US', 'en'],
                'timezone': 'America/New_York'
            }
        }
    
    def get_fingerprint(self, carrier: str) -> Dict[str, Any]:
        """Get optimized fingerprint for carrier"""
        carrier_lower = carrier.lower()
        
        # Carrier-specific profile selection
        if 'fedex' in carrier_lower:
            profile_key = 'desktop_chrome'  # FedEx works best with Chrome
        elif 'estes' in carrier_lower:
            profile_key = 'desktop_firefox'  # Estes prefers Firefox
        elif 'peninsula' in carrier_lower:
            profile_key = 'mobile_chrome'  # Peninsula has good mobile support
        else:
            profile_key = random.choice(list(self.device_profiles.keys()))
        
        return self.device_profiles[profile_key].copy()
    
    def get_headers(self, carrier: str, referer: str = None) -> Dict[str, str]:
        """Get realistic headers for carrier"""
        profile = self.get_fingerprint(carrier)
        
        headers = {
            'User-Agent': profile['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add Chrome-specific headers
        if 'chrome' in profile['user_agent'].lower():
            headers.update({
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            })
        
        if referer:
            headers['Referer'] = referer
        
        return headers


class CloudNativeSessionManager:
    """Advanced session management with connection pooling"""
    
    def __init__(self):
        self.sessions = {}
        self.fingerprinter = CloudNativeFingerprinter()
        self.session_timeouts = {}
        self.max_session_age = 300  # 5 minutes
    
    async def get_session(self, carrier: str) -> aiohttp.ClientSession:
        """Get or create session for carrier"""
        current_time = time.time()
        
        # Check if session exists and is still valid
        if carrier in self.sessions:
            session_time = self.session_timeouts.get(carrier, 0)
            if current_time - session_time < self.max_session_age:
                return self.sessions[carrier]
            else:
                # Session expired, close it
                await self.sessions[carrier].close()
                del self.sessions[carrier]
                del self.session_timeouts[carrier]
        
        # Create new session
        profile = self.fingerprinter.get_fingerprint(carrier)
        headers = self.fingerprinter.get_headers(carrier)
        
        # Create SSL context with proper settings
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=ssl_context,
            enable_cleanup_closed=True
        )
        
        # Create session with timeout
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        session = aiohttp.ClientSession(
            connector=connector,
            headers=headers,
            timeout=timeout,
            cookie_jar=aiohttp.CookieJar()
        )
        
        self.sessions[carrier] = session
        self.session_timeouts[carrier] = current_time
        
        return session
    
    async def close_all_sessions(self):
        """Close all sessions"""
        for session in self.sessions.values():
            await session.close()
        self.sessions.clear()
        self.session_timeouts.clear()


class CloudNativeTracker:
    """Cloud-native LTL tracking system"""
    
    def __init__(self):
        self.session_manager = CloudNativeSessionManager()
        self.fingerprinter = CloudNativeFingerprinter()
        self.logger = logging.getLogger(__name__)
        self.version = "2.0.1"  # Version identifier for deployment tracking
        
        # Tracking endpoints optimized for HTTP requests
        self.tracking_endpoints = {
            'fedex': [
                'https://www.fedex.com/fedextrack/?trackingnumber={}&cntry_code=us',
                'https://www.fedex.com/apps/fedextrack/?trackingnumber={}&cntry_code=us',
                'https://www.fedex.com/trackingCal/track?trackingnumber={}'
            ],
            'estes': [
                'https://www.estes-express.com/shipment-tracking?pro={}',
                'https://www.estes-express.com/myestes/shipment-tracking?pro={}',
                'https://www.estes-express.com/track?pro={}'
            ],
            'peninsula': [
                'https://www.peninsulatrucklines.com/tracking?pro={}',
                'https://peninsulatrucklines.azurewebsites.net/api/tracking?pro={}',
                'https://www.peninsulatrucklines.com/shipment-tracking?pro={}'
            ],
            'rl': [
                'https://www.rlcarriers.com',  # Main page with tracking form
                'https://www.rlcarriers.com/Track?pro={}',
                'https://www.rlcarriers.com/tracking?pro={}'
            ]
        }
        
        # Success tracking
        self.tracking_stats = {
            'total_attempts': 0,
            'successful_tracks': 0,
            'carrier_stats': {}
        }
    
    async def track_shipment(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """Track shipment using cloud-native methods"""
        start_time = time.time()
        
        # Map carrier names to internal format
        carrier_mapping = {
            'fedex freight priority': 'fedex',
            'fedex freight economy': 'fedex',
            'fedex freight': 'fedex',
            'fedex': 'fedex',
            'estes express': 'estes',
            'estes': 'estes',
            'peninsula truck lines inc': 'peninsula',
            'peninsula truck lines': 'peninsula',
            'peninsula': 'peninsula',
            'r&l carriers': 'rl',
            'rl carriers': 'rl',
            'r&l': 'rl',
            'rl': 'rl'
        }
        
        carrier_lower = carrier_mapping.get(carrier.lower(), carrier.lower())
        
        self.tracking_stats['total_attempts'] += 1
        
        if carrier_lower not in self.tracking_stats['carrier_stats']:
            self.tracking_stats['carrier_stats'][carrier_lower] = {
                'attempts': 0,
                'successes': 0
            }
        
        self.tracking_stats['carrier_stats'][carrier_lower]['attempts'] += 1
        
        self.logger.info(f"🚚 Starting cloud-native tracking for {tracking_number} on {carrier}")
        
        try:
            # Get session for this carrier
            session = await self.session_manager.get_session(carrier_lower)
            
            # Try different tracking methods
            result = await self._try_direct_endpoints(session, tracking_number, carrier_lower)
            if result and result.get('status') == 'success':
                self._record_success(carrier_lower)
                return result
            
            result = await self._try_form_submission(session, tracking_number, carrier_lower)
            if result and result.get('status') == 'success':
                self._record_success(carrier_lower)
                return result
            
            result = await self._try_api_endpoints(session, tracking_number, carrier_lower)
            if result and result.get('status') == 'success':
                self._record_success(carrier_lower)
                return result
            
            # All methods failed - return informative error with debugging info
            processing_time = time.time() - start_time
            
            # Provide carrier-specific guidance
            carrier_guidance = {
                'fedex': 'Try tracking directly at fedex.com/tracking',
                'estes': 'Try tracking directly at estes-express.com/shipment-tracking',
                'peninsula': 'Try tracking directly at peninsulatrucklines.com',
                'rl': 'Try tracking directly at rlcarriers.com'
            }
            
            guidance = carrier_guidance.get(carrier_lower, 'Try tracking directly on the carrier website')
            
            # Enhanced error information for debugging cloud deployment
            methods_attempted = ['direct_endpoints', 'form_submission', 'api_endpoints']
            
            # Log additional debugging info for cloud deployment
            self.logger.info(f"❌ All methods failed for {carrier_lower} - {tracking_number}")
            self.logger.info(f"🔍 Methods attempted: {methods_attempted}")
            self.logger.info(f"⏱️ Processing time: {processing_time:.2f}s")
            
            return {
                'status': 'error',
                'tracking_number': tracking_number,
                'carrier': carrier,
                'error': f'Cloud-native tracking attempted but failed for {carrier}',
                'explanation': f'All HTTP methods attempted. {guidance}',
                'processing_time': processing_time,
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': 'cloud_native_tracker_all_methods_failed',
                'methods_attempted': methods_attempted,
                'next_steps': f'Manual tracking recommended: {guidance}',
                'debug_info': {
                    'carrier_mapped': carrier_lower,
                    'total_attempts': self.tracking_stats['total_attempts'],
                    'successful_tracks': self.tracking_stats['successful_tracks'],
                    'cloud_deployment': True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Cloud-native tracking failed for {tracking_number}: {e}")
            processing_time = time.time() - start_time
            return {
                'status': 'error',
                'tracking_number': tracking_number,
                'carrier': carrier,
                'error': str(e),
                'explanation': f'Technical error occurred during tracking: {str(e)}',
                'processing_time': processing_time,
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': 'cloud_native_tracker_exception'
            }
    
    async def _try_direct_endpoints(self, session: aiohttp.ClientSession, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try direct endpoint access"""
        endpoints = self.tracking_endpoints.get(carrier, [])
        
        for endpoint in endpoints:
            try:
                url = endpoint.format(tracking_number)
                self.logger.info(f"🔍 Trying direct endpoint: {url}")
                
                # Add realistic delay
                await asyncio.sleep(random.uniform(1, 3))
                
                async with session.get(url) as response:
                    self.logger.info(f"📊 Direct endpoint response: {response.status} for {url}")
                    
                    if response.status == 200:
                        content = await response.text()
                        self.logger.debug(f"📄 Content length: {len(content)} chars")
                        
                        result = await self._parse_tracking_response(content, tracking_number, carrier, 'direct_endpoint')
                        if result:
                            self.logger.info(f"✅ Direct endpoint success: {url}")
                            return result
                        else:
                            self.logger.debug(f"❌ Direct endpoint parsing failed: {url}")
                    else:
                        self.logger.warning(f"⚠️ Direct endpoint failed with status {response.status}: {url}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"⏱️ Direct endpoint timeout: {endpoint}")
                continue
            except aiohttp.ClientError as e:
                self.logger.warning(f"🌐 Direct endpoint network error: {e}")
                continue
            except Exception as e:
                self.logger.error(f"❌ Direct endpoint unexpected error: {e}")
                continue
        
        self.logger.info(f"❌ All direct endpoints failed for {carrier}")
        return None
    
    async def _try_form_submission(self, session: aiohttp.ClientSession, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try form submission methods"""
        form_configs = {
            'fedex': {
                'url': 'https://www.fedex.com/apps/fedextrack/',
                'method': 'POST',
                'data': {
                    'data.trackingNumber': tracking_number,
                    'data.format': 'json',
                    'action': 'track'
                }
            },
            'estes': {
                'url': 'https://www.estes-express.com/shipment-tracking/track-shipment',
                'method': 'POST',
                'data': {
                    'pro': tracking_number,
                    'trackingAction': 'track'
                }
            },
            'peninsula': {
                'url': 'https://www.peninsulatrucklines.com/tracking',
                'method': 'POST',
                'data': {
                    'pro': tracking_number,
                    'action': 'track'
                }
            },
            'rl': {
                'url': 'https://www.rlcarriers.com',
                'method': 'POST',
                'data': {
                    'ctl00$cphBody$ToolsMenu$txtPro': tracking_number
                }
            }
        }
        
        if carrier not in form_configs:
            self.logger.debug(f"❌ No form configuration for {carrier}")
            return None
        
        config = form_configs[carrier]
        
        try:
            self.logger.info(f"📝 Trying form submission for {carrier}: {config['url']}")
            
            # Add realistic delay
            await asyncio.sleep(random.uniform(2, 4))
            
            # First get the form page to extract any CSRF tokens and hidden fields
            async with session.get(config['url']) as response:
                self.logger.info(f"📊 Form page response: {response.status} for {config['url']}")
                
                if response.status == 200:
                    form_html = await response.text()
                    soup = BeautifulSoup(form_html, 'html.parser')
                    
                    # Look for CSRF tokens
                    csrf_inputs = soup.find_all('input', {'name': re.compile(r'csrf|token|_token')})
                    for csrf_input in csrf_inputs:
                        csrf_name = csrf_input.get('name')
                        csrf_value = csrf_input.get('value')
                        if csrf_name and csrf_value:
                            config['data'][csrf_name] = csrf_value
                            self.logger.debug(f"🔐 Found CSRF token: {csrf_name}")
                    
                    # For ASP.NET forms (like R&L Carriers), get all hidden fields
                    if carrier == 'rl':
                        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
                        for hidden_input in hidden_inputs:
                            hidden_name = hidden_input.get('name')
                            hidden_value = hidden_input.get('value', '')
                            if hidden_name:
                                config['data'][hidden_name] = hidden_value
                                self.logger.debug(f"🔐 Found ASP.NET hidden field: {hidden_name}")
                else:
                    self.logger.warning(f"⚠️ Form page failed with status {response.status}")
            
            # Submit form
            if config['method'] == 'POST':
                self.logger.info(f"📤 Submitting form for {carrier}")
                async with session.post(config['url'], data=config['data']) as response:
                    self.logger.info(f"📊 Form submission response: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        self.logger.debug(f"📄 Form response content length: {len(content)} chars")
                        
                        result = await self._parse_tracking_response(content, tracking_number, carrier, 'form_submission')
                        if result:
                            self.logger.info(f"✅ Form submission success for {carrier}")
                            return result
                        else:
                            self.logger.debug(f"❌ Form submission parsing failed for {carrier}")
                    else:
                        self.logger.warning(f"⚠️ Form submission failed with status {response.status} for {carrier}")
                            
        except asyncio.TimeoutError:
            self.logger.warning(f"⏱️ Form submission timeout for {carrier}")
        except aiohttp.ClientError as e:
            self.logger.warning(f"🌐 Form submission network error for {carrier}: {e}")
        except Exception as e:
            self.logger.error(f"❌ Form submission unexpected error for {carrier}: {e}")
        
        return None
    
    async def _try_api_endpoints(self, session: aiohttp.ClientSession, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try API endpoint access"""
        api_configs = {
            'fedex': [
                {
                    'url': 'https://www.fedex.com/trackingCal/track',
                    'method': 'GET',
                    'params': {'trackingnumber': tracking_number, 'format': 'json'}
                },
                {
                    'url': 'https://www.fedex.com/apps/fedextrack/track',
                    'method': 'POST',
                    'json': {'trackingNumber': tracking_number}
                }
            ],
            'estes': [
                {
                    'url': 'https://www.estes-express.com/api/tracking',
                    'method': 'GET',
                    'params': {'pro': tracking_number}
                }
            ],
            'peninsula': [
                {
                    'url': 'https://peninsulatrucklines.azurewebsites.net/api/tracking',
                    'method': 'GET',
                    'params': {'pro': tracking_number}
                }
            ],
            'rl': [
                {
                    'url': 'https://www.rlcarriers.com/api/tracking',
                    'method': 'GET',
                    'params': {'pro': tracking_number}
                }
            ]
        }
        
        if carrier not in api_configs:
            return None
        
        configs = api_configs[carrier]
        
        for config in configs:
            try:
                # Add realistic delay
                await asyncio.sleep(random.uniform(1, 2))
                
                if config['method'] == 'GET':
                    async with session.get(config['url'], params=config.get('params', {})) as response:
                        if response.status == 200:
                            content = await response.text()
                            result = await self._parse_tracking_response(content, tracking_number, carrier, 'api_endpoint')
                            if result:
                                return result
                elif config['method'] == 'POST':
                    async with session.post(config['url'], json=config.get('json', {})) as response:
                        if response.status == 200:
                            content = await response.text()
                            result = await self._parse_tracking_response(content, tracking_number, carrier, 'api_endpoint')
                            if result:
                                return result
                                
            except Exception as e:
                self.logger.debug(f"API endpoint error for {carrier}: {e}")
                continue
        
        return None
    
    async def _parse_tracking_response(self, content: str, tracking_number: str, carrier: str, method: str) -> Optional[Dict[str, Any]]:
        """Parse tracking response from various formats"""
        try:
            # Try JSON parsing first
            try:
                data = json.loads(content)
                if self._contains_tracking_info(data, tracking_number):
                    return self._format_json_response(data, tracking_number, carrier, method)
            except json.JSONDecodeError:
                pass
            
            # Try HTML parsing
            if tracking_number in content:
                soup = BeautifulSoup(content, 'html.parser')
                return self._parse_html_response(soup, content, tracking_number, carrier, method)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Response parsing error: {e}")
            return None
    
    def _contains_tracking_info(self, data: Any, tracking_number: str) -> bool:
        """Check if data contains tracking information"""
        if isinstance(data, dict):
            for key, value in data.items():
                if tracking_number in str(value) or self._contains_tracking_info(value, tracking_number):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._contains_tracking_info(item, tracking_number):
                    return True
        elif isinstance(data, str):
            return tracking_number in data
        
        return False
    
    def _format_json_response(self, data: Dict, tracking_number: str, carrier: str, method: str) -> Dict[str, Any]:
        """Format JSON response into standard format"""
        return {
            'status': 'success',
            'tracking_number': tracking_number,
            'carrier': carrier,
            'tracking_status': 'Information Found',
            'tracking_event': f'Tracking data retrieved via {method}',
            'tracking_location': 'See details',
            'tracking_timestamp': datetime.now().isoformat(),
            'extracted_from': f'cloud_native_tracker_{method}',
            'raw_data': data
        }
    
    def _parse_html_response(self, soup: BeautifulSoup, content: str, tracking_number: str, carrier: str, method: str) -> Optional[Dict[str, Any]]:
        """Parse HTML response for tracking information"""
        # Look for common tracking patterns
        tracking_patterns = [
            r'delivered\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m?)\s+(.+)',
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m?)\s+delivered\s+(.+)',
            r'in\s+transit\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m?)\s+(.+)',
            r'picked\s+up\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m?)\s+(.+)'
        ]
        
        for pattern in tracking_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                match = matches[0]
                if len(match) >= 3:
                    return {
                        'status': 'success',
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'tracking_status': 'Delivered' if 'delivered' in pattern else 'In Transit',
                        'tracking_event': f'{match[0]} {match[1]} - {match[2]}',
                        'tracking_location': match[2].strip(),
                        'tracking_timestamp': datetime.now().isoformat(),
                        'extracted_from': f'cloud_native_tracker_{method}_html'
                    }
        
        # Enhanced pattern matching for different carriers
        carrier_patterns = {
            'fedex': [
                r'Package\s+delivered',
                r'Delivery\s+complete',
                r'Shipment\s+delivered'
            ],
            'estes': [
                r'POD\s+available',
                r'Delivery\s+confirmed',
                r'Shipment\s+delivered'
            ],
            'peninsula': [
                r'Delivered\s+to',
                r'Shipment\s+complete'
            ],
            'rl': [
                r'Delivered\s+on',
                r'Delivery\s+confirmed'
            ]
        }
        
        # Check carrier-specific patterns
        if carrier in carrier_patterns:
            for pattern in carrier_patterns[carrier]:
                if re.search(pattern, content, re.IGNORECASE):
                    return {
                        'status': 'success',
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'tracking_status': 'Delivered',
                        'tracking_event': 'Shipment delivered - see carrier website for details',
                        'tracking_location': 'Destination',
                        'tracking_timestamp': datetime.now().isoformat(),
                        'extracted_from': f'cloud_native_tracker_{method}_pattern'
                    }
        
        # Enhanced tracking number detection with more flexible matching
        content_lower = content.lower()
        tracking_lower = tracking_number.lower()
        
        # Check for tracking number in various formats
        tracking_found = any([
            tracking_number in content,
            tracking_lower in content_lower,
            tracking_number.replace('-', '') in content.replace('-', ''),
            tracking_number.replace(' ', '') in content.replace(' ', ''),
            # Handle PRO numbers with prefixes/suffixes
            any(variant in content for variant in [f"pro {tracking_number}", f"pro: {tracking_number}", f"#{tracking_number}"])
        ])
        
        if tracking_found:
            # Look for more specific status information
            status_found = 'Information Found'
            event_found = 'Tracking information located in response'
            location_found = 'See carrier website for details'
            
            # Enhanced status detection with better location and event extraction
            if any(word in content_lower for word in ['delivered', 'delivery complete', 'pod available']):
                status_found = 'Delivered'
                event_found = 'Shipment has been delivered'
                location_found = 'Destination'
                
                # Try to extract delivery date/time and location from content
                import re
                date_patterns = [
                    r'delivered\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                    r'delivery\s+date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                    r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})[^a-zA-Z]*delivered'
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        delivery_date = match.group(1)
                        event_found = f'Delivered on {delivery_date}'
                        break
                
                # Try to extract delivery location
                location_patterns = [
                    r'delivered\s+to[:\s]+([^,\n\r]{5,50})',
                    r'delivery\s+location[:\s]+([^,\n\r]{5,50})',
                    r'delivered\s+at[:\s]+([^,\n\r]{5,50})'
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        delivery_location = match.group(1).strip()
                        location_found = delivery_location[:50] if len(delivery_location) > 50 else delivery_location
                        break
                        
            elif any(word in content_lower for word in ['in transit', 'on route', 'en route']):
                status_found = 'In Transit'
                event_found = 'Shipment is in transit'
                location_found = 'In transit'
                
                # Try to extract current location
                location_patterns = [
                    r'location[:\s]+([^,\n\r]{5,50})',
                    r'current[:\s]+([^,\n\r]{5,50})',
                    r'at[:\s]+([^,\n\r]{5,50})'
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        current_location = match.group(1).strip()
                        location_found = current_location[:50] if len(current_location) > 50 else current_location
                        break
                        
            elif any(word in content_lower for word in ['picked up', 'collected', 'dispatched']):
                status_found = 'Picked Up'
                event_found = 'Shipment has been picked up'
                location_found = 'Origin'
                
                # Try to extract pickup date/time
                pickup_patterns = [
                    r'picked\s+up\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                    r'pickup\s+date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
                ]
                
                for pattern in pickup_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        pickup_date = match.group(1)
                        event_found = f'Picked up on {pickup_date}'
                        break
                        
            elif any(word in content_lower for word in ['out for delivery', 'out for del']):
                status_found = 'Out for Delivery'
                event_found = 'Shipment is out for delivery'
                location_found = 'Near destination'
                
                # Try to extract estimated delivery time
                delivery_patterns = [
                    r'estimated\s+delivery[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                    r'delivery\s+by[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
                ]
                
                for pattern in delivery_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        delivery_date = match.group(1)
                        event_found = f'Out for delivery - estimated delivery {delivery_date}'
                        break
                        
            elif any(word in content_lower for word in ['exception', 'delay', 'problem']):
                status_found = 'Exception'
                event_found = 'Shipment has an exception or delay'
                location_found = 'See carrier for details'
                
                # Try to extract exception details
                exception_patterns = [
                    r'exception[:\s]+([^,\n\r]{10,100})',
                    r'delay[:\s]+([^,\n\r]{10,100})',
                    r'problem[:\s]+([^,\n\r]{10,100})'
                ]
                
                for pattern in exception_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        exception_detail = match.group(1).strip()
                        event_found = f'Exception: {exception_detail[:100]}'
                        break
            
            return {
                'status': 'success',
                'tracking_number': tracking_number,
                'carrier': carrier,
                'tracking_status': status_found,
                'tracking_event': event_found,
                'tracking_location': location_found,
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': f'cloud_native_tracker_{method}_enhanced_v{self.version}'
            }
        
        # Check for any status indicators
        status_indicators = ['delivered', 'in transit', 'picked up', 'out for delivery', 'exception', 'delayed']
        for indicator in status_indicators:
            if indicator in content.lower():
                return {
                    'status': 'success',
                    'tracking_number': tracking_number,
                    'carrier': carrier,
                    'tracking_status': indicator.title(),
                    'tracking_event': f'Status: {indicator.title()}',
                    'tracking_location': 'See carrier website for details',
                    'tracking_timestamp': datetime.now().isoformat(),
                    'extracted_from': f'cloud_native_tracker_{method}_status'
                }
        
        return None
    
    def _record_success(self, carrier: str):
        """Record successful tracking"""
        self.tracking_stats['successful_tracks'] += 1
        self.tracking_stats['carrier_stats'][carrier]['successes'] += 1
    
    async def track_multiple_shipments(self, tracking_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Track multiple shipments concurrently"""
        start_time = time.time()
        
        self.logger.info(f"🚛 Starting bulk cloud-native tracking for {len(tracking_data)} shipments")
        
        # Create tasks for concurrent tracking
        tasks = []
        for tracking_number, carrier in tracking_data:
            task = asyncio.create_task(self.track_shipment(tracking_number, carrier))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_tracks = 0
        failed_tracks = 0
        carrier_breakdown = {}
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions
                tracking_number, carrier = tracking_data[i]
                processed_result = {
                    'status': 'error',
                    'tracking_number': tracking_number,
                    'carrier': carrier,
                    'error': str(result),
                    'tracking_timestamp': datetime.now().isoformat()
                }
                failed_tracks += 1
            else:
                processed_result = result
                if result.get('status') == 'success':
                    successful_tracks += 1
                else:
                    failed_tracks += 1
            
            processed_results.append(processed_result)
            
            # Update carrier breakdown
            carrier = processed_result.get('carrier', 'unknown')
            if carrier not in carrier_breakdown:
                carrier_breakdown[carrier] = {'total': 0, 'successful': 0, 'failed': 0}
            
            carrier_breakdown[carrier]['total'] += 1
            if processed_result.get('status') == 'success':
                carrier_breakdown[carrier]['successful'] += 1
            else:
                carrier_breakdown[carrier]['failed'] += 1
        
        processing_time = time.time() - start_time
        
        # Calculate success rate
        total_attempts = len(tracking_data)
        success_rate = f"{(successful_tracks / total_attempts * 100):.1f}%" if total_attempts > 0 else "0%"
        
        return {
            'summary': {
                'total_attempts': total_attempts,
                'successful_tracks': successful_tracks,
                'failed_tracks': failed_tracks,
                'overall_success_rate': success_rate,
                'processing_time': processing_time,
                'carrier_breakdown': carrier_breakdown,
                'enhancement_level': 'Cloud-Native HTTP Tracking'
            },
            'results': processed_results
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        total_attempts = self.tracking_stats['total_attempts']
        successful_tracks = self.tracking_stats['successful_tracks']
        
        current_success_rate = f"{(successful_tracks / total_attempts * 100):.1f}%" if total_attempts > 0 else "0%"
        
        return {
            'enhancement_level': 'Cloud-Native HTTP Tracking',
            'current_success_rate': current_success_rate,
            'phase_2_target': '15-25%',
            'proxy_integration': {'enabled': False, 'reason': 'Using direct HTTP requests'},
            'active_enhancements': [
                'Advanced HTTP fingerprinting',
                'Persistent session management',
                'Multi-endpoint fallback',
                'Intelligent response parsing',
                'Concurrent request processing'
            ],
            'tracking_attempts': total_attempts,
            'successful_tracks': successful_tracks,
            'failed_tracks': total_attempts - successful_tracks,
            'carrier_performance': self.tracking_stats['carrier_stats']
        }
    
    async def close(self):
        """Clean up resources"""
        await self.session_manager.close_all_sessions()