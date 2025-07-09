"""
Carrier Detection Utility for LTL PRO Numbers

This module provides functionality to detect LTL carriers based on PRO number patterns
and formats. Each carrier has unique numbering schemes that can be used for identification.
"""

import re
import logging
from typing import Dict, Optional, List, Tuple


class CarrierDetector:
    """
    Detects LTL carriers based on PRO number patterns and formats.
    """
    
    def __init__(self):
        self.carrier_patterns = self._initialize_carrier_patterns()
    
    def _initialize_carrier_patterns(self) -> Dict[str, Dict]:
        """
        Initialize carrier patterns with PRO number formats and tracking URLs.
        
        Returns:
            Dict containing carrier information with patterns, URLs, and metadata
        """
        return {
            'fedex_freight': {
                'name': 'FedEx Freight',
                'patterns': [
                    r'^(RS\d{8})$',             # RS-prefix 8-digit: RS25909506 (most specific)
                    r'^(\d{9}-\d{1})$',         # 9-digit with dash and 1 digit: 761607932-1
                    r'^([1-9]\d{9})$',          # 10-digit starting with 1-9: 1751027634, 4012381741, 5556372640
                    r'^(\d{3}-\d{7})$',         # 10-digit with dash: 555-6372640
                    r'^(\d{4}-\d{3}-\d{3})$',   # 10-digit with dashes: 5556-372-640
                ],
                'tracking_url': 'https://www.fedex.com/fedextrack/?trknbr={pro_number}&trkqual=~{pro_number}~FDFR',
                'login_required': False,
                'css_selectors': {
                    'status': '[data-testid="trackingStatus"], [data-cy="trackingStatus"], .tracking-status, .shipment-status, .fedex-status',
                    'location': '[data-testid="location"], [data-cy="location"], .current-location, .location-text, .fedex-location',
                    'event': '[data-testid="scanEvent"], [data-cy="scanEvent"], .latest-event, .scan-event, .fedex-event'
                },
                'priority': 1  # High priority carrier
            },
            'rl_carriers': {
                'name': 'R+L Carriers',
                'patterns': [
                    r'^(I\d{9})$',       # I-prefix 9-digit: I010185804 (most specific)
                    r'^(I\d{3}-\d{6})$', # I-prefix with dash: I010-185804
                    r'^(\d{8}-\d{1})$',  # 8-digit with dash and 1 digit: 14588517-6
                    r'^([0123]\d{8})$',  # 9-digit starting with 0,1,2,3: 933784722
                    r'^(\d{3}-\d{6})$',  # 9-digit with dash: 823-691187
                ],
                'tracking_url': 'https://www.rlcarriers.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status, .shipment-status, .status-text',
                    'location': '.current-location, .location-text, .shipment-location',
                    'event': '.latest-update, .latest-event, .tracking-event'
                },
                'priority': 1  # High priority carrier
            },
            'estes': {
                'name': 'Estes Express',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format: 123-1234567
                    r'^([0167]\d{9})$',  # 10-digit starting with 0,1,6,7: 0628143046, 1282975382, 1611116978, 1642457961
                    r'^(2\d{9})$',       # 10-digit starting with 2: 2121121287 (exclude Peninsula)
                    r'^(7[0-4]\d{7})$',  # 9-digit starting with 70-74: 750773321 (exclude Peninsula)
                    r'^(\d{8})$',        # 8-digit format: 12345678
                ],
                'tracking_url': 'https://www.estes-express.com/myestes/tracking/shipment?searchValue={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.shipment-status, .tracking-status, .status-text',
                    'location': '.current-location, .location-text, .shipment-location',
                    'event': '.latest-event, .tracking-event, .shipment-event'
                },
                'priority': 2  # Higher priority to avoid conflicts with FedEx
            },
            'tforce_freight': {
                'name': 'TForce Freight',
                'patterns': [
                    r'^(2205\d{9})$',    # TForce specific: 2205 + 9 digits
                    r'^(\d{3}-\d{7})$',  # Standard format: 123-1234567
                    r'^(\d{10})$',       # 10-digit format: 1234567890
                    r'^(\d{9})$',        # 9-digit format: 123456789
                ],
                'tracking_url': 'https://www.tforcefreight.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status, .shipment-status, .status-text',
                    'location': '.current-location, .location-text, .shipment-location',
                    'event': '.latest-event, .tracking-event, .shipment-event'
                },
                'priority': 1  # High priority carrier
            },
            'peninsula_truck_lines': {
                'name': 'Peninsula Truck Lines',
                'patterns': [
                    r'^(536\d{6})$',     # 536 prefix with 6 digits: 536246546
                    r'^(537\d{6})$',     # 537 prefix with 6 digits: 537313956
                    r'^(622\d{5})$',     # 622 prefix with 5 digits: 62263246
                    r'^(\d{9})$',        # 9-digit format: 536246546
                    r'^(\d{3}-\d{6})$',  # 9-digit with dash: 536-246546
                ],
                'tracking_url': 'https://www.peninsulatruck.com/_/#/track/?pro_number={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status, .shipment-status, .status-text, [class*="status"]',
                    'location': '.current-location, .location-text, .shipment-location, [class*="location"]',
                    'event': '.latest-event, .tracking-event, .shipment-event, [class*="event"]'
                },
                'priority': 3,  # Higher priority than Estes for specific patterns
                'spa_app': True  # Single Page Application - requires special handling
            },
            'averitt_express': {
                'name': 'Averitt Express',
                'patterns': [
                    r'^(I\d{9})$',       # I-prefix 9-digit format: I010185804
                    r'^(I\d{3}-\d{6})$', # I-prefix with dash: I010-185804
                ],
                'tracking_url': 'https://www.averittexpress.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status, .shipment-status, .status-text',
                    'location': '.current-location, .location-text, .shipment-location',
                    'event': '.latest-event, .tracking-event, .shipment-event'
                },
                'priority': 1  # High priority carrier
            },
            # Legacy carriers (lower priority)
            'old_dominion': {
                'name': 'Old Dominion Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format: 123-1234567
                    r'^([89]\d{9})$',    # 10-digit starting with 8,9: 8XXXXXXXXX, 9XXXXXXXXX
                ],
                'tracking_url': 'https://www.odfl.com/Tracking/shipment_tracking.aspx?pro_number={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-event'
                },
                'priority': 2  # Lower priority
            },
            'ups_freight': {
                'name': 'UPS Freight',
                'patterns': [
                    r'^(\d{3}\d{8})$',   # 11-digit format
                    r'^(\d{4}\d{7})$',   # 11-digit alternate
                ],
                'tracking_url': 'https://www.ups.com/track?loc=en_US&tracknum={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '[data-qa-id="trackingStatus"]',
                    'location': '[data-qa-id="location"]',
                    'event': '[data-qa-id="latestEvent"]'
                },
                'priority': 2  # Lower priority
            },
            'xpo_logistics': {
                'name': 'XPO Logistics',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.xpo.com/tracking?searchValue={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.status-text',
                    'location': '.location-text',
                    'event': '.event-description'
                },
                'priority': 2  # Lower priority
            },
            'saia': {
                'name': 'Saia',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.saia.com/tracking?searchValue={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-activity'
                },
                'priority': 2  # Lower priority
            },
            'abf_freight': {
                'name': 'ABF Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://arcb.com/tools/tracking.html?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.pro-status',
                    'location': '.pro-location',
                    'event': '.pro-event'
                },
                'priority': 2  # Lower priority
            },
            'yrc_freight': {
                'name': 'YRC Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://my.yrc.com/dynamic/national/servlet?CONTROLLER=com.rdwy.ec.rextracking.http.controller.ProcessPublicTrackingController&PRONumber={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.shipment-status',
                    'location': '.current-location',
                    'event': '.latest-activity'
                },
                'priority': 2  # Lower priority
            },
            'southeastern_freight': {
                'name': 'Southeastern Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.sefl.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-event'
                },
                'priority': 2  # Lower priority
            },
            'dayton_freight': {
                'name': 'Dayton Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.daytonfreight.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-event'
                },
                'priority': 2  # Lower priority
            }
        }
    
    def detect_carrier(self, pro_number: Optional[str]) -> Optional[Dict]:
        """
        Detect the carrier based on PRO number format.
        
        Args:
            pro_number: The PRO number to analyze
            
        Returns:
            Dict containing carrier information or None if not detected
        """
        if not pro_number:
            return None
        
        # Clean the PRO number
        cleaned_pro = self._clean_pro_number(pro_number)
        if not cleaned_pro:
            return None
        
        # Sort carriers by priority (higher priority first)
        sorted_carriers = sorted(
            self.carrier_patterns.items(),
            key=lambda x: x[1].get('priority', 3),  # Default priority is 3 (lower)
            reverse=True  # Higher priority first
        )
        
        # Try to match against known patterns in priority order
        for carrier_code, carrier_info in sorted_carriers:
            for pattern in carrier_info['patterns']:
                if re.match(pattern, cleaned_pro):
                    tracking_url = carrier_info['tracking_url']
                    if tracking_url:
                        tracking_url = tracking_url.format(pro_number=cleaned_pro)
                    else:
                        tracking_url = ''
                    
                    return {
                        'carrier_code': carrier_code,
                        'carrier_name': carrier_info['name'],
                        'tracking_url': tracking_url,
                        'login_required': carrier_info['login_required'],
                        'css_selectors': carrier_info['css_selectors']
                    }
        
        # If no specific pattern matches, return generic info
        return {
            'carrier_code': 'unknown',
            'carrier_name': 'Unknown Carrier',
            'tracking_url': '',
            'login_required': False,
            'css_selectors': {}
        }
    
    def _clean_pro_number(self, pro_number: Optional[str]) -> str:
        """
        Clean and normalize PRO number format.
        
        Args:
            pro_number: Raw PRO number string
            
        Returns:
            Cleaned PRO number string (never None)
        """
        if not pro_number:
            return ""
        
        # Remove common prefixes and suffixes
        cleaned = str(pro_number).strip().upper()
        
        # Remove common prefixes like "PRO:", "PRO#", etc.
        prefixes = ['PRO:', 'PRO#', 'PRO ', 'PRONUMBER:', 'PRONUMBER#']
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        return cleaned if cleaned else ""
    
    def get_carrier_info(self, carrier_code: str) -> Optional[Dict]:
        """
        Get carrier information by carrier code.
        
        Args:
            carrier_code: The carrier code to look up
            
        Returns:
            Dict containing carrier information or None if not found
        """
        return self.carrier_patterns.get(carrier_code)
    
    def get_all_carriers(self) -> List[Dict]:
        """
        Get list of all supported carriers.
        
        Returns:
            List of carrier information dictionaries
        """
        carriers = []
        for carrier_code, carrier_info in self.carrier_patterns.items():
            carriers.append({
                'carrier_code': carrier_code,
                'carrier_name': carrier_info['name'],
                'login_required': carrier_info['login_required']
            })
        return carriers
    
    def validate_pro_number(self, pro_number: Optional[str], carrier_code: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate PRO number format.
        
        Args:
            pro_number: PRO number to validate
            carrier_code: Optional specific carrier to validate against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not pro_number:
            return False, "PRO number cannot be empty"
        
        cleaned_pro = self._clean_pro_number(pro_number)
        if not cleaned_pro:
            return False, "PRO number cannot be empty after cleaning"
        
        if len(cleaned_pro) < 5:
            return False, "PRO number too short"
        
        if len(cleaned_pro) > 20:
            return False, "PRO number too long"
        
        # If specific carrier provided, validate against that carrier's patterns
        if carrier_code and carrier_code in self.carrier_patterns:
            carrier_info = self.carrier_patterns[carrier_code]
            for pattern in carrier_info['patterns']:
                if re.match(pattern, cleaned_pro):
                    return True, ""
            return False, f"PRO number format invalid for {carrier_info['name']}"
        
        # Otherwise, validate against any known pattern
        for carrier_key, carrier_info in self.carrier_patterns.items():
            for pattern in carrier_info['patterns']:
                if re.match(pattern, cleaned_pro):
                    return True, ""
        
        # If no pattern matches, it's still potentially valid (unknown carrier)
        return True, ""


# Initialize global carrier detector instance
carrier_detector = CarrierDetector()


def detect_carrier_from_pro(pro_number: Optional[str]) -> Optional[Dict]:
    """
    Convenience function to detect carrier from PRO number.
    
    Args:
        pro_number: PRO number to analyze
        
    Returns:
        Dict containing carrier information or None if not detected
    """
    return carrier_detector.detect_carrier(pro_number)


def get_tracking_url(pro_number: Optional[str], carrier_code: Optional[str] = None) -> Optional[str]:
    """
    Get tracking URL for a PRO number.
    
    Args:
        pro_number: PRO number to track
        carrier_code: Optional carrier code if known
        
    Returns:
        Tracking URL string or None if not available
    """
    if not pro_number:
        return None
        
    if carrier_code:
        carrier_info = carrier_detector.get_carrier_info(carrier_code)
        if carrier_info and 'tracking_url' in carrier_info and carrier_info['tracking_url']:
            tracking_url = carrier_info['tracking_url']
            if tracking_url:
                return tracking_url.format(pro_number=pro_number or '')
    
    # Try to detect carrier
    detected = carrier_detector.detect_carrier(pro_number)
    if detected and detected['tracking_url']:
        return detected['tracking_url']
    
    return None 