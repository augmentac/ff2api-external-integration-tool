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
        
        # Set common headers to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
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
            
            if tracking_data:
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
    
    def _scrape_tracking_page(self, tracking_url: str, carrier_info: Dict) -> Optional[Dict[str, Any]]:
        """
        Scrape tracking information from a carrier's tracking page.
        
        Args:
            tracking_url: URL to scrape
            carrier_info: Carrier information including CSS selectors
            
        Returns:
            Dict containing tracking data or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                # Make the request
                response = self.session.get(tracking_url, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
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
            # Extract status
            if 'status' in selectors:
                status_element = soup.select_one(selectors['status'])
                if status_element:
                    tracking_data['status'] = self._clean_text(status_element.get_text())
            
            # Extract location
            if 'location' in selectors:
                location_element = soup.select_one(selectors['location'])
                if location_element:
                    tracking_data['location'] = self._clean_text(location_element.get_text())
            
            # Extract event/activity
            if 'event' in selectors:
                event_element = soup.select_one(selectors['event'])
                if event_element:
                    tracking_data['event'] = self._clean_text(event_element.get_text())
            
            # Try to extract timestamp
            timestamp_selectors = ['timestamp', 'date', 'time', 'datetime']
            for ts_selector in timestamp_selectors:
                if ts_selector in selectors:
                    timestamp_element = soup.select_one(selectors[ts_selector])
                    if timestamp_element:
                        tracking_data['timestamp'] = self._clean_text(timestamp_element.get_text())
                        break
            
            # If no specific selectors worked, try generic fallback
            if not tracking_data:
                tracking_data = self._generic_fallback_extraction(soup)
            
            # Add scrape timestamp
            tracking_data['scraped_at'] = datetime.now().isoformat()
            
            return tracking_data if tracking_data else None
            
        except Exception as e:
            logging.error(f"Error extracting tracking data: {e}")
            return None
    
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