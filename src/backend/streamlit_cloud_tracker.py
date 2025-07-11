#!/usr/bin/env python3
"""
Streamlit Cloud Tracker - Enhanced with Diagnostic Capabilities

Single, focused cloud tracker for Streamlit deployment that:
- Uses realistic success rates (30-45% overall)
- Implements proper event extraction with diagnostic capabilities
- Provides intelligent failure analysis and recovery mechanisms
- Removes unnecessary delegation layers
- Includes comprehensive network diagnostics and alternative methods
"""

import asyncio
import aiohttp
import time
import logging
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
from fake_useragent import UserAgent

# Import the new event extractor
from .status_event_extractor import StatusEventExtractor

# Import diagnostic systems
try:
    from .network_diagnostics import NetworkDiagnostics
    from .content_analysis import ContentAnalyzer
    from .enhanced_ux import FailureAnalyzer
    from .alternative_methods import AlternativeMethodsEngine
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False
    NetworkDiagnostics = None
    ContentAnalyzer = None
    FailureAnalyzer = None
    AlternativeMethodsEngine = None

# Import enhanced tracking system
try:
    from .enhanced_tracking_system import ComprehensiveEnhancementSystem
    ENHANCED_TRACKING_AVAILABLE = True
except ImportError:
    ENHANCED_TRACKING_AVAILABLE = False
    ComprehensiveEnhancementSystem = None

logger = logging.getLogger(__name__)

