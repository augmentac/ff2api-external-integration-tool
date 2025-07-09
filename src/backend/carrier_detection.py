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
            'old_dominion': {
                'name': 'Old Dominion Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format: 123-1234567
                    r'^(\d{10})$',       # Alternate format: 1234567890
                ],
                'tracking_url': 'https://www.odfl.com/Tracking/shipment_tracking.aspx?pro_number={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-event'
                }
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
                }
            },
            'fedex_freight': {
                'name': 'FedEx Freight',
                'patterns': [
                    r'^(\d{4}-\d{4}-\d{4})$',  # 12-digit with dashes
                    r'^(\d{12})$',              # 12-digit without dashes
                ],
                'tracking_url': 'https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '[data-cy="trackingStatus"]',
                    'location': '[data-cy="location"]',
                    'event': '[data-cy="scanEvent"]'
                }
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
                }
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
                }
            },
            'estes': {
                'name': 'Estes Express',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.estes-express.com/myestes/tracking/shipment?searchValue={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.shipment-status',
                    'location': '.current-location',
                    'event': '.latest-event'
                }
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
                }
            },
            'rl_carriers': {
                'name': 'R+L Carriers',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.rlcarriers.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-update'
                }
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
                }
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
                }
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
                }
            },
            'tforce_freight': {
                'name': 'TForce Freight',
                'patterns': [
                    r'^(\d{3}-\d{7})$',  # Standard format
                    r'^(\d{10})$',       # Alternate format
                ],
                'tracking_url': 'https://www.tforcefreight.com/tracking?pro={pro_number}',
                'login_required': False,
                'css_selectors': {
                    'status': '.tracking-status',
                    'location': '.current-location',
                    'event': '.latest-event'
                }
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
        
        # Try to match against known patterns
        for carrier_code, carrier_info in self.carrier_patterns.items():
            for pattern in carrier_info['patterns']:
                if re.match(pattern, cleaned_pro):
                    return {
                        'carrier_code': carrier_code,
                        'carrier_name': carrier_info['name'],
                        'tracking_url': carrier_info['tracking_url'].format(pro_number=cleaned_pro),
                        'login_required': carrier_info['login_required'],
                        'css_selectors': carrier_info['css_selectors']
                    }
        
        # If no specific pattern matches, return generic info
        return {
            'carrier_code': 'unknown',
            'carrier_name': 'Unknown Carrier',
            'tracking_url': None,
            'login_required': False,
            'css_selectors': {}
        }
    
    def _clean_pro_number(self, pro_number: str) -> str:
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
    
    def validate_pro_number(self, pro_number: Optional[str], carrier_code: str = None) -> Tuple[bool, str]:
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
        for carrier_code, carrier_info in self.carrier_patterns.items():
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


def get_tracking_url(pro_number: Optional[str], carrier_code: str = None) -> Optional[str]:
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
            return carrier_info['tracking_url'].format(pro_number=pro_number)
    
    # Try to detect carrier
    detected = carrier_detector.detect_carrier(pro_number)
    if detected and detected['tracking_url']:
        return detected['tracking_url']
    
    return None 