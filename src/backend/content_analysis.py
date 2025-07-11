#!/usr/bin/env python3
"""
Content Analysis System for LTL Tracking
Advanced analysis of response content to detect blocking mechanisms, extract tracking data, and provide intelligent failure analysis
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import html
from urllib.parse import urlparse, parse_qs
import base64

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content detected"""
    HTML = "html"
    JSON = "json"
    XML = "xml"
    JAVASCRIPT = "javascript"
    CSS = "css"
    PLAIN_TEXT = "plain_text"
    BINARY = "binary"
    UNKNOWN = "unknown"


class BlockingMechanism(Enum):
    """Specific blocking mechanisms detected"""
    CLOUDFLARE_CHALLENGE = "cloudflare_challenge"
    CLOUDFLARE_DDOS = "cloudflare_ddos"
    RECAPTCHA = "recaptcha"
    HCAPTCHA = "hcaptcha"
    CUSTOM_CAPTCHA = "custom_captcha"
    IP_WHITELIST = "ip_whitelist"
    GEOGRAPHIC_BLOCK = "geographic_block"
    USER_AGENT_FILTER = "user_agent_filter"
    RATE_LIMIT_SOFT = "rate_limit_soft"
    RATE_LIMIT_HARD = "rate_limit_hard"
    LOGIN_WALL = "login_wall"
    PAYWALL = "paywall"
    MAINTENANCE_MODE = "maintenance_mode"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"
    JAVASCRIPT_CHALLENGE = "javascript_challenge"
    BROWSER_CHECK = "browser_check"
    NONE = "none"


@dataclass
class ContentAnalysisResult:
    """Result of content analysis"""
    content_type: ContentType
    blocking_mechanism: BlockingMechanism
    is_blocked: bool
    confidence_score: float  # 0.0 to 1.0
    blocking_details: Dict[str, Any]
    tracking_data: Optional[Dict[str, Any]] = None
    recommendations: List[str] = None
    extracted_patterns: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.extracted_patterns is None:
            self.extracted_patterns = []


