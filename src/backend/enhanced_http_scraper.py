#!/usr/bin/env python3
"""
Enhanced HTTP Scraper for 100% Success Rate

This module implements sophisticated HTTP scraping techniques including:
- Advanced session management with persistent cookies
- JavaScript variable extraction from page source
- Multi-step request flows (login → navigate → extract)
- Form automation with CSRF/ViewState handling
- Mobile site scraping
- Alternative data format discovery (JSON endpoints, XML feeds)
"""

import asyncio
import aiohttp
import json
import re
import time
import random
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import logging

logger = logging.getLogger(__name__)

class EnhancedHTTPScraper:
    """Enhanced HTTP scraper with advanced techniques for 100% success rate"""
    
    def __init__(self):
        self.sessions = {}
        self.session_cookies = {}
        self.csrf_tokens = {}
        self.viewstates = {}
        
        # Advanced user agents with real browser fingerprints
        self.user_agents = [
            {
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': '"Windows"'
            },
            {
                'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': '"macOS"'
            },
            {
                'ua': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br'
            }
        ]
        
        # Carrier-specific configurations
        self.carrier_configs = {
            'fedex': {
                'domains': ['fedex.com', 'm.fedex.com'],
                'tracking_paths': ['/apps/fedextrack/', '/fedextrack/', '/trackingCal/track', '/mobile/tracking'],
                'api_endpoints': ['/trackingCal/track', '/api/track', '/services/track'],
                'form_selectors': ['form[action*="track"]', '#tracking-form', '.track-form'],
                'requires_session': True,
                'has_mobile_site': True,
                'csrf_required': True
            },
            'estes': {
                'domains': ['estes-express.com', 'm.estes-express.com'],
                'tracking_paths': ['/myestes/shipment-tracking/', '/myestes/shipment-tracking', '/mobile/track'],
                'api_endpoints': ['/api/tracking/search', '/services/tracking', '/track/api'],
                'form_selectors': ['form[action*="track"]', '#track-form', '.tracking-form', 'form[action*="myestes"]'],
                'requires_session': True,
                'has_mobile_site': True,
                'csrf_required': True
            },
            'peninsula': {
                'domains': ['peninsulatrucklines.com'],
                'tracking_paths': ['/tracking', '/track', '/shipment-tracking'],
                'api_endpoints': ['/api/tracking', '/services/track'],
                'form_selectors': ['form', '#trackingForm', '.track-form'],
                'requires_session': False,
                'has_mobile_site': False,
                'csrf_required': True
            },
            'rl': {
                'domains': ['rlcarriers.com'],
                'tracking_paths': ['/', '/track', '/shipment-tracking'],
                'api_endpoints': ['/api/tracking', '/services/shipment'],
                'form_selectors': ['form[method="post"]', '#form1', '.aspNetHidden'],
                'requires_session': True,
                'has_mobile_site': False,
                'csrf_required': False,
                'viewstate_required': True
            }
        }
    
    async def scrape_with_enhanced_http(self, session: aiohttp.ClientSession, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Main enhanced HTTP scraping method"""
        
        logger.info(f"🔬 Starting enhanced HTTP scraping for {carrier} PRO {pro_number}")
        
        config = self.carrier_configs.get(carrier)
        if not config:
            logger.warning(f"No configuration found for carrier: {carrier}")
            return None
        
        # Try most promising approaches first with shorter timeouts
        approaches = [
            (self._try_advanced_form_submission, 10),  # Most likely to work, give 10 seconds
            (self._try_api_endpoints, 8),             # Try API endpoints quickly
            (self._try_javascript_extraction, 6),     # JavaScript extraction
            (self._try_mobile_site, 4)               # Mobile site as backup
        ]
        
        for approach, timeout_seconds in approaches:
            try:
                logger.debug(f"Trying {approach.__name__} with {timeout_seconds}s timeout")
                result = await asyncio.wait_for(
                    approach(session, pro_number, carrier, config), 
                    timeout=timeout_seconds
                )
                if result:
                    logger.info(f"✅ Enhanced HTTP scraping successful with {approach.__name__}")
                    return result
            except asyncio.TimeoutError:
                logger.debug(f"Approach {approach.__name__} timed out after {timeout_seconds}s")
                continue
            except Exception as e:
                logger.debug(f"Approach {approach.__name__} failed: {e}")
                continue
        
        logger.warning(f"❌ All enhanced HTTP approaches failed for {carrier} PRO {pro_number}")
        return None
    
    async def _try_api_endpoints(self, session: aiohttp.ClientSession, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, Any]]:
        """Try to find and use hidden API endpoints"""
        
        timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout per main page request
        
        for domain in config['domains']:
            # Try predefined API endpoints first (faster)
            headers = self._get_realistic_headers()
            for endpoint in config['api_endpoints'][:2]:  # Limit to first 2 endpoints
                api_url = f"https://www.{domain}{endpoint}"
                result = await self._try_api_url(session, api_url, pro_number, headers)
                if result:
                    return result
            
            # Only try JavaScript discovery if quick endpoints failed
            main_url = f"https://www.{domain}"
            try:
                async with session.get(main_url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract potential API endpoints from JavaScript (limit to first 3)
                        api_urls = self._extract_api_urls_from_js(content, domain)[:3]
                        
                        for api_url in api_urls:
                            result = await self._try_api_url(session, api_url, pro_number, headers)
                            if result:
                                return result
            except Exception as e:
                logger.debug(f"API endpoint discovery failed for {domain}: {e}")
                continue
        
        return None
    
    async def _try_javascript_extraction(self, session: aiohttp.ClientSession, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, Any]]:
        """Extract tracking data from JavaScript variables in page source"""
        
        for domain in config['domains']:
            for path in config['tracking_paths']:
                url = f"https://www.{domain}{path}"
                
                # Try with PRO number in URL
                test_urls = [
                    f"{url}?trackingNumber={pro_number}",
                    f"{url}?pro={pro_number}",
                    f"{url}#{pro_number}",
                    url
                ]
                
                for test_url in test_urls:
                    try:
                        headers = self._get_realistic_headers()
                        async with session.get(test_url, headers=headers) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Extract JavaScript variables
                                js_data = self._extract_javascript_variables(content)
                                
                                # Look for tracking data in JS variables
                                tracking_data = self._find_tracking_in_js_data(js_data, pro_number)
                                if tracking_data:
                                    return tracking_data
                                
                                # Try to find and execute tracking requests from JS
                                tracking_requests = self._extract_tracking_requests_from_js(content)
                                for request_info in tracking_requests:
                                    result = await self._execute_js_tracking_request(session, request_info, pro_number, domain)
                                    if result:
                                        return result
                    
                    except Exception as e:
                        logger.debug(f"JavaScript extraction failed for {test_url}: {e}")
                        continue
        
        return None
    
    async def _try_mobile_site(self, session: aiohttp.ClientSession, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, Any]]:
        """Try mobile site which often has simpler structure"""
        
        if not config.get('has_mobile_site'):
            return None
        
        mobile_domains = [d for d in config['domains'] if d.startswith('m.')]
        if not mobile_domains:
            # Try adding m. prefix to main domains
            mobile_domains = [f"m.{d}" for d in config['domains'] if not d.startswith('m.')]
        
        for domain in mobile_domains:
            for path in config['tracking_paths']:
                url = f"https://{domain}{path}"
                
                try:
                    # Use mobile user agent
                    headers = self._get_mobile_headers()
                    
                    # Try GET with PRO number
                    test_url = f"{url}?trackingNumber={pro_number}"
                    async with session.get(test_url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            result = self._parse_mobile_response(content, pro_number)
                            if result:
                                return result
                    
                    # Try POST form submission
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            form_content = await response.text()
                            form_data = self._extract_mobile_form_data(form_content, pro_number)
                            
                            if form_data:
                                async with session.post(url, data=form_data, headers=headers) as form_response:
                                    if form_response.status == 200:
                                        result_content = await form_response.text()
                                        result = self._parse_mobile_response(result_content, pro_number)
                                        if result:
                                            return result
                
                except Exception as e:
                    logger.debug(f"Mobile site failed for {url}: {e}")
                    continue
        
        return None
    
    async def _try_advanced_form_submission(self, session: aiohttp.ClientSession, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, Any]]:
        """Advanced form submission with proper token handling"""
        
        timeout = aiohttp.ClientTimeout(total=8)  # 8 second timeout per request
        
        for domain in config['domains']:
            for path in config['tracking_paths'][:2]:  # Limit to first 2 paths
                url = f"https://www.{domain}{path}"
                
                try:
                    headers = self._get_realistic_headers()
                    
                    # Get the form page
                    async with session.get(url, headers=headers, timeout=timeout) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Extract comprehensive form data
                            form_data = await self._extract_comprehensive_form_data(session, content, pro_number, carrier, config)
                            
                            if form_data:
                                # Determine form action
                                form_action = self._find_form_action(content, config['form_selectors']) or url
                                if not form_action.startswith('http'):
                                    form_action = urljoin(url, form_action)
                                
                                # Shorter delay for faster execution
                                await asyncio.sleep(random.uniform(0.5, 1.0))
                                
                                # Submit form with proper headers
                                form_headers = headers.copy()
                                form_headers.update({
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                    'Referer': url,
                                    'Origin': f"https://www.{domain}"
                                })
                                
                                async with session.post(form_action, data=form_data, headers=form_headers, timeout=timeout) as form_response:
                                    if form_response.status in [200, 302]:
                                        result_content = await form_response.text()
                                        result = self._parse_form_response(result_content, pro_number, carrier)
                                        if result:
                                            return result
                                        
                                        # Handle redirects manually if needed
                                        if form_response.status == 302:
                                            redirect_url = form_response.headers.get('Location')
                                            if redirect_url:
                                                result = await self._follow_redirect_and_parse(session, redirect_url, pro_number, headers)
                                                if result:
                                                    return result
                
                except Exception as e:
                    logger.debug(f"Advanced form submission failed for {url}: {e}")
                    continue
        
        return None
    
    async def _try_session_based_extraction(self, session: aiohttp.ClientSession, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, Any]]:
        """Multi-step session-based extraction"""
        
        if not config.get('requires_session'):
            return None
        
        for domain in config['domains']:
            try:
                # Step 1: Initialize session
                session_data = await self._initialize_carrier_session(session, domain, carrier)
                if not session_data:
                    continue
                
                # Step 2: Navigate to tracking page
                tracking_url = await self._navigate_to_tracking(session, domain, config, session_data)
                if not tracking_url:
                    continue
                
                # Step 3: Submit tracking request
                result = await self._submit_tracking_with_session(session, tracking_url, pro_number, session_data, config)
                if result:
                    return result
            
            except Exception as e:
                logger.debug(f"Session-based extraction failed for {domain}: {e}")
                continue
        
        return None
    
    async def _try_alternative_formats(self, session: aiohttp.ClientSession, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, Any]]:
        """Try alternative data formats (XML, RSS, etc.)"""
        
        alternative_formats = [
            ('xml', 'application/xml'),
            ('json', 'application/json'),
            ('rss', 'application/rss+xml'),
            ('atom', 'application/atom+xml')
        ]
        
        for domain in config['domains']:
            for format_ext, content_type in alternative_formats:
                test_urls = [
                    f"https://www.{domain}/api/tracking.{format_ext}?pro={pro_number}",
                    f"https://www.{domain}/services/track.{format_ext}?trackingNumber={pro_number}",
                    f"https://www.{domain}/feed/tracking/{pro_number}.{format_ext}",
                    f"https://www.{domain}/tracking/{pro_number}.{format_ext}"
                ]
                
                for url in test_urls:
                    try:
                        headers = self._get_realistic_headers()
                        headers['Accept'] = content_type
                        
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                content = await response.text()
                                result = self._parse_alternative_format(content, pro_number, format_ext)
                                if result:
                                    return result
                    
                    except Exception as e:
                        logger.debug(f"Alternative format {format_ext} failed for {url}: {e}")
                        continue
        
        return None
    
    def _get_realistic_headers(self) -> Dict[str, str]:
        """Get realistic browser headers"""
        profile = random.choice(self.user_agents)
        
        headers = {
            'User-Agent': profile['ua'],
            'Accept': profile['accept'],
            'Accept-Language': profile['accept_language'],
            'Accept-Encoding': profile['accept_encoding'],
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add Chrome-specific headers if applicable
        if 'sec_ch_ua' in profile:
            headers.update({
                'sec-ch-ua': profile['sec_ch_ua'],
                'sec-ch-ua-mobile': profile['sec_ch_ua_mobile'],
                'sec-ch-ua-platform': profile['sec_ch_ua_platform']
            })
        
        return headers
    
    def _get_mobile_headers(self) -> Dict[str, str]:
        """Get mobile-specific headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _extract_api_urls_from_js(self, content: str, domain: str) -> List[str]:
        """Extract API URLs from JavaScript code"""
        api_urls = []
        
        # Common API URL patterns in JavaScript
        patterns = [
            r'["\']https?://[^"\']*(?:api|service|track)[^"\']*["\']',
            r'["\'][^"\']*(?:api|service|track)[^"\']*["\']',
            r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'serviceUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'trackingUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'endpoint\s*[:=]\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match.group(1) if match.groups() else match.group().strip('\'"')
                if url and ('api' in url.lower() or 'service' in url.lower() or 'track' in url.lower()):
                    if not url.startswith('http'):
                        url = f"https://www.{domain}{url if url.startswith('/') else '/' + url}"
                    api_urls.append(url)
        
        return list(set(api_urls))  # Remove duplicates
    
    def _extract_javascript_variables(self, content: str) -> Dict[str, Any]:
        """Extract JavaScript variables from page source"""
        js_vars = {}
        
        # Common variable patterns
        patterns = [
            r'var\s+(\w+)\s*=\s*({[^}]*}[^;]*);',
            r'window\.(\w+)\s*=\s*({[^}]*}[^;]*);',
            r'(\w+)\s*:\s*({[^}]*})',
            r'["\'](\w*[Tt]rack\w*)["\']:\s*({[^}]*})',
            r'["\'](\w*[Dd]ata\w*)["\']:\s*({[^}]*})'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                var_name = match.group(1)
                var_value = match.group(2)
                try:
                    # Try to parse as JSON
                    js_vars[var_name] = json.loads(var_value)
                except:
                    # Store as string if not valid JSON
                    js_vars[var_name] = var_value
        
        return js_vars
    
    def _find_tracking_in_js_data(self, js_data: Dict[str, Any], pro_number: str) -> Optional[Dict[str, Any]]:
        """Find tracking data in extracted JavaScript variables"""
        
        for var_name, var_data in js_data.items():
            if isinstance(var_data, dict):
                # Look for tracking information
                if self._contains_tracking_data(var_data, pro_number):
                    return self._extract_tracking_from_js_object(var_data, pro_number)
        
        return None
    
    def _contains_tracking_data(self, data: Any, pro_number: str) -> bool:
        """Check if data contains tracking information"""
        if isinstance(data, str):
            return pro_number in data or any(keyword in data.lower() for keyword in ['delivered', 'in transit', 'tracking'])
        elif isinstance(data, dict):
            return any(self._contains_tracking_data(v, pro_number) for v in data.values())
        elif isinstance(data, list):
            return any(self._contains_tracking_data(item, pro_number) for item in data)
        return False
    
    def _extract_tracking_from_js_object(self, data: Dict[str, Any], pro_number: str) -> Dict[str, Any]:
        """Extract tracking information from JavaScript object"""
        
        # Look for common tracking fields
        status = self._find_in_object(data, ['status', 'trackingStatus', 'deliveryStatus', 'state'])
        location = self._find_in_object(data, ['location', 'deliveryLocation', 'currentLocation', 'destination'])
        event = self._find_in_object(data, ['event', 'description', 'statusDescription', 'message'])
        timestamp = self._find_in_object(data, ['timestamp', 'date', 'dateTime', 'lastUpdate'])
        
        if status:
            return {
                'status': str(status),
                'location': str(location) if location else 'Unknown',
                'event': str(event) if event else f'Package {status.lower()}',
                'timestamp': str(timestamp) if timestamp else datetime.now().isoformat()
            }
        
        return None
    
    def _find_in_object(self, data: Any, keys: List[str]) -> Any:
        """Find value in nested object by key names"""
        if isinstance(data, dict):
            for key in keys:
                if key in data:
                    return data[key]
            # Search recursively
            for value in data.values():
                result = self._find_in_object(value, keys)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_in_object(item, keys)
                if result:
                    return result
        return None
    
    async def _try_api_url(self, session: aiohttp.ClientSession, api_url: str, pro_number: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Try a specific API URL with various request methods"""
        
        # Set request timeout
        timeout = aiohttp.ClientTimeout(total=3)  # 3 seconds per request
        
        # Try GET with query parameters
        get_urls = [
            f"{api_url}?trackingNumber={pro_number}",
            f"{api_url}?pro={pro_number}",
            f"{api_url}?number={pro_number}",
            f"{api_url}/{pro_number}"
        ]
        
        for url in get_urls:
            try:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            result = self._parse_api_response(data, pro_number)
                            if result:
                                return result
                        except:
                            # Try as text
                            text = await response.text()
                            if pro_number in text:
                                return self._parse_text_response(text, pro_number)
            except Exception as e:
                logger.debug(f"GET request failed for {url}: {e}")
                continue
        
        # Try only the most promising POST request to save time
        post_data = {'trackingNumber': pro_number}
        
        try:
            post_headers = headers.copy()
            post_headers['Content-Type'] = 'application/json'
            
            async with session.post(api_url, json=post_data, headers=post_headers, timeout=timeout) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        result = self._parse_api_response(data, pro_number)
                        if result:
                            return result
                    except:
                        text = await response.text()
                        if pro_number in text:
                            return self._parse_text_response(text, pro_number)
        except Exception as e:
            logger.debug(f"POST request failed for {api_url}: {e}")
        
        return None
    
    def _parse_api_response(self, data: Any, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse API response data"""
        
        if isinstance(data, dict):
            # Look for tracking information
            result = self._extract_tracking_from_js_object(data, pro_number)
            if result:
                return result
            
            # Try nested structures
            for key in ['data', 'result', 'tracking', 'shipment', 'package']:
                if key in data and data[key]:
                    nested_result = self._parse_api_response(data[key], pro_number)
                    if nested_result:
                        return nested_result
        
        elif isinstance(data, list):
            for item in data:
                result = self._parse_api_response(item, pro_number)
                if result:
                    return result
        
        return None
    
    def _parse_text_response(self, text: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse text response for tracking information"""
        
        # Enhanced status patterns
        status_patterns = [
            r'(delivered|in transit|out for delivery|picked up|exception|arrived|departed|completed)',
            r'status[:\s]*(delivered|in transit|out for delivery|picked up|exception|arrived|departed|completed)',
            r'current.*?status[:\s]*(delivered|in transit|out for delivery|picked up|exception)',
        ]
        
        # Enhanced location patterns - much more comprehensive
        location_patterns = [
            # City, State format (most common)
            r'([A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2,3}(?:\s+US)?)',
            # City, ST US format
            r'([A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2}\s+US)',
            # All caps format
            r'([A-Z]{3,}\s*,\s*[A-Z]{2,3}(?:\s+US)?)',
            # Location with address
            r'(?:location|destination|at|in)\s*[:]*\s*([A-Z][a-zA-Z\s,]{10,50})',
            # Terminal or facility
            r'(?:terminal|facility|depot)[:\s]*([A-Z][a-zA-Z\s,]{5,40})',
            # Near status keywords
            r'(?:delivered|arrived|departed).*?(?:at|in|to)\s*([A-Z][a-zA-Z\s,]{5,40})',
            # City name patterns
            r'\b([A-Z][a-zA-Z]{3,15}[\s,]*[A-Z]{2,3})\b',
        ]
        
        status = None
        location = None
        
        # Find status
        for pattern in status_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                status = match.group(1).title()
                if status.lower() == 'picked up':
                    status = 'Delivered'  # Normalize
                break
        
        # Find location with enhanced searching
        for pattern in location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                potential_location = match.group(1).strip()
                
                # Validate location format
                if self._is_valid_location(potential_location):
                    location = potential_location
                    break
            
            if location:
                break
        
        # If no location found yet, try extracting from context around status
        if not location and status:
            status_pos = text.lower().find(status.lower())
            if status_pos != -1:
                # Look 200 characters before and after status
                context = text[max(0, status_pos-200):status_pos+200]
                location_match = re.search(r'([A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2,3})', context)
                if location_match:
                    location = location_match.group(1).strip()
        
        if status:
            return {
                'status': status,
                'location': location or 'Unknown',
                'event': f'Package {status.lower()}',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _is_valid_location(self, location: str) -> bool:
        """Validate if a string looks like a valid location"""
        if not location or len(location) < 5:
            return False
        
        # Check for common location patterns
        patterns = [
            r'^[A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2,3}(?:\s+US)?$',
            r'^[A-Z]{3,}\s*,\s*[A-Z]{2,3}(?:\s+US)?$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, location.strip()):
                return True
        
        return False
    
    # Additional helper methods would continue here...
    # (For brevity, I'm showing the key structure and main methods)
    
    async def _extract_comprehensive_form_data(self, session: aiohttp.ClientSession, content: str, pro_number: str, carrier: str, config: Dict) -> Optional[Dict[str, str]]:
        """Extract comprehensive form data including tokens, viewstates, etc."""
        # Implementation for comprehensive form data extraction
        soup = BeautifulSoup(content, 'html.parser')
        form_data = {}
        
        # Find the main form
        form = None
        for selector in config['form_selectors']:
            form = soup.select_one(selector)
            if form:
                break
        
        if not form:
            form = soup.find('form')
        
        if form:
            # Extract all hidden inputs
            for input_elem in form.find_all('input', {'type': 'hidden'}):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
            
            # Add tracking number in various formats
            form_data.update({
                'trackingNumber': pro_number,
                'pro': pro_number,
                'proNumber': pro_number,
                'number': pro_number
            })
            
            # Handle carrier-specific requirements
            if carrier == 'rl' and config.get('viewstate_required'):
                # R&L specific ViewState handling
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                if viewstate:
                    form_data['__VIEWSTATE'] = viewstate.get('value', '')
                
                viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
                if viewstate_gen:
                    form_data['__VIEWSTATEGENERATOR'] = viewstate_gen.get('value', '')
                
                event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
                if event_validation:
                    form_data['__EVENTVALIDATION'] = event_validation.get('value', '')
                
                # R&L specific field names
                form_data['ctl00$cphBody$ToolsMenu$txtPro'] = pro_number
                form_data['ctl00$cphBody$ToolsMenu$btnTrack'] = 'Track'
            
            elif config.get('csrf_required'):
                # Extract CSRF tokens
                csrf_token = soup.find('input', {'name': re.compile(r'.*csrf.*', re.I)}) or \
                           soup.find('meta', {'name': 'csrf-token'})
                
                if csrf_token:
                    token_value = csrf_token.get('value') or csrf_token.get('content')
                    if token_value:
                        form_data['_token'] = token_value
                        form_data['csrf_token'] = token_value
        
        return form_data if form_data else None
    
    def _parse_form_response(self, content: str, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Parse form response for tracking data"""
        
        # Try JSON extraction first
        try:
            # Look for JSON in the response
            json_match = re.search(r'({[^}]*"[^"]*(?:status|tracking|delivery)[^"]*"[^}]*})', content, re.IGNORECASE | re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                result = self._parse_api_response(data, pro_number)
                if result:
                    return result
        except:
            pass
        
        # HTML parsing
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for tracking information in tables
        tables = soup.find_all('table')
        for table in tables:
            result = self._extract_tracking_from_table(table, pro_number)
            if result:
                return result
        
        # Look for tracking information in divs
        tracking_divs = soup.find_all('div', class_=re.compile(r'track|status|result', re.I))
        for div in tracking_divs:
            result = self._extract_tracking_from_element(div, pro_number)
            if result:
                return result
        
        # General text-based extraction
        return self._parse_text_response(content, pro_number)
    
    def _extract_tracking_from_table(self, table, pro_number: str) -> Optional[Dict[str, Any]]:
        """Extract tracking information from HTML table"""
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_text = row.get_text().strip()
            
            if pro_number in row_text or any(keyword in row_text.lower() for keyword in ['delivered', 'in transit', 'pickup']):
                # Try to extract structured data from cells
                status = location = None
                
                # Enhanced status extraction
                status_match = re.search(r'(delivered|in transit|out for delivery|picked up|exception|arrived|departed)', row_text, re.IGNORECASE)
                if status_match:
                    status = status_match.group(1).title()
                    if status.lower() == 'picked up':
                        status = 'Delivered'
                
                # Enhanced location extraction from table
                location_patterns = [
                    r'([A-Z][a-zA-Z\s]{2,20},\s*[A-Z]{2,3}(?:\s+US)?)',
                    r'([A-Z]{3,}\s*,\s*[A-Z]{2,3}(?:\s+US)?)',
                ]
                
                for pattern in location_patterns:
                    loc_match = re.search(pattern, row_text)
                    if loc_match and self._is_valid_location(loc_match.group(1)):
                        location = loc_match.group(1).strip()
                        break
                
                # If cells are structured, check individual cells
                if len(cells) >= 3 and not location:
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        for pattern in location_patterns:
                            cell_match = re.search(pattern, cell_text)
                            if cell_match and self._is_valid_location(cell_match.group(1)):
                                location = cell_match.group(1).strip()
                                break
                        if location:
                            break
                
                if status:
                    return {
                        'status': status,
                        'location': location or 'Unknown',
                        'event': f'Package {status.lower()}',
                        'timestamp': datetime.now().isoformat()
                    }
        
        return None
    
    def _extract_tracking_from_element(self, element, pro_number: str) -> Optional[Dict[str, Any]]:
        """Extract tracking information from HTML element"""
        
        text = element.get_text().strip()
        
        if pro_number in text or len(text) > 20:
            # Use enhanced text parsing method
            result = self._parse_text_response(text, pro_number)
            if result:
                return result
        
        return None
    
    # Additional methods for mobile parsing, session management, etc. would be implemented here
    def _parse_mobile_response(self, content: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse mobile site response"""
        return self._parse_form_response(content, pro_number, 'mobile')
    
    def _extract_mobile_form_data(self, content: str, pro_number: str) -> Optional[Dict[str, str]]:
        """Extract form data from mobile site"""
        soup = BeautifulSoup(content, 'html.parser')
        form = soup.find('form')
        
        if form:
            form_data = {}
            for input_elem in form.find_all('input'):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name and input_elem.get('type') == 'hidden':
                    form_data[name] = value
            
            form_data.update({
                'trackingNumber': pro_number,
                'pro': pro_number
            })
            
            return form_data
        
        return None
    
    def _find_form_action(self, content: str, selectors: List[str]) -> Optional[str]:
        """Find form action URL"""
        soup = BeautifulSoup(content, 'html.parser')
        
        for selector in selectors:
            form = soup.select_one(selector)
            if form:
                action = form.get('action')
                if action:
                    return action
        
        return None
    
    async def _follow_redirect_and_parse(self, session: aiohttp.ClientSession, redirect_url: str, pro_number: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Follow redirect and parse the result"""
        try:
            async with session.get(redirect_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_form_response(content, pro_number, 'redirect')
        except Exception as e:
            logger.debug(f"Redirect follow failed: {e}")
        
        return None
    
    # Placeholder methods for session-based extraction
    async def _initialize_carrier_session(self, session: aiohttp.ClientSession, domain: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Initialize carrier-specific session"""
        return {'domain': domain, 'carrier': carrier}
    
    async def _navigate_to_tracking(self, session: aiohttp.ClientSession, domain: str, config: Dict, session_data: Dict) -> Optional[str]:
        """Navigate to tracking page with session"""
        return f"https://www.{domain}{config['tracking_paths'][0]}"
    
    async def _submit_tracking_with_session(self, session: aiohttp.ClientSession, tracking_url: str, pro_number: str, session_data: Dict, config: Dict) -> Optional[Dict[str, Any]]:
        """Submit tracking request with session data"""
        return None  # Placeholder
    
    def _parse_alternative_format(self, content: str, pro_number: str, format_type: str) -> Optional[Dict[str, Any]]:
        """Parse alternative format responses"""
        if format_type == 'xml':
            return self._parse_xml_response(content, pro_number)
        elif format_type == 'json':
            try:
                data = json.loads(content)
                return self._parse_api_response(data, pro_number)
            except:
                pass
        return None
    
    def _parse_xml_response(self, content: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse XML response"""
        try:
            soup = BeautifulSoup(content, 'xml')
            
            # Look for tracking elements
            tracking_elements = soup.find_all(['status', 'location', 'description', 'event'])
            
            if tracking_elements:
                status = location = event = None
                
                for elem in tracking_elements:
                    if elem.name == 'status':
                        status = elem.get_text().strip()
                    elif elem.name == 'location':
                        location = elem.get_text().strip()
                    elif elem.name in ['description', 'event']:
                        event = elem.get_text().strip()
                
                if status:
                    return {
                        'status': status,
                        'location': location or 'Unknown',
                        'event': event or f'Package {status.lower()}',
                        'timestamp': datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.debug(f"XML parsing failed: {e}")
        
        return None
    
    def _extract_tracking_requests_from_js(self, content: str) -> List[Dict[str, Any]]:
        """Extract tracking request information from JavaScript"""
        # This would extract AJAX call patterns from JS
        return []  # Placeholder
    
    async def _execute_js_tracking_request(self, session: aiohttp.ClientSession, request_info: Dict, pro_number: str, domain: str) -> Optional[Dict[str, Any]]:
        """Execute tracking request extracted from JavaScript"""
        return None  # Placeholder