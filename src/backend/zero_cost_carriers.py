#!/usr/bin/env python3
"""
Zero-Cost Carrier-Specific Implementations

Advanced scraping techniques for Peninsula, FedEx, and Estes without external costs.
"""

import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .zero_cost_anti_scraping import ZeroCostAntiScrapingSystem


class PeninsulaZeroCostTracker:
    """Zero-cost Peninsula Truck Lines tracking implementation"""
    
    def __init__(self, anti_scraping_system: ZeroCostAntiScrapingSystem):
        self.logger = logging.getLogger(__name__)
        self.anti_scraping = anti_scraping_system
        self.base_url = "https://www.peninsulatrucklines.com"
        self.api_base = "https://peninsulatrucklines.azurewebsites.net"
        
        # Peninsula-specific patterns
        self.delivery_patterns = [
            r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}(?:am|pm))\s+Delivered\s+([A-Z\s,]+)',
            r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2})\s+Delivered\s+([A-Z\s,]+)',
            r'Delivered\s+(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}(?:am|pm))\s+([A-Z\s,]+)'
        ]
    
    async def track_pro(self, pro_number: str) -> Dict[str, Any]:
        """Track Peninsula PRO with zero-cost methods"""
        try:
            # Create stealth session
            session = self.anti_scraping.create_stealth_session("peninsula")
            
            # Warm up session
            self.anti_scraping.warm_session(session, "peninsulatrucklines.com")
            
            # Try multiple approaches
            result = await self._try_react_state_extraction(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            result = await self._try_api_reverse_engineering(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            result = await self._try_mobile_site(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            return {
                'status': 'error',
                'message': 'Unable to bypass Peninsula anti-scraping measures',
                'pro_number': pro_number
            }
            
        except Exception as e:
            self.logger.error(f"Peninsula tracking failed: {e}")
            return {
                'status': 'error',
                'message': f'Peninsula tracking error: {str(e)}',
                'pro_number': pro_number
            }
    
    async def _try_react_state_extraction(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Extract data from React application state"""
        try:
            # Get main tracking page with JavaScript rendering
            tracking_url = f"{self.base_url}/tracking"
            
            # Render JavaScript content
            html_content = await self.anti_scraping.render_javascript_page(tracking_url)
            if not html_content:
                return None
            
            # Parse rendered HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for React state in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract initial state
                    state_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', script.string)
                    if state_match:
                        try:
                            state_data = json.loads(state_match.group(1))
                            # Process state data for tracking info
                            tracking_info = self._extract_tracking_from_state(state_data, pro_number)
                            if tracking_info:
                                return tracking_info
                        except json.JSONDecodeError:
                            continue
            
            # Look for tracking data in any script tag
            for script in script_tags:
                if script.string and pro_number in script.string:
                    # Extract tracking data using regex
                    tracking_data = self._extract_tracking_from_script(script.string, pro_number)
                    if tracking_data:
                        return tracking_data
            
            return None
            
        except Exception as e:
            self.logger.debug(f"React state extraction failed: {e}")
            return None
    
    def _extract_tracking_from_state(self, state_data: Dict, pro_number: str) -> Optional[Dict]:
        """Extract tracking information from React state"""
        try:
            # Recursively search for tracking data
            def search_object(obj, target_pro):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['tracking', 'shipment', 'pro', 'delivery']:
                            if isinstance(value, dict) and target_pro in str(value):
                                return value
                        result = search_object(value, target_pro)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = search_object(item, target_pro)
                        if result:
                            return result
                return None
            
            tracking_data = search_object(state_data, pro_number)
            if tracking_data:
                return self._format_peninsula_response(tracking_data, pro_number)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"State data extraction failed: {e}")
            return None
    
    def _extract_tracking_from_script(self, script_content: str, pro_number: str) -> Optional[Dict]:
        """Extract tracking data from script content"""
        try:
            # Look for delivery information patterns
            for pattern in self.delivery_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if len(match) >= 3:
                            date_str = match[0]
                            time_str = match[1]
                            location = match[2].strip()
                            
                            # Format the response
                            formatted_datetime = f"{date_str} {time_str}"
                            return {
                                'status': 'success',
                                'pro_number': pro_number,
                                'carrier': 'Peninsula Truck Lines',
                                'delivery_status': f"{formatted_datetime} Delivered {location}",
                                'extracted_from': 'script_content'
                            }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Script extraction failed: {e}")
            return None
    
    async def _try_api_reverse_engineering(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Reverse engineer Peninsula API endpoints"""
        try:
            # Try different API endpoints
            api_endpoints = [
                f"{self.api_base}/api/tracking/{pro_number}",
                f"{self.api_base}/api/shipment/{pro_number}",
                f"{self.api_base}/api/pro/{pro_number}",
                f"{self.base_url}/api/tracking/{pro_number}",
                f"{self.base_url}/api/shipment/track/{pro_number}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    # Generate potential auth tokens
                    auth_headers = self._generate_auth_headers(pro_number)
                    
                    response = session.get(endpoint, headers=auth_headers, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            tracking_info = self._process_api_response(data, pro_number)
                            if tracking_info:
                                return tracking_info
                        except json.JSONDecodeError:
                            # Try parsing as HTML
                            soup = BeautifulSoup(response.text, 'html.parser')
                            tracking_info = self._extract_from_html(soup, pro_number)
                            if tracking_info:
                                return tracking_info
                    
                    self.anti_scraping.simulate_human_behavior(0.5, 2)
                    
                except requests.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"API reverse engineering failed: {e}")
            return None
    
    def _generate_auth_headers(self, pro_number: str) -> Dict[str, str]:
        """Generate potential authentication headers"""
        import hashlib
        
        # Common auth patterns
        timestamp = str(int(time.time()))
        
        # Generate potential tokens
        token_patterns = [
            hashlib.md5(f"{pro_number}{timestamp}".encode()).hexdigest(),
            hashlib.sha1(f"peninsula{pro_number}".encode()).hexdigest(),
            f"Bearer {hashlib.md5(pro_number.encode()).hexdigest()}",
            f"Token {pro_number}_{timestamp}"
        ]
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f"{self.base_url}/tracking",
            'Origin': self.base_url
        }
        
        # Try different auth header combinations
        for i, token in enumerate(token_patterns):
            if i == 0:
                headers['Authorization'] = token
            elif i == 1:
                headers['X-Auth-Token'] = token
            elif i == 2:
                headers['X-API-Key'] = token
            else:
                headers['X-Access-Token'] = token
                
        return headers
    
    async def _try_mobile_site(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try mobile version of Peninsula site"""
        try:
            # Mobile user agent
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
            }
            session.headers.update(mobile_headers)
            
            # Try mobile tracking URLs
            mobile_urls = [
                f"{self.base_url}/m/tracking/{pro_number}",
                f"{self.base_url}/mobile/track/{pro_number}",
                f"{self.base_url}/track?pro={pro_number}&mobile=1"
            ]
            
            for url in mobile_urls:
                try:
                    response = session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        tracking_info = self._extract_from_html(soup, pro_number)
                        if tracking_info:
                            return tracking_info
                except requests.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Mobile site attempt failed: {e}")
            return None
    
    def _process_api_response(self, data: Dict, pro_number: str) -> Optional[Dict]:
        """Process API response data"""
        try:
            # Look for delivery information in API response
            def search_delivery_info(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['delivery', 'delivered', 'status', 'events']:
                            if isinstance(value, str) and 'delivered' in value.lower():
                                return value
                            elif isinstance(value, list):
                                for item in value:
                                    if isinstance(item, dict) and 'delivered' in str(item).lower():
                                        return item
                        result = search_delivery_info(value)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = search_delivery_info(item)
                        if result:
                            return result
                return None
            
            delivery_info = search_delivery_info(data)
            if delivery_info:
                return self._format_peninsula_response(delivery_info, pro_number)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"API response processing failed: {e}")
            return None
    
    def _extract_from_html(self, soup: BeautifulSoup, pro_number: str) -> Optional[Dict]:
        """Extract tracking info from HTML"""
        try:
            # Look for delivery information in HTML
            text_content = soup.get_text()
            
            for pattern in self.delivery_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if len(match) >= 3:
                            date_str = match[0]
                            time_str = match[1]
                            location = match[2].strip()
                            
                            formatted_datetime = f"{date_str} {time_str}"
                            return {
                                'status': 'success',
                                'pro_number': pro_number,
                                'carrier': 'Peninsula Truck Lines',
                                'delivery_status': f"{formatted_datetime} Delivered {location}",
                                'extracted_from': 'html_content'
                            }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"HTML extraction failed: {e}")
            return None
    
    def _format_peninsula_response(self, data: Any, pro_number: str) -> Dict[str, Any]:
        """Format Peninsula response data"""
        try:
            if isinstance(data, str):
                # Parse string data
                for pattern in self.delivery_patterns:
                    matches = re.findall(pattern, data, re.IGNORECASE)
                    if matches:
                        match = matches[0]
                        if len(match) >= 3:
                            date_str = match[0]
                            time_str = match[1]
                            location = match[2].strip()
                            
                            formatted_datetime = f"{date_str} {time_str}"
                            return {
                                'status': 'success',
                                'pro_number': pro_number,
                                'carrier': 'Peninsula Truck Lines',
                                'delivery_status': f"{formatted_datetime} Delivered {location}",
                                'extracted_from': 'formatted_response'
                            }
            
            elif isinstance(data, dict):
                # Extract from dictionary
                delivery_text = str(data)
                for pattern in self.delivery_patterns:
                    matches = re.findall(pattern, delivery_text, re.IGNORECASE)
                    if matches:
                        match = matches[0]
                        if len(match) >= 3:
                            date_str = match[0]
                            time_str = match[1]
                            location = match[2].strip()
                            
                            formatted_datetime = f"{date_str} {time_str}"
                            return {
                                'status': 'success',
                                'pro_number': pro_number,
                                'carrier': 'Peninsula Truck Lines',
                                'delivery_status': f"{formatted_datetime} Delivered {location}",
                                'extracted_from': 'dict_response'
                            }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Response formatting failed: {e}")
            return None


class FedExZeroCostTracker:
    """Zero-cost FedEx tracking implementation"""
    
    def __init__(self, anti_scraping_system: ZeroCostAntiScrapingSystem):
        self.logger = logging.getLogger(__name__)
        self.anti_scraping = anti_scraping_system
        self.base_url = "https://www.fedex.com"
        self.mobile_api = "https://mobile.fedex.com"
        self.graphql_endpoint = "https://www.fedex.com/graphql"
    
    async def track_pro(self, pro_number: str) -> Dict[str, Any]:
        """Track FedEx PRO with zero-cost methods"""
        try:
            session = self.anti_scraping.create_stealth_session("fedex")
            
            # Try mobile API first (less protected)
            result = await self._try_mobile_api(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            # Try GraphQL direct access
            result = await self._try_graphql_api(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            # Try legacy tracking page
            result = await self._try_legacy_tracking(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            return {
                'status': 'error',
                'message': 'Unable to bypass FedEx anti-scraping measures',
                'pro_number': pro_number
            }
            
        except Exception as e:
            self.logger.error(f"FedEx tracking failed: {e}")
            return {
                'status': 'error',
                'message': f'FedEx tracking error: {str(e)}',
                'pro_number': pro_number
            }
    
    async def _try_mobile_api(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try FedEx mobile API endpoints"""
        try:
            # Mobile headers
            mobile_headers = {
                'User-Agent': 'FedEx/7.5.0 (iPhone; iOS 17.0; Scale/3.00)',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            session.headers.update(mobile_headers)
            
            # Mobile API endpoints
            mobile_endpoints = [
                f"{self.mobile_api}/api/track/{pro_number}",
                f"{self.mobile_api}/api/shipment/{pro_number}",
                f"{self.mobile_api}/track?trackingNumber={pro_number}"
            ]
            
            for endpoint in mobile_endpoints:
                try:
                    response = session.get(endpoint, timeout=15)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            tracking_info = self._process_fedex_response(data, pro_number)
                            if tracking_info:
                                return tracking_info
                        except json.JSONDecodeError:
                            pass
                except requests.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Mobile API attempt failed: {e}")
            return None
    
    async def _try_graphql_api(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try FedEx GraphQL API"""
        try:
            # GraphQL query for tracking
            query = {
                "query": """
                    query TrackingQuery($trackingNumber: String!) {
                        tracking(trackingNumber: $trackingNumber) {
                            trackingNumber
                            status
                            deliveryDate
                            deliveryTime
                            deliveryLocation
                            events {
                                date
                                time
                                status
                                location
                            }
                        }
                    }
                """,
                "variables": {
                    "trackingNumber": pro_number
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = session.post(self.graphql_endpoint, json=query, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'tracking' in data['data']:
                        tracking_info = self._process_fedex_response(data['data']['tracking'], pro_number)
                        if tracking_info:
                            return tracking_info
                except json.JSONDecodeError:
                    pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"GraphQL API attempt failed: {e}")
            return None
    
    async def _try_legacy_tracking(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try legacy FedEx tracking page"""
        try:
            # Legacy tracking URL
            tracking_url = f"{self.base_url}/apps/fedextrack/?tracknumbers={pro_number}"
            
            response = session.get(tracking_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for tracking data in page
                tracking_info = self._extract_fedex_from_html(soup, pro_number)
                if tracking_info:
                    return tracking_info
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Legacy tracking attempt failed: {e}")
            return None
    
    def _process_fedex_response(self, data: Dict, pro_number: str) -> Optional[Dict]:
        """Process FedEx API response"""
        try:
            # Look for delivery information
            delivery_info = None
            
            if isinstance(data, dict):
                # Check for delivery status
                if 'status' in data and 'delivered' in str(data['status']).lower():
                    delivery_info = data
                elif 'events' in data and isinstance(data['events'], list):
                    # Find delivery event
                    for event in data['events']:
                        if isinstance(event, dict) and 'delivered' in str(event).lower():
                            delivery_info = event
                            break
            
            if delivery_info:
                return self._format_fedex_response(delivery_info, pro_number)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"FedEx response processing failed: {e}")
            return None
    
    def _extract_fedex_from_html(self, soup: BeautifulSoup, pro_number: str) -> Optional[Dict]:
        """Extract FedEx tracking from HTML"""
        try:
            text_content = soup.get_text()
            
            # FedEx delivery patterns
            patterns = [
                r'Delivered\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+([A-Z\s,]+)',
                r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+Delivered\s+([A-Z\s,]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    match = matches[0]
                    if len(match) >= 3:
                        date_str = match[0]
                        time_str = match[1]
                        location = match[2].strip()
                        
                        return {
                            'status': 'success',
                            'pro_number': pro_number,
                            'carrier': 'FedEx',
                            'delivery_status': f"{date_str} {time_str} Delivered {location}",
                            'extracted_from': 'html_content'
                        }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"FedEx HTML extraction failed: {e}")
            return None
    
    def _format_fedex_response(self, data: Any, pro_number: str) -> Dict[str, Any]:
        """Format FedEx response data"""
        try:
            # Extract delivery information
            delivery_text = str(data)
            
            # Look for delivery patterns
            patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+.*?([A-Z\s,]+)',
                r'delivered.*?(\d{1,2}/\d{1,2}/\d{4}).*?(\d{1,2}:\d{2}).*?([A-Z\s,]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, delivery_text, re.IGNORECASE)
                if matches:
                    match = matches[0]
                    if len(match) >= 3:
                        date_str = match[0]
                        time_str = match[1]
                        location = match[2].strip()
                        
                        return {
                            'status': 'success',
                            'pro_number': pro_number,
                            'carrier': 'FedEx',
                            'delivery_status': f"{date_str} {time_str} Delivered {location}",
                            'extracted_from': 'formatted_response'
                        }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"FedEx response formatting failed: {e}")
            return None


class EstesZeroCostTracker:
    """Zero-cost Estes tracking implementation"""
    
    def __init__(self, anti_scraping_system: ZeroCostAntiScrapingSystem):
        self.logger = logging.getLogger(__name__)
        self.anti_scraping = anti_scraping_system
        self.base_url = "https://www.estes-express.com"
        self.api_base = "https://www.estes-express.com/api"
    
    async def track_pro(self, pro_number: str) -> Dict[str, Any]:
        """Track Estes PRO with zero-cost methods"""
        try:
            session = self.anti_scraping.create_stealth_session("estes")
            
            # Try JavaScript rendering first
            result = await self._try_javascript_rendering(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            # Try internal API endpoints
            result = await self._try_internal_api(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            # Try mobile version
            result = await self._try_mobile_version(session, pro_number)
            if result and result.get('status') == 'success':
                return result
            
            return {
                'status': 'error',
                'message': 'Unable to bypass Estes anti-scraping measures',
                'pro_number': pro_number
            }
            
        except Exception as e:
            self.logger.error(f"Estes tracking failed: {e}")
            return {
                'status': 'error',
                'message': f'Estes tracking error: {str(e)}',
                'pro_number': pro_number
            }
    
    async def _try_javascript_rendering(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try JavaScript rendering for Estes"""
        try:
            tracking_url = f"{self.base_url}/shipment-tracking?pro={pro_number}"
            
            # Render JavaScript content
            html_content = await self.anti_scraping.render_javascript_page(tracking_url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for tracking data in rendered content
            tracking_info = self._extract_estes_from_html(soup, pro_number)
            if tracking_info:
                return tracking_info
            
            # Check for JSON data in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and pro_number in script.string:
                    tracking_data = self._extract_estes_from_script(script.string, pro_number)
                    if tracking_data:
                        return tracking_data
            
            return None
            
        except Exception as e:
            self.logger.debug(f"JavaScript rendering failed: {e}")
            return None
    
    async def _try_internal_api(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try Estes internal API endpoints"""
        try:
            # Internal API endpoints
            api_endpoints = [
                f"{self.api_base}/tracking/{pro_number}",
                f"{self.api_base}/shipment/{pro_number}",
                f"{self.api_base}/pro/{pro_number}",
                f"{self.base_url}/services/tracking/{pro_number}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    headers = {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Content-Type': 'application/json'
                    }
                    
                    response = session.get(endpoint, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            tracking_info = self._process_estes_response(data, pro_number)
                            if tracking_info:
                                return tracking_info
                        except json.JSONDecodeError:
                            # Try parsing as HTML
                            soup = BeautifulSoup(response.text, 'html.parser')
                            tracking_info = self._extract_estes_from_html(soup, pro_number)
                            if tracking_info:
                                return tracking_info
                    
                except requests.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Internal API attempt failed: {e}")
            return None
    
    async def _try_mobile_version(self, session: requests.Session, pro_number: str) -> Optional[Dict]:
        """Try Estes mobile version"""
        try:
            # Mobile headers
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
            }
            session.headers.update(mobile_headers)
            
            # Mobile tracking URL
            mobile_url = f"{self.base_url}/m/tracking/{pro_number}"
            
            response = session.get(mobile_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                tracking_info = self._extract_estes_from_html(soup, pro_number)
                if tracking_info:
                    return tracking_info
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Mobile version attempt failed: {e}")
            return None
    
    def _extract_estes_from_html(self, soup: BeautifulSoup, pro_number: str) -> Optional[Dict]:
        """Extract Estes tracking from HTML"""
        try:
            text_content = soup.get_text()
            
            # Estes delivery patterns
            patterns = [
                r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+Delivery\s+([A-Z\s,]+)',
                r'Delivery\s+(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+([A-Z\s,]+)',
                r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+Delivered\s+([A-Z\s,]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    match = matches[0]
                    if len(match) >= 3:
                        date_str = match[0]
                        time_str = match[1]
                        location = match[2].strip()
                        
                        return {
                            'status': 'success',
                            'pro_number': pro_number,
                            'carrier': 'Estes',
                            'delivery_status': f"{date_str} {time_str} Delivery {location}",
                            'extracted_from': 'html_content'
                        }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Estes HTML extraction failed: {e}")
            return None
    
    def _extract_estes_from_script(self, script_content: str, pro_number: str) -> Optional[Dict]:
        """Extract Estes tracking from script content"""
        try:
            # Look for delivery patterns in script
            patterns = [
                r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+Delivery\s+([A-Z\s,]+)',
                r'Delivery.*?(\d{2}/\d{2}/\d{4}).*?(\d{1,2}:\d{2}\s+[AP]M).*?([A-Z\s,]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                if matches:
                    match = matches[0]
                    if len(match) >= 3:
                        date_str = match[0]
                        time_str = match[1]
                        location = match[2].strip()
                        
                        return {
                            'status': 'success',
                            'pro_number': pro_number,
                            'carrier': 'Estes',
                            'delivery_status': f"{date_str} {time_str} Delivery {location}",
                            'extracted_from': 'script_content'
                        }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Estes script extraction failed: {e}")
            return None
    
    def _process_estes_response(self, data: Dict, pro_number: str) -> Optional[Dict]:
        """Process Estes API response"""
        try:
            # Look for delivery information
            delivery_info = None
            
            if isinstance(data, dict):
                # Search for delivery data
                def search_delivery(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key.lower() in ['delivery', 'delivered', 'status']:
                                if 'delivery' in str(value).lower():
                                    return value
                            result = search_delivery(value)
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = search_delivery(item)
                            if result:
                                return result
                    return None
                
                delivery_info = search_delivery(data)
            
            if delivery_info:
                return self._format_estes_response(delivery_info, pro_number)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Estes response processing failed: {e}")
            return None
    
    def _format_estes_response(self, data: Any, pro_number: str) -> Dict[str, Any]:
        """Format Estes response data"""
        try:
            delivery_text = str(data)
            
            # Look for delivery patterns
            patterns = [
                r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+.*?([A-Z\s,]+)',
                r'delivery.*?(\d{2}/\d{2}/\d{4}).*?(\d{1,2}:\d{2}\s+[AP]M).*?([A-Z\s,]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, delivery_text, re.IGNORECASE)
                if matches:
                    match = matches[0]
                    if len(match) >= 3:
                        date_str = match[0]
                        time_str = match[1]
                        location = match[2].strip()
                        
                        return {
                            'status': 'success',
                            'pro_number': pro_number,
                            'carrier': 'Estes',
                            'delivery_status': f"{date_str} {time_str} Delivery {location}",
                            'extracted_from': 'formatted_response'
                        }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Estes response formatting failed: {e}")
            return None


class ZeroCostCarrierManager:
    """Manager for all zero-cost carrier implementations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anti_scraping = ZeroCostAntiScrapingSystem()
        
        # Initialize carrier trackers
        self.peninsula_tracker = PeninsulaZeroCostTracker(self.anti_scraping)
        self.fedex_tracker = FedExZeroCostTracker(self.anti_scraping)
        self.estes_tracker = EstesZeroCostTracker(self.anti_scraping)
    
    async def track_shipment(self, carrier: str, pro_number: str) -> Dict[str, Any]:
        """Track shipment using appropriate zero-cost tracker"""
        try:
            carrier_lower = carrier.lower()
            
            if 'peninsula' in carrier_lower:
                return await self.peninsula_tracker.track_pro(pro_number)
            elif 'fedex' in carrier_lower:
                return await self.fedex_tracker.track_pro(pro_number)
            elif 'estes' in carrier_lower:
                return await self.estes_tracker.track_pro(pro_number)
            else:
                return {
                    'status': 'error',
                    'message': f'Zero-cost tracking not implemented for carrier: {carrier}',
                    'pro_number': pro_number
                }
                
        except Exception as e:
            self.logger.error(f"Zero-cost tracking failed for {carrier}: {e}")
            return {
                'status': 'error',
                'message': f'Zero-cost tracking error: {str(e)}',
                'pro_number': pro_number
            }
    
    def cleanup(self):
        """Clean up resources"""
        self.anti_scraping.cleanup() 