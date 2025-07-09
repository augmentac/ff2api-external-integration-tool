"""
LTL Tracking Client for scraping carrier websites to get tracking information.

This module provides web scraping functionality specifically for LTL carrier tracking
systems. It integrates with the existing external integration framework.
"""

import requests
import time
import json
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime

from .carrier_detection import detect_carrier_from_pro, get_tracking_url


@dataclass
class TrackingResult:
    """Data structure for tracking results"""
    pro_number: str
    carrier_name: str
    tracking_status: Optional[str] = None
    tracking_location: Optional[str] = None
    tracking_event: Optional[str] = None
    tracking_timestamp: Optional[str] = None
    scraped_data: Optional[str] = None
    scrape_success: bool = False
    error_message: Optional[str] = None
    load_id: Optional[str] = None
    row_index: Optional[int] = None


class LTLTrackingClient:
    """
    Web scraping client for LTL carrier tracking systems.
    
    This client can:
    - Detect carrier from PRO number
    - Scrape tracking information from carrier websites
    - Handle basic authentication
    - Parse structured data from tracking pages
    """
    
    def __init__(self, delay_between_requests: int = 2, max_retries: int = 3, timeout: int = 30):
        """
        Initialize the LTL tracking client.
        
        Args:
            delay_between_requests: Delay in seconds between requests
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.delay_between_requests = delay_between_requests
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set enhanced headers to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Cache-Control': 'max-age=0'
        })
    
    def track_pro_number(self, pro_number: str) -> TrackingResult:
        """
        Track a single PRO number.
        
        Args:
            pro_number: PRO number to track
            
        Returns:
            TrackingResult object with tracking information
        """
        result = TrackingResult(
            pro_number=pro_number,
            carrier_name="Unknown"
        )
        
        try:
            # Detect carrier from PRO number
            carrier_info = detect_carrier_from_pro(pro_number)
            if not carrier_info:
                result.error_message = "Could not detect carrier from PRO number"
                return result
            
            result.carrier_name = carrier_info['carrier_name']
            
            # Get tracking URL
            tracking_url = carrier_info.get('tracking_url')
            if not tracking_url:
                result.error_message = "No tracking URL available for this carrier"
                return result
            
            # Scrape tracking information
            tracking_data = self._scrape_tracking_page(tracking_url, carrier_info)
            
            # Check if we actually got useful tracking data
            if tracking_data and self._has_useful_tracking_data(tracking_data):
                result.tracking_status = tracking_data.get('status')
                result.tracking_location = tracking_data.get('location')
                result.tracking_event = tracking_data.get('event')
                result.tracking_timestamp = tracking_data.get('timestamp')
                result.scraped_data = json.dumps(tracking_data)
                result.scrape_success = True
            else:
                result.error_message = "Failed to scrape tracking information"
            
        except Exception as e:
            result.error_message = f"Error tracking PRO number: {str(e)}"
            logging.error(f"Error tracking PRO {pro_number}: {e}")
        
        return result
    
    def track_multiple_pro_numbers(self, pro_numbers: List[str]) -> List[TrackingResult]:
        """
        Track multiple PRO numbers.
        
        Args:
            pro_numbers: List of PRO numbers to track
            
        Returns:
            List of TrackingResult objects
        """
        results = []
        
        for i, pro_number in enumerate(pro_numbers):
            try:
                result = self.track_pro_number(pro_number)
                results.append(result)
                
                # Add delay between requests (except for the last one)
                if i < len(pro_numbers) - 1:
                    time.sleep(self.delay_between_requests)
                    
            except Exception as e:
                logging.error(f"Error tracking PRO {pro_number}: {e}")
                results.append(TrackingResult(
                    pro_number=pro_number,
                    carrier_name="Unknown",
                    error_message=f"Error tracking PRO number: {str(e)}"
                ))
        
        return results
    
    def _has_useful_tracking_data(self, tracking_data: Dict[str, Any]) -> bool:
        """
        Check if tracking data contains useful information.
        
        Args:
            tracking_data: Dictionary containing tracking data
            
        Returns:
            True if tracking data contains useful information, False otherwise
        """
        if not tracking_data:
            return False
            
        # Check if we have any meaningful tracking information
        useful_fields = ['status', 'location', 'event', 'timestamp']
        
        for field in useful_fields:
            value = tracking_data.get(field)
            if value and value not in ['No status available', 'No location available', 'No timestamp available', 'N/A', '', None]:
                # Additional validation to ensure the value is actually useful
                value_str = str(value).strip().lower()
                if value_str and value_str not in ['no data', 'not found', 'error', 'failed', 'unavailable', 'none', 'null']:
                    # Filter out Peninsula Truck Lines contact information and generic website content
                    if self._is_generic_website_content(value_str):
                        continue
                    return True
        
        # Don't consider generic fallback fields as useful unless they contain specific tracking terms
        fallback_fields = ['table_data', 'div_data', 'meta_tracking', 'peninsula_data']
        tracking_keywords = ['delivered', 'in transit', 'out for delivery', 'picked up', 'at terminal', 'departed', 'arrived']
        
        for field in fallback_fields:
            value = tracking_data.get(field)
            if value:
                value_str = str(value).strip().lower()
                if any(keyword in value_str for keyword in tracking_keywords):
                    # Still filter out generic content even if it contains tracking keywords
                    if not self._is_generic_website_content(value_str):
                        return True
        
        return False
    
    def _is_generic_website_content(self, text: str) -> bool:
        """
        Check if text contains generic website content that should not be considered tracking data.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is generic website content, False otherwise
        """
        text_lower = text.lower()
        
        # Peninsula Truck Lines specific filters
        peninsula_filters = [
            'general contact', 'phone:', 'fax:', 'corporate address', 'mailing address',
            'federal way, wa', 'auburn, wa', 'peninsula truck lines, inc',
            'po box 587', 'copyright', 'all rights reserved', 'privacy and cookies',
            'terms of service', 'machine readable files', 'facebook', 'twitter',
            'linkedin', 'instagram', 'youtube', 'join our community'
        ]
        
        # Generic website content filters
        generic_filters = [
            'contact us', 'about us', 'privacy policy', 'terms of use',
            'copyright', 'all rights reserved', 'footer', 'navigation',
            'menu', 'login', 'register', 'subscribe', 'newsletter',
            'social media', 'follow us', 'phone number', 'email address',
            'corporate headquarters', 'mailing address', 'po box'
        ]
        
        all_filters = peninsula_filters + generic_filters
        
        # Check if text contains any of the filter terms
        for filter_term in all_filters:
            if filter_term in text_lower:
                return True
        
        # Check if text is mostly contact information (contains multiple contact indicators)
        contact_indicators = ['phone', 'fax', 'address', 'email', 'contact', 'zip', 'state']
        contact_count = sum(1 for indicator in contact_indicators if indicator in text_lower)
        
        # If text contains 3+ contact indicators, it's likely contact info
        if contact_count >= 3:
            return True
        
        return False
    
    def _scrape_tracking_page(self, tracking_url: str, carrier_info: Dict) -> Optional[Dict[str, Any]]:
        """
        Scrape tracking information from a carrier's tracking page.
        
        Args:
            tracking_url: URL to scrape
            carrier_info: Carrier information including CSS selectors
            
        Returns:
            Dict containing tracking data or None if failed
        """
        # Check if this is FedEx and needs special handling
        is_fedex = 'fedex' in carrier_info.get('name', '').lower()
        
        # Check if this is Peninsula and needs special SPA handling
        is_peninsula = 'peninsula' in carrier_info.get('name', '').lower()
        
        # Check if this is an SPA application (like Peninsula)
        is_spa = carrier_info.get('spa_app', False)
        
        for attempt in range(self.max_retries):
            try:
                # Special handling for FedEx
                if is_fedex:
                    tracking_data = self._scrape_fedex_tracking(tracking_url, carrier_info)
                    if tracking_data:
                        return tracking_data
                    # If FedEx-specific method fails, continue with general method
                
                # Special handling for Peninsula
                if is_peninsula:
                    # Extract PRO number from URL
                    import re
                    pro_match = re.search(r'pro_number=([^&]+)', tracking_url)
                    if pro_match:
                        pro_number = pro_match.group(1)
                        tracking_data = self._scrape_peninsula_tracking(tracking_url, pro_number)
                        if tracking_data:
                            return tracking_data
                    # If Peninsula-specific method fails, continue with general method
                
                # Make the request with carrier-specific headers
                headers = self._get_carrier_specific_headers(carrier_info)
                response = self.session.get(tracking_url, timeout=self.timeout, headers=headers)
                response.raise_for_status()
                
                # For SPA applications, we may need to wait for JavaScript to load
                if is_spa or is_peninsula:
                    time.sleep(3)  # Give SPA time to load
                
                # Parse the HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # For Peninsula and other SPAs, try to extract data from scripts first
                if is_spa or is_peninsula:
                    script_data = self._extract_spa_data(response.text, carrier_info)
                    if script_data:
                        return script_data
                
                # Extract tracking data using CSS selectors
                tracking_data = self._extract_tracking_data(soup, carrier_info.get('css_selectors', {}))
                
                if tracking_data:
                    return tracking_data
                
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"Failed to scrape {tracking_url} after {self.max_retries} attempts")
            
            except Exception as e:
                logging.error(f"Error scraping tracking page: {e}")
                break
        
        return None
    
    def _scrape_fedex_tracking(self, tracking_url: str, carrier_info: Dict) -> Optional[Dict[str, Any]]:
        """
        Enhanced FedEx tracking with multiple fallback methods.
        
        Args:
            tracking_url: FedEx tracking URL
            carrier_info: Carrier information
            
        Returns:
            Dict containing tracking data or None if failed
        """
        try:
            # Extract PRO number from URL
            import re
            pro_match = re.search(r'trknbr=([^&]+)', tracking_url)
            if not pro_match:
                return None
            
            pro_number = pro_match.group(1)
            
            # Method 1: Try mobile FedEx tracking (less protected)
            mobile_url = f"https://m.fedex.com/track/{pro_number}"
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.fedex.com/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(mobile_url, headers=mobile_headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tracking_data = self._extract_fedex_mobile_data(soup)
                if tracking_data:
                    return tracking_data
            
            # Method 2: Try alternative FedEx tracking endpoint
            alt_url = f"https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber={pro_number}&cntry_code=us&locale=en_US"
            alt_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.fedex.com/en-us/tracking.html',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(alt_url, headers=alt_headers, timeout=self.timeout)
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    tracking_data = self._extract_fedex_json_data(json_data)
                    if tracking_data:
                        return tracking_data
                except:
                    pass
            
            # Method 3: Try original URL with session warming
            self._warm_fedex_session()
            response = self.session.get(tracking_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tracking_data = self._extract_tracking_data(soup, carrier_info.get('css_selectors', {}))
                if tracking_data:
                    return tracking_data
            
        except Exception as e:
            logging.debug(f"FedEx tracking failed: {e}")
        
        return None
    
    def _warm_fedex_session(self):
        """Warm up the session by visiting FedEx homepage first"""
        try:
            self.session.get('https://www.fedex.com/', timeout=10)
            time.sleep(1)
        except:
            pass
    
    def _extract_fedex_mobile_data(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract tracking data from FedEx mobile page"""
        tracking_data = {}
        
        try:
            # Look for mobile-specific elements
            status_element = soup.select_one('.tracking-status, .shipment-status, [class*="status"]')
            if status_element:
                tracking_data['status'] = self._clean_text(status_element.get_text())
            
            location_element = soup.select_one('.location, .current-location, [class*="location"]')
            if location_element:
                tracking_data['location'] = self._clean_text(location_element.get_text())
            
            # Look for tracking events
            event_elements = soup.select('.tracking-event, .scan-event, [class*="event"]')
            if event_elements:
                latest_event = event_elements[0]
                tracking_data['event'] = self._clean_text(latest_event.get_text())
            
        except Exception as e:
            logging.debug(f"Error extracting FedEx mobile data: {e}")
        
        return tracking_data if tracking_data else None
    
    def _extract_fedex_json_data(self, json_data: Dict) -> Optional[Dict[str, Any]]:
        """Extract tracking data from FedEx JSON response"""
        tracking_data = {}
        
        try:
            # Navigate through typical FedEx JSON structure
            if 'TrackPackagesResponse' in json_data:
                packages = json_data['TrackPackagesResponse'].get('packageList', [])
                if packages:
                    package = packages[0]
                    
                    # Extract status
                    if 'keyStatus' in package:
                        tracking_data['status'] = package['keyStatus']
                    
                    # Extract location from scan events
                    scan_events = package.get('scanEventList', [])
                    if scan_events:
                        latest_event = scan_events[0]
                        if 'scanLocation' in latest_event:
                            location_info = latest_event['scanLocation']
                            location_parts = []
                            if 'city' in location_info:
                                location_parts.append(location_info['city'])
                            if 'stateOrProvinceCode' in location_info:
                                location_parts.append(location_info['stateOrProvinceCode'])
                            if location_parts:
                                tracking_data['location'] = ', '.join(location_parts)
                        
                        if 'status' in latest_event:
                            tracking_data['event'] = latest_event['status']
                        
                        if 'date' in latest_event:
                            tracking_data['timestamp'] = latest_event['date']
            
        except Exception as e:
            logging.debug(f"Error extracting FedEx JSON data: {e}")
        
        return tracking_data if tracking_data else None
    
    def _get_carrier_specific_headers(self, carrier_info: Dict) -> Dict[str, str]:
        """Get carrier-specific headers"""
        carrier_name = carrier_info.get('name', '').lower()
        
        if 'fedex' in carrier_name:
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.fedex.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin'
            }
        elif 'rl' in carrier_name or 'r+l' in carrier_name:
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www2.rlcarriers.com/'
            }
        elif 'peninsula' in carrier_name:
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.peninsulatruck.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'no-cache'
            }
        
        # Default headers for other carriers
        return {}
    
    def _extract_spa_data(self, html_content: str, carrier_info: Dict) -> Optional[Dict[str, Any]]:
        """
        Extract data from Single Page Applications by parsing JavaScript.
        
        Args:
            html_content: Raw HTML content
            carrier_info: Carrier information
            
        Returns:
            Dict containing extracted tracking data
        """
        tracking_data = {}
        
        try:
            import re
            
            # Look for common SPA data patterns
            patterns = [
                r'trackingStatus["\']?\s*:\s*["\']([^"\']+)["\']',
                r'status["\']?\s*:\s*["\']([^"\']+)["\']',
                r'shipmentStatus["\']?\s*:\s*["\']([^"\']+)["\']',
                r'"status":\s*"([^"]+)"',
                r'tracking.*status.*"([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    tracking_data['status'] = matches[0]
                    break
            
            # Look for location data
            location_patterns = [
                r'location["\']?\s*:\s*["\']([^"\']+)["\']',
                r'currentLocation["\']?\s*:\s*["\']([^"\']+)["\']',
                r'"location":\s*"([^"]+)"',
            ]
            
            for pattern in location_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    tracking_data['location'] = matches[0]
                    break
            
            # Look for event data
            event_patterns = [
                r'lastEvent["\']?\s*:\s*["\']([^"\']+)["\']',
                r'latestActivity["\']?\s*:\s*["\']([^"\']+)["\']',
                r'"event":\s*"([^"]+)"',
            ]
            
            for pattern in event_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    tracking_data['event'] = matches[0]
                    break
            
            # Peninsula-specific: Look for API endpoints or data
            if 'peninsula' in carrier_info.get('name', '').lower():
                peninsula_patterns = [
                    r'pro.*?(\d{9})',
                    r'tracking.*?status.*?"([^"]+)"',
                    r'shipment.*?data.*?"([^"]+)"'
                ]
                
                for pattern in peninsula_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches and not tracking_data.get('status'):
                        tracking_data['peninsula_data'] = matches[0]
        
        except Exception as e:
            logging.debug(f"Error extracting SPA data: {e}")
        
        return tracking_data if tracking_data else None
    
    def _extract_tracking_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Extract tracking data from parsed HTML using CSS selectors.
        
        Args:
            soup: BeautifulSoup parsed HTML
            selectors: Dict of CSS selectors for different data fields
            
        Returns:
            Dict containing extracted tracking data
        """
        tracking_data = {}
        
        try:
            # Extract status using multiple selectors as fallbacks
            if 'status' in selectors:
                status_selectors = selectors['status'].split(', ')
                for selector in status_selectors:
                    status_element = soup.select_one(selector.strip())
                    if status_element and status_element.get_text().strip():
                        tracking_data['status'] = self._clean_text(status_element.get_text())
                        break
            
            # Extract location using multiple selectors as fallbacks
            if 'location' in selectors:
                location_selectors = selectors['location'].split(', ')
                for selector in location_selectors:
                    location_element = soup.select_one(selector.strip())
                    if location_element and location_element.get_text().strip():
                        tracking_data['location'] = self._clean_text(location_element.get_text())
                        break
            
            # Extract event/activity using multiple selectors as fallbacks
            if 'event' in selectors:
                event_selectors = selectors['event'].split(', ')
                for selector in event_selectors:
                    event_element = soup.select_one(selector.strip())
                    if event_element and event_element.get_text().strip():
                        tracking_data['event'] = self._clean_text(event_element.get_text())
                        break
            
            # Try to extract timestamp
            timestamp_selectors = ['timestamp', 'date', 'time', 'datetime']
            for ts_selector in timestamp_selectors:
                if ts_selector in selectors:
                    timestamp_element = soup.select_one(selectors[ts_selector])
                    if timestamp_element and timestamp_element.get_text().strip():
                        tracking_data['timestamp'] = self._clean_text(timestamp_element.get_text())
                        break
            
            # Enhanced extraction for priority carriers
            if not tracking_data or len(tracking_data) < 2:
                tracking_data.update(self._priority_carrier_extraction(soup))
            
            # If still no specific data found, try generic fallback
            if not tracking_data:
                tracking_data = self._generic_fallback_extraction(soup)
            
            # Add scrape timestamp
            tracking_data['scraped_at'] = datetime.now().isoformat()
            
            return tracking_data if tracking_data else None
            
        except Exception as e:
            logging.error(f"Error extracting tracking data: {e}")
            return None

    def _priority_carrier_extraction(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Enhanced extraction specifically for our 5 priority carriers.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dict containing extracted tracking data
        """
        tracking_data = {}
        
        try:
            # FedEx Freight specific patterns
            fedex_status = soup.select_one('[data-testid="trackingStatus"], [data-cy="trackingStatus"], .fedex-status')
            if fedex_status:
                tracking_data['status'] = self._clean_text(fedex_status.get_text())
            
            # R+L Carriers specific patterns
            rl_status = soup.select_one('.tracking-status, .shipment-status, [class*="status"]')
            if rl_status and 'rlcarriers' in soup.get_text().lower():
                tracking_data['status'] = self._clean_text(rl_status.get_text())
            
            # Estes Express specific patterns  
            estes_status = soup.select_one('.shipment-status, .tracking-detail, [class*="estes"]')
            if estes_status and 'estes' in soup.get_text().lower():
                tracking_data['status'] = self._clean_text(estes_status.get_text())
            
            # TForce Freight specific patterns
            tforce_status = soup.select_one('.tracking-status, [class*="tforce"], [class*="freight"]')
            if tforce_status and ('tforce' in soup.get_text().lower() or 'freight' in soup.get_text().lower()):
                tracking_data['status'] = self._clean_text(tforce_status.get_text())
            
            # Peninsula Truck Lines specific patterns (SPA handling)
            peninsula_data = self._extract_peninsula_data(soup)
            if peninsula_data:
                tracking_data.update(peninsula_data)
            
            # Look for common table structures used by LTL carriers
            tracking_table = soup.select_one('table[class*="track"], table[class*="status"], table[class*="shipment"]')
            if tracking_table:
                rows = tracking_table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        header = self._clean_text(cells[0].get_text()).lower()
                        value = self._clean_text(cells[1].get_text())
                        if 'status' in header and value:
                            tracking_data['status'] = value
                        elif 'location' in header and value:
                            tracking_data['location'] = value
                        elif 'event' in header or 'activity' in header and value:
                            tracking_data['event'] = value
                        elif 'date' in header or 'time' in header and value:
                            tracking_data['timestamp'] = value
        
        except Exception as e:
            logging.debug(f"Error in priority carrier extraction: {e}")
        
        return tracking_data

    def _extract_peninsula_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Enhanced extraction for Peninsula Truck Lines SPA.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dict containing Peninsula tracking data
        """
        tracking_data = {}
        
        try:
            # Peninsula uses SPA, so look for script tags with data
            script_tags = soup.find_all('script')
            for script in script_tags:
                script_content = script.get_text()
                if 'tracking' in script_content.lower() or 'status' in script_content.lower():
                    # Try to extract JSON data from script tags
                    import re
                    json_matches = re.findall(r'\{[^{}]*"status"[^{}]*\}', script_content)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if 'status' in data:
                                tracking_data['status'] = str(data['status'])
                            break
                        except:
                            continue
            
            # Look for Peninsula-specific elements that might appear after JS loads
            peninsula_selectors = [
                '[class*="peninsula"]', '[id*="peninsula"]', '[class*="track"]',
                '[class*="status"]', '[class*="shipment"]', '[class*="delivery"]',
                '.tracking-result', '.pro-status', '.shipment-status'
            ]
            
            for selector in peninsula_selectors:
                element = soup.select_one(selector)
                if element:
                    text = self._clean_text(element.get_text())
                    if text and not self._is_generic_website_content(text):
                        tracking_data['status'] = text
                        break
            
            # Look for API endpoints or configuration in script tags
            api_patterns = [
                r'api["\']?\s*:\s*["\']([^"\']+)["\']',
                r'endpoint["\']?\s*:\s*["\']([^"\']+)["\']',
                r'trackingUrl["\']?\s*:\s*["\']([^"\']+)["\']',
                r'/api/[^"\']+',
                r'track[^"\']*api[^"\']*'
            ]
            
            for script in script_tags:
                script_content = script.get_text()
                for pattern in api_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    if matches:
                        tracking_data['api_endpoint'] = matches[0]
                        break
            
            # Check for any hidden form data or meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('name') and 'tracking' in meta.get('name', '').lower():
                    content = meta.get('content', '')
                    if content:
                        tracking_data['meta_tracking'] = content
        
        except Exception as e:
            logging.debug(f"Error extracting Peninsula data: {e}")
        
        return tracking_data
    
    def _scrape_peninsula_tracking(self, tracking_url: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced Peninsula tracking with API endpoint detection and extended wait times.
        
        Args:
            tracking_url: Peninsula tracking URL
            pro_number: PRO number to track
            
        Returns:
            Dict containing tracking data or None if failed
        """
        try:
            # Method 1: Try to find and call their API directly
            api_data = self._try_peninsula_api(pro_number)
            if api_data:
                return api_data
            
            # Method 2: Load the page and wait for SPA to initialize
            peninsula_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.peninsulatruck.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            response = self.session.get(tracking_url, headers=peninsula_headers, timeout=self.timeout)
            if response.status_code == 200:
                # Wait longer for SPA to load
                time.sleep(5)
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract any API endpoints from the page
                api_endpoints = self._extract_peninsula_api_endpoints(soup, pro_number)
                for endpoint in api_endpoints:
                    api_data = self._call_peninsula_api(endpoint, pro_number)
                    if api_data:
                        return api_data
                
                # Fallback to regular extraction
                return self._extract_peninsula_data(soup)
            
        except Exception as e:
            logging.debug(f"Peninsula tracking failed: {e}")
        
        return None
    
    def _try_peninsula_api(self, pro_number: str) -> Optional[Dict[str, Any]]:
        """
        Try common Peninsula API endpoints.
        
        Args:
            pro_number: PRO number to track
            
        Returns:
            Dict containing tracking data or None if failed
        """
        # Common API endpoints for Peninsula
        api_endpoints = [
            f'https://www.peninsulatruck.com/api/tracking/{pro_number}',
            f'https://www.peninsulatruck.com/api/track?pro={pro_number}',
            f'https://www.peninsulatruck.com/_/api/tracking?pro_number={pro_number}',
            f'https://www.peninsulatruck.com/_/api/track/{pro_number}',
            f'https://api.peninsulatruck.com/tracking/{pro_number}',
            f'https://api.peninsulatruck.com/track?pro={pro_number}'
        ]
        
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'https://www.peninsulatruck.com/_/#/track/?pro_number={pro_number}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(endpoint, headers=api_headers, timeout=10)
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        tracking_data = self._parse_peninsula_api_response(json_data)
                        if tracking_data:
                            return tracking_data
                    except:
                        # Try to parse as text if JSON fails
                        text_data = response.text
                        if any(keyword in text_data.lower() for keyword in ['delivered', 'transit', 'picked up', 'terminal']):
                            return {'status': text_data.strip()}
            except:
                continue
        
        return None
    
    def _extract_peninsula_api_endpoints(self, soup: BeautifulSoup, pro_number: str) -> List[str]:
        """
        Extract API endpoints from Peninsula's SPA page.
        
        Args:
            soup: BeautifulSoup parsed HTML
            pro_number: PRO number for URL construction
            
        Returns:
            List of potential API endpoints
        """
        endpoints = []
        
        try:
            script_tags = soup.find_all('script')
            for script in script_tags:
                script_content = script.get_text()
                
                # Look for API endpoint patterns
                import re
                patterns = [
                    r'["\']([^"\']*api[^"\']*track[^"\']*)["\']',
                    r'["\']([^"\']*track[^"\']*api[^"\']*)["\']',
                    r'baseUrl["\']?\s*:\s*["\']([^"\']+)["\']',
                    r'apiUrl["\']?\s*:\s*["\']([^"\']+)["\']',
                    r'trackingApi["\']?\s*:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if 'api' in match.lower() and 'track' in match.lower():
                            # Construct full URL if needed
                            if match.startswith('/'):
                                endpoint = f'https://www.peninsulatruck.com{match}'
                            elif not match.startswith('http'):
                                endpoint = f'https://www.peninsulatruck.com/{match}'
                            else:
                                endpoint = match
                            
                            # Add PRO number to endpoint
                            if '?' in endpoint:
                                endpoint = f'{endpoint}&pro_number={pro_number}'
                            else:
                                endpoint = f'{endpoint}?pro_number={pro_number}'
                            
                            endpoints.append(endpoint)
        
        except Exception as e:
            logging.debug(f"Error extracting Peninsula API endpoints: {e}")
        
        return endpoints
    
    def _call_peninsula_api(self, endpoint: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """
        Call Peninsula API endpoint.
        
        Args:
            endpoint: API endpoint URL
            pro_number: PRO number
            
        Returns:
            Dict containing tracking data or None if failed
        """
        try:
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'https://www.peninsulatruck.com/_/#/track/?pro_number={pro_number}',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(endpoint, headers=api_headers, timeout=10)
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    return self._parse_peninsula_api_response(json_data)
                except:
                    # Try to parse as text
                    text_data = response.text.strip()
                    if text_data and any(keyword in text_data.lower() for keyword in ['delivered', 'transit', 'picked up', 'terminal']):
                        return {'status': text_data}
        
        except Exception as e:
            logging.debug(f"Error calling Peninsula API {endpoint}: {e}")
        
        return None
    
    def _parse_peninsula_api_response(self, json_data: Dict) -> Optional[Dict[str, Any]]:
        """
        Parse Peninsula API JSON response.
        
        Args:
            json_data: JSON response from Peninsula API
            
        Returns:
            Dict containing tracking data or None if failed
        """
        tracking_data = {}
        
        try:
            # Common JSON structure patterns
            if isinstance(json_data, dict):
                # Direct status field
                if 'status' in json_data:
                    tracking_data['status'] = str(json_data['status'])
                
                # Nested tracking data
                if 'tracking' in json_data:
                    tracking_info = json_data['tracking']
                    if isinstance(tracking_info, dict):
                        if 'status' in tracking_info:
                            tracking_data['status'] = str(tracking_info['status'])
                        if 'location' in tracking_info:
                            tracking_data['location'] = str(tracking_info['location'])
                        if 'event' in tracking_info:
                            tracking_data['event'] = str(tracking_info['event'])
                
                # Shipment data
                if 'shipment' in json_data:
                    shipment_info = json_data['shipment']
                    if isinstance(shipment_info, dict):
                        if 'status' in shipment_info:
                            tracking_data['status'] = str(shipment_info['status'])
                        if 'current_location' in shipment_info:
                            tracking_data['location'] = str(shipment_info['current_location'])
                
                # Array of tracking events
                if 'events' in json_data and isinstance(json_data['events'], list):
                    events = json_data['events']
                    if events:
                        latest_event = events[0]
                        if isinstance(latest_event, dict):
                            if 'status' in latest_event:
                                tracking_data['status'] = str(latest_event['status'])
                            if 'location' in latest_event:
                                tracking_data['location'] = str(latest_event['location'])
                            if 'description' in latest_event:
                                tracking_data['event'] = str(latest_event['description'])
            
            # Handle array response
            elif isinstance(json_data, list) and json_data:
                first_item = json_data[0]
                if isinstance(first_item, dict):
                    return self._parse_peninsula_api_response(first_item)
        
        except Exception as e:
            logging.debug(f"Error parsing Peninsula API response: {e}")
        
        return tracking_data if tracking_data else None
    
    def _generic_fallback_extraction(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Generic fallback extraction for when specific selectors don't work.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dict containing any tracking data found
        """
        tracking_data = {}
        
        # Look for common tracking-related text patterns
        text_content = soup.get_text().lower()
        
        # Common status indicators
        status_patterns = [
            'delivered', 'in transit', 'out for delivery', 'picked up',
            'at terminal', 'departed', 'arrived', 'exception', 'delayed'
        ]
        
        for pattern in status_patterns:
            if pattern in text_content:
                tracking_data['status'] = pattern.title()
                break
        
        # Try to find any structured data
        try:
            # Look for tables that might contain tracking info
            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text().lower()
                if any(keyword in table_text for keyword in ['status', 'location', 'date', 'time']):
                    tracking_data['table_data'] = self._clean_text(table.get_text())
                    break
            
            # Look for divs with tracking-related classes
            tracking_keywords = ['track', 'status', 'event', 'shipment']
            tracking_divs = []
            all_divs = soup.find_all('div')
            for div in all_divs:
                class_attr = div.get('class', [])
                if class_attr and any(keyword in ' '.join(class_attr).lower() for keyword in tracking_keywords):
                    tracking_divs.append(div)
                    break
            
            if tracking_divs:
                tracking_data['div_data'] = self._clean_text(tracking_divs[0].get_text())
        
        except Exception as e:
            logging.debug(f"Error in generic fallback extraction: {e}")
        
        return tracking_data
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.strip().split())
        
        # Remove common unwanted characters
        cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        return cleaned
    
    def test_carrier_connection(self, carrier_code: str) -> Dict[str, Any]:
        """
        Test connection to a specific carrier's tracking system.
        
        Args:
            carrier_code: Carrier code to test
            
        Returns:
            Dict containing connection test results
        """
        from .carrier_detection import carrier_detector
        
        carrier_info = carrier_detector.get_carrier_info(carrier_code)
        if not carrier_info:
            return {'success': False, 'error': 'Unknown carrier code'}
        
        # Use a test PRO number format for this carrier
        test_pro = "123-1234567"  # Generic test format
        test_url = carrier_info['tracking_url'].format(pro_number=test_pro)
        
        try:
            response = self.session.get(test_url, timeout=self.timeout)
            
            return {
                'success': True,
                'carrier_name': carrier_info['name'],
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'url_tested': test_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'carrier_name': carrier_info['name'],
                'error': str(e),
                'url_tested': test_url
            }
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()


# Utility function for easy integration
def track_pro_numbers(pro_numbers: List[str], **kwargs) -> List[TrackingResult]:
    """
    Convenience function to track multiple PRO numbers.
    
    Args:
        pro_numbers: List of PRO numbers to track
        **kwargs: Additional arguments for LTLTrackingClient
        
    Returns:
        List of TrackingResult objects
    """
    client = LTLTrackingClient(**kwargs)
    try:
        return client.track_multiple_pro_numbers(pro_numbers)
    finally:
        client.close()


def track_single_pro(pro_number: str, **kwargs) -> TrackingResult:
    """
    Convenience function to track a single PRO number.
    
    Args:
        pro_number: PRO number to track
        **kwargs: Additional arguments for LTLTrackingClient
        
    Returns:
        TrackingResult object
    """
    client = LTLTrackingClient(**kwargs)
    try:
        return client.track_pro_number(pro_number)
    finally:
        client.close() 