class ContentAnalyzer:
    """
    Advanced content analysis system
    Detects blocking mechanisms, extracts tracking data, and provides intelligent analysis
    """
    
    def __init__(self):
        # Blocking pattern definitions
        self.blocking_patterns = {
            BlockingMechanism.CLOUDFLARE_CHALLENGE: {
                'patterns': [
                    r'checking your browser',
                    r'ddos protection by cloudflare',
                    r'please wait while we verify',
                    r'cloudflare ray id',
                    r'cf-ray',
                    r'__cf_chl_jschl_tk__',
                    r'cloudflare-nginx',
                    r'attention required.*cloudflare'
                ],
                'headers': ['cf-ray', 'cf-cache-status', 'cloudflare-nginx'],
                'confidence_boost': 0.9
            },
            BlockingMechanism.CLOUDFLARE_DDOS: {
                'patterns': [
                    r'this website is using a security service',
                    r'cloudflare.*ddos',
                    r'under attack mode',
                    r'security check.*cloudflare'
                ],
                'headers': ['cf-ray'],
                'confidence_boost': 0.8
            },
            BlockingMechanism.RECAPTCHA: {
                'patterns': [
                    r'recaptcha',
                    r'g-recaptcha',
                    r'google.*recaptcha',
                    r'please complete the captcha',
                    r'recaptcha_response_field'
                ],
                'confidence_boost': 0.9
            },
            BlockingMechanism.HCAPTCHA: {
                'patterns': [
                    r'hcaptcha',
                    r'h-captcha',
                    r'hcaptcha\.com',
                    r'please complete.*captcha'
                ],
                'confidence_boost': 0.9
            },
            BlockingMechanism.CUSTOM_CAPTCHA: {
                'patterns': [
                    r'captcha',
                    r'prove you are human',
                    r'security verification',
                    r'robot verification',
                    r'enter the characters',
                    r'verify you are not a robot'
                ],
                'confidence_boost': 0.7
            },
            BlockingMechanism.IP_WHITELIST: {
                'patterns': [
                    r'ip.*not.*authorized',
                    r'ip.*blocked',
                    r'access denied.*ip',
                    r'unauthorized ip address',
                    r'ip.*whitelist',
                    r'your ip.*blocked'
                ],
                'confidence_boost': 0.8
            },
            BlockingMechanism.GEOGRAPHIC_BLOCK: {
                'patterns': [
                    r'not available in your region',
                    r'geographic.*restriction',
                    r'location.*blocked',
                    r'country.*blocked',
                    r'vpn.*detected',
                    r'proxy.*detected',
                    r'geo.*blocked'
                ],
                'confidence_boost': 0.8
            },
            BlockingMechanism.USER_AGENT_FILTER: {
                'patterns': [
                    r'user agent.*blocked',
                    r'bot.*detected',
                    r'automated.*request',
                    r'script.*detected',
                    r'crawler.*blocked',
                    r'invalid.*user.*agent'
                ],
                'confidence_boost': 0.8
            },
            BlockingMechanism.RATE_LIMIT_SOFT: {
                'patterns': [
                    r'rate limit.*exceeded',
                    r'too many requests',
                    r'slow down',
                    r'try again.*later',
                    r'request.*throttled'
                ],
                'headers': ['x-ratelimit-limit', 'x-rate-limit-remaining', 'retry-after'],
                'confidence_boost': 0.9
            },
            BlockingMechanism.RATE_LIMIT_HARD: {
                'patterns': [
                    r'429.*too many requests',
                    r'rate limit.*exceeded.*permanently',
                    r'blocked due to excessive requests'
                ],
                'headers': ['retry-after'],
                'confidence_boost': 0.9
            },
            BlockingMechanism.LOGIN_WALL: {
                'patterns': [
                    r'please log in',
                    r'login required',
                    r'sign in to continue',
                    r'authentication required',
                    r'please sign in',
                    r'account required'
                ],
                'confidence_boost': 0.8
            },
            BlockingMechanism.PAYWALL: {
                'patterns': [
                    r'subscription required',
                    r'premium.*required',
                    r'upgrade.*account',
                    r'payment.*required'
                ],
                'confidence_boost': 0.7
            },
            BlockingMechanism.MAINTENANCE_MODE: {
                'patterns': [
                    r'under maintenance',
                    r'temporarily unavailable',
                    r'scheduled maintenance',
                    r'system.*maintenance',
                    r'service.*temporarily.*unavailable'
                ],
                'confidence_boost': 0.9
            },
            BlockingMechanism.SERVER_ERROR: {
                'patterns': [
                    r'500.*internal server error',
                    r'502.*bad gateway',
                    r'503.*service unavailable',
                    r'504.*gateway timeout',
                    r'server error'
                ],
                'confidence_boost': 0.9
            },
            BlockingMechanism.JAVASCRIPT_CHALLENGE: {
                'patterns': [
                    r'javascript.*required',
                    r'please enable javascript',
                    r'js.*challenge',
                    r'javascript.*disabled'
                ],
                'confidence_boost': 0.8
            },
            BlockingMechanism.BROWSER_CHECK: {
                'patterns': [
                    r'browser.*check',
                    r'verify.*browser',
                    r'browser.*verification',
                    r'checking.*browser'
                ],
                'confidence_boost': 0.8
            }
        }
        
        # Tracking data extraction patterns
        self.tracking_patterns = {
            'status': [
                r'status["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'tracking[_\s]?status["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'shipment[_\s]?status["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'delivery[_\s]?status["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'<span[^>]*status[^>]*>([^<]+)</span>',
                r'<div[^>]*status[^>]*>([^<]+)</div>'
            ],
            'location': [
                r'location["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'current[_\s]?location["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'origin["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'destination["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'<span[^>]*location[^>]*>([^<]+)</span>',
                r'<div[^>]*location[^>]*>([^<]+)</div>'
            ],
            'timestamp': [
                r'timestamp["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'updated[_\s]?at["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'last[_\s]?updated["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'date["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b'
            ],
            'pro_number': [
                r'pro[_\s]?number["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'tracking[_\s]?number["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'shipment[_\s]?id["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'reference[_\s]?number["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)'
            ],
            'carrier': [
                r'carrier["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'scac["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)',
                r'service[_\s]?provider["\']?\s*[:=]\s*["\']?([^"\'<>,\n]+)'
            ]
        }
        
        # Valid status indicators
        self.valid_statuses = {
            'delivered', 'out for delivery', 'in transit', 'picked up', 'departed',
            'arrived', 'on vehicle', 'at terminal', 'scheduled', 'pending',
            'exception', 'delayed', 'cancelled', 'returned', 'damaged'
        }
        
        # Error indicators
        self.error_indicators = {
            'not found', 'invalid', 'error', 'unable to track', 'no information',
            'no data', 'not available', 'system error', 'timeout', 'failed'
        }
    
    def analyze_content(self, content: str, headers: Dict[str, str] = None, 
                       carrier: str = None, pro_number: str = None) -> ContentAnalysisResult:
        """
        Analyze content for blocking mechanisms and tracking data
        
        Args:
            content: Response content to analyze
            headers: HTTP response headers
            carrier: Carrier name for context
            pro_number: PRO number for context
            
        Returns:
            ContentAnalysisResult with analysis details
        """
        if headers is None:
            headers = {}
        
        # Detect content type
        content_type = self._detect_content_type(content, headers)
        
        # Detect blocking mechanisms
        blocking_mechanism, confidence_score, blocking_details = self._detect_blocking_mechanism(content, headers)
        
        # Determine if content is blocked
        is_blocked = blocking_mechanism != BlockingMechanism.NONE
        
        # Extract tracking data if not blocked
        tracking_data = None
        if not is_blocked:
            tracking_data = self._extract_tracking_data(content, carrier, pro_number)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            blocking_mechanism, tracking_data, carrier, confidence_score
        )
        
        # Extract patterns for debugging
        extracted_patterns = self._extract_debug_patterns(content, blocking_mechanism)
        
        return ContentAnalysisResult(
            content_type=content_type,
            blocking_mechanism=blocking_mechanism,
            is_blocked=is_blocked,
            confidence_score=confidence_score,
            blocking_details=blocking_details,
            tracking_data=tracking_data,
            recommendations=recommendations,
            extracted_patterns=extracted_patterns
        )
    
    def _detect_content_type(self, content: str, headers: Dict[str, str]) -> ContentType:
        """Detect the type of content"""
        content_type_header = headers.get('content-type', '').lower()
        
        if 'application/json' in content_type_header:
            return ContentType.JSON
        elif 'text/html' in content_type_header:
            return ContentType.HTML
        elif 'application/xml' in content_type_header or 'text/xml' in content_type_header:
            return ContentType.XML
        elif 'application/javascript' in content_type_header or 'text/javascript' in content_type_header:
            return ContentType.JAVASCRIPT
        elif 'text/css' in content_type_header:
            return ContentType.CSS
        elif 'text/plain' in content_type_header:
            return ContentType.PLAIN_TEXT
        
        # Content-based detection
        content_trimmed = content.strip()
        
        if content_trimmed.startswith('{') and content_trimmed.endswith('}'):
            return ContentType.JSON
        elif content_trimmed.startswith('[') and content_trimmed.endswith(']'):
            return ContentType.JSON
        elif content_trimmed.startswith('<?xml') or content_trimmed.startswith('<xml'):
            return ContentType.XML
        elif content_trimmed.startswith('<!DOCTYPE') or content_trimmed.startswith('<html'):
            return ContentType.HTML
        elif '<html' in content_trimmed.lower() or '<body' in content_trimmed.lower():
            return ContentType.HTML
        elif any(js_indicator in content_trimmed for js_indicator in ['function(', 'var ', 'const ', 'let ']):
            return ContentType.JAVASCRIPT
        
        # Check for binary content
        try:
            content.encode('utf-8')
            return ContentType.PLAIN_TEXT
        except UnicodeEncodeError:
            return ContentType.BINARY
    
    def _detect_blocking_mechanism(self, content: str, headers: Dict[str, str]) -> Tuple[BlockingMechanism, float, Dict[str, Any]]:
        """Detect blocking mechanisms with confidence scoring"""
        content_lower = content.lower()
        header_keys = [k.lower() for k in headers.keys()]
        header_values = [str(v).lower() for v in headers.values()]
        
        best_match = BlockingMechanism.NONE
        best_confidence = 0.0
        best_details = {}
        
        for mechanism, config in self.blocking_patterns.items():
            confidence = 0.0
            details = {'matches': [], 'headers': []}
            
            # Check content patterns
            for pattern in config['patterns']:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    confidence += 0.3
                    details['matches'].append({'pattern': pattern, 'matches': matches})
            
            # Check header patterns
            if 'headers' in config:
                for header_pattern in config['headers']:
                    header_pattern_lower = header_pattern.lower()
                    if header_pattern_lower in header_keys:
                        confidence += 0.4
                        details['headers'].append(header_pattern)
                    elif any(header_pattern_lower in hv for hv in header_values):
                        confidence += 0.3
                        details['headers'].append(header_pattern)
            
            # Apply confidence boost
            if confidence > 0:
                confidence *= config.get('confidence_boost', 1.0)
                confidence = min(confidence, 1.0)  # Cap at 1.0
            
            # Update best match
            if confidence > best_confidence:
                best_match = mechanism
                best_confidence = confidence
                best_details = details
        
        return best_match, best_confidence, best_details
    
    def _extract_tracking_data(self, content: str, carrier: str = None, pro_number: str = None) -> Optional[Dict[str, Any]]:
        """Extract tracking data from content"""
        tracking_data = {}
        
        # Try JSON extraction first
        json_data = self._extract_json_data(content)
        if json_data:
            tracking_data.update(json_data)
        
        # Try pattern-based extraction
        for field, patterns in self.tracking_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Take the first non-empty match
                    value = next((m.strip() for m in matches if m.strip()), None)
                    if value:
                        tracking_data[field] = self._clean_extracted_value(value)
                        break
        
        # Validate tracking data
        if tracking_data:
            tracking_data = self._validate_tracking_data(tracking_data, carrier, pro_number)
        
        return tracking_data if tracking_data else None
    
    def _extract_json_data(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON data from content"""
        try:
            # Try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON objects in HTML
        json_patterns = [
            r'<script[^>]*>.*?var\s+\w+\s*=\s*(\{.*?\});',
            r'<script[^>]*>.*?(\{.*?"status".*?\})',
            r'<script[^>]*>.*?(\{.*?"tracking".*?\})',
            r'window\.\w+\s*=\s*(\{.*?\});',
            r'data-\w+\s*=\s*["\'](\{.*?\})["\']'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _clean_extracted_value(self, value: str) -> str:
        """Clean extracted values"""
        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Decode HTML entities
        value = html.unescape(value)
        
        # Remove extra whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Remove quotes
        value = value.strip('"\'')
        
        return value
    
    def _validate_tracking_data(self, tracking_data: Dict[str, Any], carrier: str = None, pro_number: str = None) -> Dict[str, Any]:
        """Validate and clean tracking data"""
        validated_data = {}
        
        for field, value in tracking_data.items():
            if isinstance(value, str):
                value = value.strip()
                
                # Skip empty values
                if not value or value.lower() in ['null', 'none', 'undefined', '']:
                    continue
                
                # Validate status
                if field == 'status':
                    if any(status in value.lower() for status in self.valid_statuses):
                        validated_data[field] = value
                    elif any(error in value.lower() for error in self.error_indicators):
                        validated_data['error'] = value
                
                # Validate other fields
                elif field in ['location', 'timestamp', 'pro_number', 'carrier']:
                    if len(value) > 2:  # Minimum length check
                        validated_data[field] = value
                
                # Keep any other field as is
                else:
                    validated_data[field] = value
        
        return validated_data
    
    def _generate_recommendations(self, blocking_mechanism: BlockingMechanism, 
                                 tracking_data: Optional[Dict[str, Any]], 
                                 carrier: str = None, confidence_score: float = 0.0) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if blocking_mechanism == BlockingMechanism.NONE:
            if tracking_data:
                recommendations.append("✅ No blocking detected - tracking data extracted successfully")
            else:
                recommendations.append("⚠️ No blocking detected but no tracking data found")
                recommendations.append("💡 Try: Different URL patterns, form submission, API endpoints")
        
        elif blocking_mechanism == BlockingMechanism.CLOUDFLARE_CHALLENGE:
            recommendations.append("🌐 CloudFlare challenge detected")
            recommendations.append("💡 Try: Residential proxies, slower request patterns, browser fingerprinting")
            recommendations.append("🔧 Consider: Third-party tracking services, mobile endpoints")
        
        elif blocking_mechanism == BlockingMechanism.RECAPTCHA:
            recommendations.append("🤖 reCAPTCHA detected")
            recommendations.append("💡 Try: Different endpoints, mobile APIs, guest tracking forms")
            recommendations.append("🔧 Consider: Captcha solving services, alternative carrier contact")
        
        elif blocking_mechanism == BlockingMechanism.RATE_LIMIT_SOFT:
            recommendations.append("⏱️ Rate limiting detected")
            recommendations.append("💡 Try: Increase delays (5-10 seconds), distribute requests")
            recommendations.append("🔧 Consider: Request batching, off-peak timing")
        
        elif blocking_mechanism == BlockingMechanism.RATE_LIMIT_HARD:
            recommendations.append("🚫 Hard rate limiting detected")
            recommendations.append("💡 Try: Different IP addresses, longer delays (1+ hour)")
            recommendations.append("🔧 Consider: Alternative tracking methods, manual contact")
        
        elif blocking_mechanism == BlockingMechanism.IP_WHITELIST:
            recommendations.append("🚫 IP blocking detected")
            recommendations.append("💡 Try: Proxy rotation, different cloud providers")
            recommendations.append("🔧 Consider: Residential IP services, manual tracking")
        
        elif blocking_mechanism == BlockingMechanism.LOGIN_WALL:
            recommendations.append("🔐 Login required detected")
            recommendations.append("💡 Try: Guest endpoints, mobile APIs, public tracking pages")
            recommendations.append("🔧 Consider: Account creation, alternative methods")
        
        elif blocking_mechanism == BlockingMechanism.GEOGRAPHIC_BLOCK:
            recommendations.append("🌍 Geographic blocking detected")
            recommendations.append("💡 Try: US-based proxies, different regions")
            recommendations.append("🔧 Consider: Regional cloud providers, manual contact")
        
        elif blocking_mechanism == BlockingMechanism.USER_AGENT_FILTER:
            recommendations.append("🤖 User agent filtering detected")
            recommendations.append("💡 Try: Rotate user agents, use legitimate browser signatures")
            recommendations.append("🔧 Consider: Mobile user agents, legitimate crawler UAs")
        
        elif blocking_mechanism == BlockingMechanism.MAINTENANCE_MODE:
            recommendations.append("🔧 Maintenance mode detected")
            recommendations.append("💡 Try: Wait and retry, check carrier announcements")
            recommendations.append("🔧 Consider: Alternative carriers, manual contact")
        
        elif blocking_mechanism == BlockingMechanism.SERVER_ERROR:
            recommendations.append("🚨 Server error detected")
            recommendations.append("💡 Try: Wait and retry, different endpoints")
            recommendations.append("🔧 Consider: Alternative carriers, manual contact")
        
        # Add confidence information
        if confidence_score > 0.8:
            recommendations.append(f"🎯 High confidence detection ({confidence_score:.1%})")
        elif confidence_score > 0.5:
            recommendations.append(f"⚠️ Medium confidence detection ({confidence_score:.1%})")
        else:
            recommendations.append(f"❓ Low confidence detection ({confidence_score:.1%})")
        
        return recommendations
    
    def _extract_debug_patterns(self, content: str, blocking_mechanism: BlockingMechanism) -> List[str]:
        """Extract patterns for debugging purposes"""
        patterns = []
        
        if blocking_mechanism in self.blocking_patterns:
            config = self.blocking_patterns[blocking_mechanism]
            for pattern in config['patterns']:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    patterns.append(f"{pattern} -> {matches[:3]}")  # First 3 matches
        
        return patterns
    
    def bulk_analyze(self, content_list: List[Tuple[str, Dict[str, str]]], 
                    carrier: str = None) -> List[ContentAnalysisResult]:
        """Analyze multiple content items efficiently"""
        results = []
        
        for content, headers in content_list:
            result = self.analyze_content(content, headers, carrier)
            results.append(result)
        
        return results
    
    def generate_analysis_report(self, results: List[ContentAnalysisResult]) -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""
        if not results:
            return {"error": "No results to analyze"}
        
        report = {
            "timestamp": datetime.now(),
            "total_analyzed": len(results),
            "summary": {
                "blocked_count": sum(1 for r in results if r.is_blocked),
                "success_count": sum(1 for r in results if not r.is_blocked),
                "tracking_data_found": sum(1 for r in results if r.tracking_data),
                "success_rate": sum(1 for r in results if not r.is_blocked) / len(results)
            },
            "blocking_mechanisms": {},
            "content_types": {},
            "recommendations": []
        }
        
        # Analyze blocking mechanisms
        for result in results:
            mechanism = result.blocking_mechanism.value
            if mechanism not in report["blocking_mechanisms"]:
                report["blocking_mechanisms"][mechanism] = 0
            report["blocking_mechanisms"][mechanism] += 1
            
            content_type = result.content_type.value
            if content_type not in report["content_types"]:
                report["content_types"][content_type] = 0
            report["content_types"][content_type] += 1
        
        # Generate overall recommendations
        if report["summary"]["success_rate"] == 0:
            report["recommendations"].append("🚨 Complete blocking detected - consider alternative methods")
        elif report["summary"]["success_rate"] < 0.3:
            report["recommendations"].append("⚠️ High blocking rate - optimization required")
        elif report["summary"]["success_rate"] < 0.7:
            report["recommendations"].append("⚠️ Moderate blocking - fine-tuning recommended")
        else:
            report["recommendations"].append("✅ Good success rate - monitor and maintain")
        
        # Most common blocking mechanism
        if report["blocking_mechanisms"]:
            most_common = max(report["blocking_mechanisms"], key=report["blocking_mechanisms"].get)
            if most_common != "none":
                report["recommendations"].append(f"🎯 Primary issue: {most_common.replace('_', ' ').title()}")
        
        return report


def analyze_carrier_response(content: str, headers: Dict[str, str] = None, 
                           carrier: str = None, pro_number: str = None) -> ContentAnalysisResult:
    """
    Convenience function to analyze a single carrier response
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(content, headers, carrier, pro_number)


def analyze_multiple_responses(responses: List[Tuple[str, Dict[str, str]]], 
                             carrier: str = None) -> List[ContentAnalysisResult]:
    """
    Convenience function to analyze multiple responses
    """
    analyzer = ContentAnalyzer()
    return analyzer.bulk_analyze(responses, carrier)


if __name__ == "__main__":
    # Example usage
    analyzer = ContentAnalyzer()
    
    # Test blocking detection
    cloudflare_content = """
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <h1>Please wait while we verify your browser...</h1>
        <p>DDoS protection by Cloudflare</p>
        <p>Ray ID: 123456789</p>
    </body>
    </html>
    """
    
    headers = {"cf-ray": "123456789", "server": "cloudflare-nginx"}
    
    result = analyzer.analyze_content(cloudflare_content, headers, "fedex")
    print(f"Blocking mechanism: {result.blocking_mechanism}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Recommendations: {result.recommendations}") 