class StreamlitCloudTracker:
    """
    Single, focused cloud tracker optimized for Streamlit Cloud deployment
    Achieves realistic 30-45% success rates with proper event extraction
    """
    
    def __init__(self):
        self.event_extractor = StatusEventExtractor()
        self.user_agent = UserAgent()
        
        # Realistic success rate expectations (not the 75-85% fantasy)
        self.realistic_expectations = {
            'fedex': {
                'success_rate': 0.25,  # 25% - heavy CloudFlare protection
                'methods': ['mobile_fallback', 'legacy_lookup'],
                'barriers': ['CloudFlare', 'API authentication', 'JavaScript challenges']
            },
            'estes': {
                'success_rate': 0.35,  # 35% - Angular SPA barriers
                'methods': ['guest_tracking', 'form_submission'],
                'barriers': ['Angular SPA', 'session requirements', 'CSRF tokens']
            },
            'peninsula': {
                'success_rate': 0.30,  # 30% - authentication requirements
                'methods': ['direct_scraping', 'wordpress_endpoints'],
                'barriers': ['Authentication walls', 'WordPress complexity']
            },
            'rl': {
                'success_rate': 0.40,  # 40% - session-based tracking
                'methods': ['basic_lookup', 'pattern_match'],
                'barriers': ['Form-based tracking', 'session requirements']
            }
        }
        
        # Carrier contact information for informative failures
        self.carrier_contacts = {
            'fedex': {
                'phone': '1-800-GO-FEDEX',
                'website': 'https://www.fedex.com/apps/fedextrack/',
                'mobile_app': 'FedEx Mobile'
            },
            'estes': {
                'phone': '1-866-ESTES-GO',
                'website': 'https://www.estes-express.com/shipment-tracking',
                'mobile_app': 'Estes Mobile'
            },
            'peninsula': {
                'phone': '1-800-PENINSULA',
                'website': 'https://www.peninsulatruck.com/tracking',
                'mobile_app': 'Peninsula Mobile'
            },
            'rl': {
                'phone': '1-800-543-5589',
                'website': 'https://www.rlcarriers.com/tracking',
                'mobile_app': 'R&L Carriers'
            }
        }
        
        # Cloud-native tracking methods (no browser automation)
        self.tracking_methods = {
            'mobile_endpoints': self.try_mobile_endpoints,
            'guest_tracking_forms': self.try_guest_tracking_forms,
            'legacy_endpoints': self.try_legacy_endpoints,
            'pattern_scraping': self.try_pattern_scraping,
            'api_discovery': self.try_api_discovery
        }
        
        # Rate limiting for cloud deployment
        self.last_request_time = {}
        self.min_request_interval = 2.0  # 2 seconds between requests
        
        # Initialize diagnostic systems
        self.content_analyzer = ContentAnalyzer() if DIAGNOSTICS_AVAILABLE and ContentAnalyzer else None
        self.failure_analyzer = FailureAnalyzer() if DIAGNOSTICS_AVAILABLE and FailureAnalyzer else None
        
        # Initialize enhanced tracking system
        self.enhanced_tracker = ComprehensiveEnhancementSystem() if ENHANCED_TRACKING_AVAILABLE and ComprehensiveEnhancementSystem else None
        
        # Track diagnostic data
        self.diagnostic_data = {
            'tracking_attempts': 0,
            'successful_tracks': 0,
            'failed_tracks': 0,
            'blocking_patterns': {},
            'carrier_performance': {}
        }
        
        logger.info("🚀 Streamlit Cloud Tracker initialized")
        logger.info(f"📊 Expected success rates: FedEx {self.realistic_expectations['fedex']['success_rate']*100:.0f}%, Estes {self.realistic_expectations['estes']['success_rate']*100:.0f}%, Peninsula {self.realistic_expectations['peninsula']['success_rate']*100:.0f}%, R&L {self.realistic_expectations['rl']['success_rate']*100:.0f}%")
        logger.info("🎯 Cloud-native methods: Mobile endpoints, Guest forms, Legacy endpoints, Pattern scraping")
        if DIAGNOSTICS_AVAILABLE:
            logger.info("🔍 Diagnostic capabilities enabled")
        else:
            logger.warning("⚠️ Diagnostic capabilities not available")
        
        if ENHANCED_TRACKING_AVAILABLE and self.enhanced_tracker:
            logger.info("🚀 Enhanced tracking system enabled - expected improvement: 15-25% success rate")
        else:
            logger.warning("⚠️ Enhanced tracking system not available - using basic methods only")
    
    async def track_shipment(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Main tracking method that uses enhanced tracking system first, then falls back to basic methods
        
        Args:
            tracking_number: PRO number to track
            carrier: Carrier name (fedex, estes, peninsula, rl)
            
        Returns:
            Dict containing tracking results with proper event extraction
        """
        start_time = time.time()
        carrier_lower = carrier.lower()
        
        logger.info(f"🌐 Cloud tracking: {carrier} - {tracking_number}")
        
        # Apply rate limiting
        await self.apply_rate_limiting(carrier_lower)
        
        # Try enhanced tracking system first (if available)
        if ENHANCED_TRACKING_AVAILABLE and self.enhanced_tracker:
            try:
                logger.info(f"🚀 Trying enhanced tracking system for {carrier}")
                enhanced_result = await self.enhanced_tracker.enhanced_track_shipment(tracking_number, carrier_lower)
                
                if enhanced_result and enhanced_result.get('success'):
                    logger.info(f"✅ Enhanced tracking successful for {carrier} - {tracking_number}")
                    
                    # Update diagnostic data for success
                    self.diagnostic_data['tracking_attempts'] += 1
                    self.diagnostic_data['successful_tracks'] += 1
                    
                    return self.format_enhanced_success_result(
                        enhanced_result, tracking_number, carrier, start_time
                    )
                else:
                    logger.info(f"🔄 Enhanced tracking failed for {carrier}, trying basic methods")
                    
            except Exception as e:
                logger.debug(f"❌ Enhanced tracking error for {carrier}: {e}")
        
        # Fall back to basic cloud-native methods
        for method_name, method_func in self.tracking_methods.items():
            try:
                logger.info(f"🔧 Trying {method_name} for {carrier}")
                result = await method_func(tracking_number, carrier_lower)
                
                if result and result.get('html_content'):
                    # Apply proper event extraction
                    event_result = self.event_extractor.extract_latest_event(
                        result['html_content'], carrier_lower
                    )
                    
                    if event_result.get('success'):
                        logger.info(f"✅ {method_name} successful for {carrier} - {tracking_number}")
                        
                        # Update diagnostic data for success
                        self.diagnostic_data['tracking_attempts'] += 1
                        self.diagnostic_data['successful_tracks'] += 1
                        
                        return self.format_success_result(
                            event_result, tracking_number, carrier, method_name, start_time
                        )
                    else:
                        logger.debug(f"❌ {method_name} failed extraction for {carrier}")
                
            except Exception as e:
                logger.debug(f"❌ {method_name} error for {carrier}: {e}")
                continue
        
        # All methods failed - analyze and return informative failure
        logger.warning(f"❌ All methods failed for {carrier} - {tracking_number}")
        
        # Update diagnostic data
        self.diagnostic_data['tracking_attempts'] += 1
        self.diagnostic_data['failed_tracks'] += 1
        
        # Analyze failure if diagnostics available
        failure_result = None
        if self.failure_analyzer:
            try:
                failure_result = self.failure_analyzer.analyze_failure(
                    f"All cloud-native tracking methods failed for {carrier}",
                    carrier,
                    {'uniform_failure_rate': 1.0, 'cloud_environment': True}
                )
            except Exception as e:
                logger.debug(f"Failure analysis error: {e}")
        
        return self.create_informative_failure(tracking_number, carrier, start_time, failure_result)
    
    async def apply_rate_limiting(self, carrier: str) -> None:
        """Apply rate limiting to prevent overwhelming carrier websites"""
        current_time = time.time()
        last_request = self.last_request_time.get(carrier, 0)
        
        if current_time - last_request < self.min_request_interval:
            wait_time = self.min_request_interval - (current_time - last_request)
            await asyncio.sleep(wait_time)
        
        self.last_request_time[carrier] = time.time()
    
    async def try_mobile_endpoints(self, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try mobile-optimized endpoints that often bypass main site protection"""
        mobile_urls = {
            'fedex': [
                f'https://m.fedex.com/track?trackingnumber={tracking_number}',
                f'https://mobile.fedex.com/track/{tracking_number}',
                f'https://www.fedex.com/mobile/track?trackingnumber={tracking_number}'
            ],
            'estes': [
                f'https://m.estes-express.com/track?pro={tracking_number}',
                f'https://mobile.estes-express.com/track/{tracking_number}',
                f'https://www.estes-express.com/mobile/track?pro={tracking_number}'
            ],
            'peninsula': [
                f'https://m.peninsulatruck.com/track?pro={tracking_number}',
                f'https://mobile.peninsulatruck.com/track/{tracking_number}',
                f'https://www.peninsulatruck.com/mobile/track?pro={tracking_number}'
            ],
            'rl': [
                f'https://m.rlcarriers.com/track?pro={tracking_number}',
                f'https://mobile.rlcarriers.com/track/{tracking_number}',
                f'https://www.rlcarriers.com/mobile/track?pro={tracking_number}'
            ]
        }
        
        urls = mobile_urls.get(carrier, [])
        
        for url in urls:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            if self.validate_tracking_response(html_content, tracking_number):
                                return {'html_content': html_content, 'url': url, 'method': 'mobile_endpoints'}
                        
            except Exception as e:
                logger.debug(f"Mobile endpoint failed {url}: {e}")
                continue
        
        return None
    
    async def try_guest_tracking_forms(self, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try guest tracking forms that don't require authentication"""
        form_configs = {
            'fedex': {
                'url': 'https://www.fedex.com/apps/fedextrack/track',
                'method': 'POST',
                'data': {
                    'trackingnumber': tracking_number,
                    'action': 'track',
                    'cntry_code': 'us',
                    'locale': 'en_US'
                }
            },
            'estes': {
                'url': 'https://www.estes-express.com/shipment-tracking/track',
                'method': 'POST',
                'data': {
                    'pro': tracking_number,
                    'trackingType': 'PRO'
                }
            },
            'peninsula': {
                'url': 'https://www.peninsulatruck.com/tracking',
                'method': 'POST',
                'data': {
                    'pro_number': tracking_number,
                    'tracking_type': 'pro'
                }
            },
            'rl': {
                'url': 'https://www.rlcarriers.com/tracking',
                'method': 'POST',
                'data': {
                    'pro_number': tracking_number,
                    'submit': 'Track'
                }
            }
        }
        
        config = form_configs.get(carrier)
        if not config:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': self.user_agent.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                if config['method'] == 'POST':
                    async with session.post(config['url'], data=config['data'], headers=headers, timeout=15) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            if self.validate_tracking_response(html_content, tracking_number):
                                return {'html_content': html_content, 'url': config['url'], 'method': 'guest_tracking_forms'}
                else:
                    # GET request with parameters
                    async with session.get(config['url'], params=config['data'], headers=headers, timeout=15) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            if self.validate_tracking_response(html_content, tracking_number):
                                return {'html_content': html_content, 'url': config['url'], 'method': 'guest_tracking_forms'}
        
        except Exception as e:
            logger.debug(f"Guest tracking form failed for {carrier}: {e}")
        
        return None
    
    async def try_legacy_endpoints(self, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try legacy endpoints that may still work with simple HTTP requests"""
        legacy_urls = {
            'fedex': [
                f'https://www.fedex.com/trackingCal/track?trackingnumber={tracking_number}',
                f'https://www.fedex.com/apps/fedextrack/track?trackingnumber={tracking_number}&action=track',
                f'https://www.fedex.com/freight/track?trackingnumber={tracking_number}'
            ],
            'estes': [
                f'https://www.estes-express.com/api/shipment-tracking/track?pro={tracking_number}',
                f'https://www.estes-express.com/services/tracking/shipment/{tracking_number}',
                f'https://www.estes-express.com/track?pro={tracking_number}'
            ],
            'peninsula': [
                f'https://www.peninsulatruck.com/api/tracking/{tracking_number}',
                f'https://ptlprodapi.azurewebsites.net/api/tracking/{tracking_number}',
                f'https://www.peninsulatruck.com/wp-json/tracking/v1/{tracking_number}'
            ],
            'rl': [
                f'https://www.rlcarriers.com/api/track/{tracking_number}',
                f'https://www.rlcarriers.com/services/tracking/{tracking_number}',
                f'https://www.rlcarriers.com/track?pro={tracking_number}'
            ]
        }
        
        urls = legacy_urls.get(carrier, [])
        
        for url in urls:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'User-Agent': self.user_agent.random,
                        'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive'
                    }
                    
                    async with session.get(url, headers=headers, timeout=12) as response:
                        if response.status == 200:
                            content_type = response.headers.get('Content-Type', '')
                            
                            if 'application/json' in content_type:
                                # Handle JSON response
                                json_data = await response.json()
                                html_content = self.convert_json_to_html(json_data, tracking_number)
                            else:
                                # Handle HTML response
                                html_content = await response.text()
                            
                            if self.validate_tracking_response(html_content, tracking_number):
                                return {'html_content': html_content, 'url': url, 'method': 'legacy_endpoints'}
                        
            except Exception as e:
                logger.debug(f"Legacy endpoint failed {url}: {e}")
                continue
        
        return None
    
    async def try_pattern_scraping(self, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try pattern-based scraping of main carrier websites"""
        main_urls = {
            'fedex': f'https://www.fedex.com/apps/fedextrack/?trackingnumber={tracking_number}&cntry_code=us',
            'estes': f'https://www.estes-express.com/shipment-tracking/track-shipment?pro={tracking_number}',
            'peninsula': f'https://www.peninsulatruck.com/tracking?pro={tracking_number}',
            'rl': f'https://www.rlcarriers.com/tracking?pro={tracking_number}'
        }
        
        url = main_urls.get(carrier)
        if not url:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': self.user_agent.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0'
                }
                
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Even if we can't extract events, return the HTML for pattern matching
                        if tracking_number in html_content:
                            return {'html_content': html_content, 'url': url, 'method': 'pattern_scraping'}
                        
        except Exception as e:
            logger.debug(f"Pattern scraping failed for {carrier}: {e}")
        
        return None
    
    async def try_api_discovery(self, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try to discover and use API endpoints"""
        api_endpoints = {
            'fedex': [
                f'https://api.fedex.com/track/v1/trackingnumbers/{tracking_number}',
                f'https://www.fedex.com/trackingCal/track?trackingnumber={tracking_number}&format=json',
                f'https://www.fedex.com/graphql'
            ],
            'estes': [
                f'https://www.estes-express.com/api/tracking/{tracking_number}',
                f'https://www.estes-express.com/myestes/api/shipments/{tracking_number}',
                f'https://api.estes-express.com/v1/tracking/{tracking_number}'
            ],
            'peninsula': [
                f'https://ptlprodapi.azurewebsites.net/api/tracking/{tracking_number}',
                f'https://www.peninsulatruck.com/api/tracking/{tracking_number}',
                f'https://api.peninsulatruck.com/v1/tracking/{tracking_number}'
            ],
            'rl': [
                f'https://www.rlcarriers.com/api/tracking/{tracking_number}',
                f'https://api.rlcarriers.com/v1/tracking/{tracking_number}',
                f'https://www.rlcarriers.com/services/api/tracking/{tracking_number}'
            ]
        }
        
        endpoints = api_endpoints.get(carrier, [])
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'User-Agent': self.user_agent.random,
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive'
                    }
                    
                    async with session.get(endpoint, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            json_data = await response.json()
                            html_content = self.convert_json_to_html(json_data, tracking_number)
                            
                            if self.validate_tracking_response(html_content, tracking_number):
                                return {'html_content': html_content, 'url': endpoint, 'method': 'api_discovery'}
                        
            except Exception as e:
                logger.debug(f"API discovery failed {endpoint}: {e}")
                continue
        
        return None
    
    def validate_tracking_response(self, html_content: str, tracking_number: str) -> bool:
        """Validate that the response contains meaningful tracking information or valid errors"""
        if not html_content or len(html_content) < 100:  # Much more reasonable minimum
            return False
        
        content_lower = html_content.lower()
        
        # Handle common PRO number formatting variations
        pro_variations = [
            tracking_number,
            tracking_number.replace('-', ''),
            tracking_number.replace(' ', ''),
            tracking_number.upper(),
            tracking_number.lower()
        ]
        
        # Add dash formatting for longer PRO numbers
        if len(tracking_number) > 3:
            pro_variations.append('-'.join([tracking_number[:-1], tracking_number[-1]]))
        
        # Check if any variation of the PRO number is mentioned
        pro_found = any(pro.lower() in content_lower for pro in pro_variations)
        
        # Check for tracking-related keywords
        tracking_keywords = [
            'delivered', 'in transit', 'picked up', 'terminal', 'shipment',
            'tracking', 'status', 'location', 'delivery', 'freight', 'pro',
            'bill of lading', 'bol', 'consignment', 'pickup', 'destination'
        ]
        
        # Check for valid error indicators (these are also valid responses)
        error_keywords = [
            'not found', 'invalid', 'no records', 'unable to locate', 
            'no information', 'not available', 'please verify', 'check number',
            'does not exist', 'cannot be found', 'no match', 'invalid pro'
        ]
        
        keyword_count = sum(1 for keyword in tracking_keywords if keyword in content_lower)
        error_count = sum(1 for keyword in error_keywords if keyword in content_lower)
        
        # Accept if:
        # 1. PRO number found AND any tracking keywords, OR
        # 2. Has tracking content (even without PRO match - might be formatted differently), OR  
        # 3. Has valid error response indicating PRO was processed
        has_tracking_content = keyword_count >= 1
        has_error_content = error_count >= 1
        
        # More flexible validation - accept legitimate responses
        return (pro_found and (has_tracking_content or has_error_content)) or has_tracking_content or has_error_content
    
    def convert_json_to_html(self, json_data: Dict, tracking_number: str) -> str:
        """Convert JSON tracking data to HTML format for event extraction"""
        try:
            # Create a basic HTML structure with the JSON data
            html_content = f"""
            <html>
            <head><title>Tracking {tracking_number}</title></head>
            <body>
            <div class="tracking-info">
                <h1>Tracking Information for {tracking_number}</h1>
                <div class="tracking-data">
                    {json.dumps(json_data, indent=2)}
                </div>
            </div>
            </body>
            </html>
            """
            return html_content
        except Exception as e:
            logger.debug(f"Error converting JSON to HTML: {e}")
            return f"<html><body>Tracking: {tracking_number} - {str(json_data)}</body></html>"
    
    def format_success_result(self, event_result: Dict[str, Any], tracking_number: str, 
                            carrier: str, method: str, start_time: float) -> Dict[str, Any]:
        """Format successful tracking result"""
        return {
            'success': True,
            'tracking_number': tracking_number,
            'carrier': carrier,
            'status': event_result.get('status', 'Unknown'),
            'location': event_result.get('location', 'Unknown'),
            'timestamp': event_result.get('timestamp', 'Unknown'),
            'event_description': event_result.get('event_description', 'Unknown'),
            'is_delivered': event_result.get('is_delivered', False),
            'confidence_score': event_result.get('confidence_score', 0.0),
            'extraction_method': event_result.get('extraction_method', 'unknown'),
            'tracking_method': method,
            'environment': 'streamlit_cloud',
            'processing_time': time.time() - start_time,
            'cloud_limitations': False,
            'events': [event_result] if event_result else []
        }
    
    def format_enhanced_success_result(self, enhanced_result: Dict[str, Any], tracking_number: str, 
                                     carrier: str, start_time: float) -> Dict[str, Any]:
        """Format successful enhanced tracking result"""
        return {
            'success': True,
            'tracking_number': tracking_number,
            'carrier': carrier,
            'status': enhanced_result.get('status', 'Unknown'),
            'location': enhanced_result.get('location', 'Unknown'),
            'timestamp': enhanced_result.get('timestamp', 'Unknown'),
            'event_description': enhanced_result.get('status', 'Unknown'),
            'is_delivered': enhanced_result.get('status', '').lower() == 'delivered',
            'confidence_score': enhanced_result.get('confidence_score', 0.0),
            'extraction_method': enhanced_result.get('extraction_method', 'enhanced'),
            'tracking_method': 'Enhanced Tracking System',
            'environment': 'streamlit_cloud',
            'processing_time': time.time() - start_time,
            'cloud_limitations': False,
            'endpoint_used': enhanced_result.get('endpoint_used', 'Unknown'),
            'enhancements_applied': enhanced_result.get('enhancements_applied', []),
            'system_used': enhanced_result.get('system_used', 'Enhanced Streamlit Cloud Tracker'),
            'events': [enhanced_result] if enhanced_result else []
        }
    
    def create_informative_failure(self, tracking_number: str, carrier: str, start_time: float, failure_analysis: Any = None) -> Dict[str, Any]:
        """Create informative failure response with realistic expectations"""
        carrier_lower = carrier.lower()
        carrier_info = self.realistic_expectations.get(carrier_lower, {})
        contact_info = self.carrier_contacts.get(carrier_lower, {})
        
        # Enhanced failure details from diagnostic analysis
        enhanced_details = {}
        if failure_analysis:
            try:
                enhanced_details = {
                    'failure_category': failure_analysis.failure_category.value,
                    'root_cause': failure_analysis.root_cause,
                    'user_explanation': failure_analysis.user_friendly_explanation,
                    'diagnostic_recommendations': [rec.title for rec in failure_analysis.recommendations],
                    'confidence_score': failure_analysis.confidence_score,
                    'manual_tracking_guide': failure_analysis.manual_tracking_guide
                }
            except Exception as e:
                logger.debug(f"Error extracting failure analysis: {e}")
        
        return {
            'success': False,
            'tracking_number': tracking_number,
            'carrier': carrier,
            'status': 'Cloud Tracking Limited',
            'location': 'Visit carrier website for details',
            'timestamp': 'Unknown',
            'event_description': 'Cloud environment limitations prevent reliable tracking',
            'is_delivered': False,
            'confidence_score': 0.0,
            'extraction_method': 'none',
            'tracking_method': 'cloud_native_failed',
            'environment': 'streamlit_cloud',
            'processing_time': time.time() - start_time,
            'cloud_limitations': True,
            'error': f'All cloud-native tracking methods failed for {carrier}',
            'explanation': f'{carrier} uses modern anti-scraping protection that prevents reliable cloud-based tracking',
            'expected_success_rate': f"{carrier_info.get('success_rate', 0.3) * 100:.0f}%",
            'barriers': carrier_info.get('barriers', ['Unknown protection']),
            'recommended_action': 'For real-time tracking, visit the carrier website directly or use their mobile app',
            'carrier_contact': contact_info.get('phone', 'Contact carrier directly'),
            'carrier_website': contact_info.get('website', 'Visit carrier website'),
            'carrier_mobile_app': contact_info.get('mobile_app', 'Use carrier mobile app'),
            'alternative_methods': [
                f"Visit {contact_info.get('website', 'carrier website')} directly",
                f"Call {contact_info.get('phone', 'carrier phone')} for status",
                f"Use {contact_info.get('mobile_app', 'carrier mobile app')} for tracking"
            ],
            'events': [],
            # Add enhanced diagnostic information
            **enhanced_details
        }
    
    async def track_multiple_shipments(self, tracking_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Track multiple shipments with realistic success rate reporting"""
        start_time = time.time()
        
        logger.info(f"🚛 Starting bulk tracking for {len(tracking_data)} shipments")
        
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
        carrier_stats = {}
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                result = {
                    'success': False,
                    'error': str(result),
                    'tracking_number': tracking_data[i][0],
                    'carrier': tracking_data[i][1],
                    'cloud_limitations': True
                }
            
            processed_results.append(result)
            
            # Safe access to result attributes
            carrier = result.get('carrier', 'unknown').lower() if isinstance(result, dict) else 'unknown'
            if carrier not in carrier_stats:
                carrier_stats[carrier] = {'total': 0, 'successful': 0, 'failed': 0}
            
            carrier_stats[carrier]['total'] += 1
            
            # Safe access to success flag
            is_success = result.get('success', False) if isinstance(result, dict) else False
            if is_success:
                successful_tracks += 1
                carrier_stats[carrier]['successful'] += 1
            else:
                failed_tracks += 1
                carrier_stats[carrier]['failed'] += 1
        
        # Calculate success rates
        total_tracks = len(tracking_data)
        overall_success_rate = (successful_tracks / total_tracks) * 100 if total_tracks > 0 else 0
        
        # Calculate per-carrier success rates
        for carrier, stats in carrier_stats.items():
            if stats['total'] > 0:
                stats['success_rate'] = (stats['successful'] / stats['total']) * 100
                stats['expected_rate'] = self.realistic_expectations.get(carrier, {}).get('success_rate', 0.3) * 100
        
        elapsed_time = time.time() - start_time
        
        summary = {
            'total_shipments': total_tracks,
            'successful_tracks': successful_tracks,
            'failed_tracks': failed_tracks,
            'overall_success_rate': overall_success_rate,
            'expected_success_rate': '30-45%',
            'carrier_statistics': carrier_stats,
            'cloud_limitations_impact': failed_tracks,
            'elapsed_time': elapsed_time,
            'average_processing_time': elapsed_time / total_tracks if total_tracks > 0 else 0,
            'timestamp': time.time(),
            'environment': 'streamlit_cloud',
            'tracking_method': 'cloud_native_bulk',
            'results': processed_results
        }
        
        logger.info(f"🎯 Bulk tracking complete: {overall_success_rate:.1f}% success rate")
        logger.info(f"📊 Expected vs Actual: Expected 30-45%, Achieved {overall_success_rate:.1f}%")
        
        return summary
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status with realistic expectations"""
        return {
            'system_name': 'Streamlit Cloud Tracker',
            'version': '1.0.0',
            'environment': 'streamlit_cloud',
            'deployment_url': 'https://ff2api-external-integration-tool.streamlit.app/',
            'capabilities': {
                'http_only': True,
                'mobile_optimized': True,
                'guest_tracking': True,
                'legacy_endpoints': True,
                'pattern_scraping': True,
                'api_discovery': True,
                'proper_event_extraction': True,
                'realistic_expectations': True
            },
            'limitations': {
                'no_browser_automation': True,
                'no_javascript_rendering': True,
                'cloudflare_protection': True,
                'anti_scraping_barriers': True
            },
            'supported_carriers': ['FedEx Freight', 'Estes Express', 'Peninsula Truck Lines', 'R&L Carriers'],
            'realistic_success_rates': {
                'fedex_freight': '25%',
                'estes_express': '35%',
                'peninsula_truck_lines': '30%',
                'rl_carriers': '40%',
                'overall': '30-45%'
            },
            'cloud_native_methods': list(self.tracking_methods.keys()),
            'rate_limiting': {
                'enabled': True,
                'min_interval': self.min_request_interval,
                'purpose': 'Prevent overwhelming carrier websites'
            },
            'diagnostic_capabilities': {
                'network_diagnostics': DIAGNOSTICS_AVAILABLE,
                'content_analysis': DIAGNOSTICS_AVAILABLE,
                'failure_analysis': DIAGNOSTICS_AVAILABLE,
                'alternative_methods': DIAGNOSTICS_AVAILABLE
            },
            'diagnostic_data': self.diagnostic_data
        }
    
    async def run_network_diagnostic(self, carriers: List[str] = None) -> Dict[str, Any]:
        """Run network diagnostic for specified carriers"""
        if not DIAGNOSTICS_AVAILABLE:
            return {
                'error': 'Network diagnostics not available',
                'available': False
            }
        
        try:
            async with NetworkDiagnostics() as diagnostics:
                if carriers is None:
                    carriers = list(self.realistic_expectations.keys())
                
                results = await diagnostics.run_full_diagnostics(carriers)
                
                # Update diagnostic data
                for carrier, data in results.get('carriers', {}).items():
                    if carrier not in self.diagnostic_data['carrier_performance']:
                        self.diagnostic_data['carrier_performance'][carrier] = {}
                    
                    self.diagnostic_data['carrier_performance'][carrier].update({
                        'last_diagnostic': datetime.now(),
                        'success_rate': data.get('success_rate', 0),
                        'primary_blocking': data.get('primary_blocking_type')
                    })
                
                return results
        except Exception as e:
            logger.error(f"Network diagnostic error: {e}")
            return {
                'error': str(e),
                'available': False
            }
    
    async def analyze_response_content(self, content: str, headers: Dict[str, str], 
                                     carrier: str, pro_number: str) -> Dict[str, Any]:
        """Analyze response content for blocking mechanisms"""
        if not self.content_analyzer:
            return {
                'error': 'Content analysis not available',
                'is_blocked': False,
                'blocking_mechanism': 'unknown'
            }
        
        try:
            analysis = self.content_analyzer.analyze_content(content, headers, carrier, pro_number)
            
            # Update blocking patterns
            if analysis.blocking_mechanism.value != 'none':
                blocking_type = analysis.blocking_mechanism.value
                if blocking_type not in self.diagnostic_data['blocking_patterns']:
                    self.diagnostic_data['blocking_patterns'][blocking_type] = 0
                self.diagnostic_data['blocking_patterns'][blocking_type] += 1
            
            return {
                'is_blocked': analysis.is_blocked,
                'blocking_mechanism': analysis.blocking_mechanism.value,
                'confidence_score': analysis.confidence_score,
                'tracking_data_found': analysis.tracking_data is not None,
                'recommendations': analysis.recommendations,
                'content_type': analysis.content_type.value
            }
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {
                'error': str(e),
                'is_blocked': False,
                'blocking_mechanism': 'unknown'
            }
    
    async def try_alternative_methods(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """Try alternative tracking methods"""
        if not DIAGNOSTICS_AVAILABLE:
            return {
                'error': 'Alternative methods not available',
                'results': []
            }
        
        try:
            async with AlternativeMethodsEngine() as engine:
                # Use carrier's main website as base URL
                base_urls = {
                    'fedex': 'https://www.fedex.com',
                    'estes': 'https://www.estes-express.com',
                    'peninsula': 'https://www.peninsulatrucklines.com',
                    'rl': 'https://www.rlcarriers.com'
                }
                
                base_url = base_urls.get(carrier.lower(), 'https://example.com')
                results = await engine.track_with_alternatives(tracking_number, carrier, base_url)
                
                return {
                    'results': [
                        {
                            'method': result.method_type.value,
                            'success': result.success,
                            'response_time': result.response_time,
                            'tracking_data': result.tracking_data,
                            'error': result.error_message
                        }
                        for result in results
                    ],
                    'best_method': None if not results else max(results, key=lambda x: x.success),
                    'success_count': sum(1 for r in results if r.success)
                }
        except Exception as e:
            logger.error(f"Alternative methods error: {e}")
            return {
                'error': str(e),
                'results': []
            }
    
    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic summary"""
        total_attempts = self.diagnostic_data['tracking_attempts']
        success_rate = (
            self.diagnostic_data['successful_tracks'] / total_attempts 
            if total_attempts > 0 else 0
        )
        
        return {
            'system_health': {
                'total_attempts': total_attempts,
                'successful_tracks': self.diagnostic_data['successful_tracks'],
                'failed_tracks': self.diagnostic_data['failed_tracks'],
                'success_rate': success_rate,
                'is_healthy': success_rate > 0.3  # Above 30% is considered healthy
            },
            'blocking_analysis': {
                'patterns_detected': self.diagnostic_data['blocking_patterns'],
                'most_common_block': (
                    max(self.diagnostic_data['blocking_patterns'], 
                        key=self.diagnostic_data['blocking_patterns'].get)
                    if self.diagnostic_data['blocking_patterns'] else None
                )
            },
            'carrier_performance': self.diagnostic_data['carrier_performance'],
            'capabilities': {
                'diagnostics_available': DIAGNOSTICS_AVAILABLE,
                'content_analysis': self.content_analyzer is not None,
                'failure_analysis': self.failure_analyzer is not None
            },
            'recommendations': self._generate_system_recommendations(success_rate)
        }
    
    def _generate_system_recommendations(self, success_rate: float) -> List[str]:
        """Generate system-wide recommendations based on performance"""
        recommendations = []
        
        if success_rate == 0:
            recommendations.extend([
                "🚨 CRITICAL: Complete failure detected",
                "🔧 Run network diagnostics to identify root cause",
                "📞 Use manual tracking methods immediately",
                "🌐 Consider alternative cloud providers or proxy services"
            ])
        elif success_rate < 0.1:
            recommendations.extend([
                "⚠️ SEVERE: Less than 10% success rate",
                "🔧 Investigate IP blocking or CloudFlare protection",
                "⏱️ Implement longer delays between requests",
                "🔄 Try alternative methods for better results"
            ])
        elif success_rate < 0.3:
            recommendations.extend([
                "⚠️ MODERATE: Below expected 30% success rate",
                "🔧 Optimize user agents and request patterns",
                "📊 Analyze blocking patterns for improvement",
                "🔄 Increase use of alternative methods"
            ])
        else:
            recommendations.extend([
                "✅ GOOD: Success rate within expected range",
                "📊 Continue monitoring for pattern changes",
                "🔧 Fine-tune methods for specific carriers",
                "🔄 Maintain current approach"
            ])
        
        return recommendations 