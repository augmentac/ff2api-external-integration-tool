#!/usr/bin/env python3
"""
Enhanced UX System for LTL Tracking
Provides intelligent failure analysis, specific recommendations, and comprehensive manual tracking guidance
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import json

logger = logging.getLogger(__name__)


class FailureCategory(Enum):
    """Categories of tracking failures"""
    INFRASTRUCTURE_BLOCKING = "infrastructure_blocking"
    CARRIER_PROTECTION = "carrier_protection"
    RATE_LIMITING = "rate_limiting"
    AUTHENTICATION_REQUIRED = "authentication_required"
    SYSTEM_MAINTENANCE = "system_maintenance"
    NETWORK_ERROR = "network_error"
    INVALID_PRO = "invalid_pro"
    CARRIER_SYSTEM_DOWN = "carrier_system_down"
    UNKNOWN = "unknown"


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class TrackingRecommendation:
    """Individual tracking recommendation"""
    title: str
    description: str
    priority: RecommendationPriority
    action_type: str  # 'technical', 'manual', 'contact', 'wait'
    estimated_time: Optional[str] = None
    success_probability: Optional[float] = None
    instructions: List[str] = field(default_factory=list)
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class ManualTrackingGuide:
    """Complete manual tracking guide for a carrier"""
    carrier_name: str
    website_url: str
    phone_number: str
    email: Optional[str] = None
    hours_of_operation: Optional[str] = None
    tracking_url: Optional[str] = None
    step_by_step_instructions: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)
    alternative_methods: List[str] = field(default_factory=list)
    common_issues: List[str] = field(default_factory=list)


@dataclass
class FailureAnalysisResult:
    """Result of failure analysis"""
    failure_category: FailureCategory
    confidence_score: float
    root_cause: str
    user_friendly_explanation: str
    recommendations: List[TrackingRecommendation]
    manual_tracking_guide: Optional[ManualTrackingGuide] = None
    technical_details: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)


class CarrierContactDatabase:
    """Database of carrier contact information and manual tracking guides"""
    
    def __init__(self):
        self.carrier_info = {
            'fedex': {
                'name': 'FedEx Freight',
                'website': 'https://www.fedex.com',
                'phone': '1-800-463-3339',
                'email': 'wecare@fedex.com',
                'hours': 'Monday-Friday 8 AM - 6 PM EST',
                'tracking_url': 'https://www.fedex.com/fedextrack/',
                'customer_service_url': 'https://www.fedex.com/en-us/customer-support.html',
                'manual_steps': [
                    "Visit https://www.fedex.com/fedextrack/",
                    "Enter your PRO number in the 'Track a Package' field",
                    "Click 'Track' to view shipment status",
                    "For detailed information, click 'View Details'",
                    "If tracking fails, call 1-800-463-3339 with your PRO number ready"
                ],
                'tips': [
                    "FedEx PRO numbers are typically 8-12 digits",
                    "Try both with and without spaces/dashes",
                    "Have your reference number ready as backup",
                    "Business hours tracking is most reliable"
                ],
                'alternatives': [
                    "Call customer service at 1-800-463-3339",
                    "Use FedEx mobile app",
                    "Contact your shipper for tracking details",
                    "Visit a FedEx location in person"
                ],
                'common_issues': [
                    "New shipments may take 2-4 hours to appear in system",
                    "Some tracking requires login for detailed information",
                    "International shipments may have different tracking numbers"
                ]
            },
            'estes': {
                'name': 'Estes Express Lines',
                'website': 'https://www.estes-express.com',
                'phone': '1-866-378-3748',
                'email': 'customerservice@estes-express.com',
                'hours': 'Monday-Friday 8 AM - 5 PM EST',
                'tracking_url': 'https://www.estes-express.com/myestes/shipment-tracking',
                'customer_service_url': 'https://www.estes-express.com/contact-us',
                'manual_steps': [
                    "Visit https://www.estes-express.com/myestes/shipment-tracking",
                    "Enter your PRO number in the tracking field",
                    "Click 'Track Shipment' to view status",
                    "For detailed tracking, you may need to create a free MyEstes account",
                    "Call 1-866-378-3748 if tracking is unavailable"
                ],
                'tips': [
                    "Estes PRO numbers are typically 7-10 digits",
                    "Try entering without leading zeros",
                    "MyEstes account provides more detailed tracking",
                    "Mobile website sometimes works better than desktop"
                ],
                'alternatives': [
                    "Call customer service at 1-866-378-3748",
                    "Create a MyEstes account for detailed tracking",
                    "Contact your shipper for updates",
                    "Visit an Estes terminal location"
                ],
                'common_issues': [
                    "Some tracking requires MyEstes account login",
                    "Real-time GPS tracking may not be available for all shipments",
                    "Tracking may be delayed for new shipments"
                ]
            },
            'peninsula': {
                'name': 'Peninsula Truck Lines',
                'website': 'https://www.peninsulatrucklines.com',
                'phone': '1-800-840-6400',
                'email': 'customerservice@peninsulatrucklines.com',
                'hours': 'Monday-Friday 7 AM - 6 PM PST',
                'tracking_url': 'https://www.peninsulatrucklines.com/track-shipment',
                'customer_service_url': 'https://www.peninsulatrucklines.com/contact-us',
                'manual_steps': [
                    "Visit https://www.peninsulatrucklines.com/track-shipment",
                    "Enter your PRO number in the tracking field",
                    "Click 'Track' to view shipment status",
                    "For detailed information, call customer service",
                    "Have your reference number ready as backup"
                ],
                'tips': [
                    "Peninsula PRO numbers are typically 6-9 digits",
                    "Try both with and without dashes",
                    "Have shipper's reference number ready",
                    "Customer service is very helpful for detailed tracking"
                ],
                'alternatives': [
                    "Call customer service at 1-800-840-6400",
                    "Email customerservice@peninsulatrucklines.com",
                    "Contact your shipper for tracking details",
                    "Visit a Peninsula terminal location"
                ],
                'common_issues': [
                    "Online tracking may have limited detail",
                    "Phone support provides more comprehensive information",
                    "Some shipments require reference number for tracking"
                ]
            },
            'rl': {
                'name': 'R&L Carriers',
                'website': 'https://www.rlcarriers.com',
                'phone': '1-800-543-5589',
                'email': 'customerservice@rlcarriers.com',
                'hours': 'Monday-Friday 8 AM - 5 PM EST',
                'tracking_url': 'https://www.rlcarriers.com/tracking',
                'customer_service_url': 'https://www.rlcarriers.com/contact-us',
                'manual_steps': [
                    "Visit https://www.rlcarriers.com/tracking",
                    "Enter your PRO number in the tracking field",
                    "Click 'Track' to view shipment status",
                    "For detailed tracking, call customer service",
                    "Have your bill of lading number ready as backup"
                ],
                'tips': [
                    "R&L PRO numbers are typically 6-8 digits",
                    "Try entering without leading zeros",
                    "Bill of lading number can be used for tracking",
                    "Customer service provides real-time updates"
                ],
                'alternatives': [
                    "Call customer service at 1-800-543-5589",
                    "Email customerservice@rlcarriers.com",
                    "Use bill of lading number for tracking",
                    "Contact your shipper for updates"
                ],
                'common_issues': [
                    "Online tracking may not show all scan events",
                    "Phone support provides more detailed information",
                    "Some deliveries require appointment scheduling"
                ]
            }
        }
    
    def get_carrier_info(self, carrier: str) -> Optional[Dict[str, Any]]:
        """Get carrier contact information"""
        carrier_lower = carrier.lower()
        
        # Handle common variations
        if 'fedex' in carrier_lower:
            return self.carrier_info.get('fedex')
        elif 'estes' in carrier_lower:
            return self.carrier_info.get('estes')
        elif 'peninsula' in carrier_lower:
            return self.carrier_info.get('peninsula')
        elif 'r&l' in carrier_lower or 'rl' in carrier_lower:
            return self.carrier_info.get('rl')
        
        return None
    
    def get_manual_tracking_guide(self, carrier: str) -> Optional[ManualTrackingGuide]:
        """Get complete manual tracking guide for a carrier"""
        info = self.get_carrier_info(carrier)
        if not info:
            return None
        
        return ManualTrackingGuide(
            carrier_name=info['name'],
            website_url=info['website'],
            phone_number=info['phone'],
            email=info.get('email'),
            hours_of_operation=info.get('hours'),
            tracking_url=info.get('tracking_url'),
            step_by_step_instructions=info.get('manual_steps', []),
            tips=info.get('tips', []),
            alternative_methods=info.get('alternatives', []),
            common_issues=info.get('common_issues', [])
        )


class FailureAnalyzer:
    """Analyzes tracking failures and provides intelligent recommendations"""
    
    def __init__(self):
        self.contact_db = CarrierContactDatabase()
        
        # Failure pattern mappings
        self.failure_patterns = {
            FailureCategory.INFRASTRUCTURE_BLOCKING: {
                'patterns': [
                    'cloudflare',
                    'cf-ray',
                    'ddos protection',
                    'security check',
                    'blocked',
                    'forbidden',
                    'access denied',
                    'ip.*blocked'
                ],
                'indicators': [
                    'uniform_failure_across_carriers',
                    'immediate_failures',
                    'network_level_blocking'
                ]
            },
            FailureCategory.CARRIER_PROTECTION: {
                'patterns': [
                    'captcha',
                    'recaptcha',
                    'bot.*detected',
                    'automated.*request',
                    'user.*agent.*blocked',
                    'suspicious.*activity'
                ],
                'indicators': [
                    'carrier_specific_blocking',
                    'content_based_blocking',
                    'challenge_response'
                ]
            },
            FailureCategory.RATE_LIMITING: {
                'patterns': [
                    'rate.*limit',
                    'too.*many.*requests',
                    'throttled',
                    'slow.*down',
                    'try.*again.*later'
                ],
                'indicators': [
                    'http_429',
                    'retry_after_header',
                    'rate_limit_headers'
                ]
            },
            FailureCategory.AUTHENTICATION_REQUIRED: {
                'patterns': [
                    'login.*required',
                    'authentication.*required',
                    'please.*sign.*in',
                    'account.*required',
                    'unauthorized'
                ],
                'indicators': [
                    'login_forms',
                    'auth_redirects',
                    'session_required'
                ]
            },
            FailureCategory.SYSTEM_MAINTENANCE: {
                'patterns': [
                    'maintenance',
                    'temporarily.*unavailable',
                    'scheduled.*maintenance',
                    'system.*down',
                    'under.*construction'
                ],
                'indicators': [
                    'maintenance_pages',
                    'service_unavailable',
                    'temporary_errors'
                ]
            },
            FailureCategory.NETWORK_ERROR: {
                'patterns': [
                    'connection.*failed',
                    'timeout',
                    'network.*error',
                    'dns.*error',
                    'connection.*refused'
                ],
                'indicators': [
                    'connection_timeouts',
                    'dns_failures',
                    'network_unreachable'
                ]
            },
            FailureCategory.INVALID_PRO: {
                'patterns': [
                    'invalid.*pro',
                    'not.*found',
                    'pro.*number.*invalid',
                    'shipment.*not.*found',
                    'tracking.*number.*invalid'
                ],
                'indicators': [
                    'pro_format_errors',
                    'not_found_responses',
                    'invalid_number_messages'
                ]
            }
        }
    
    def analyze_failure(self, error_message: str, carrier: str = None, 
                       technical_details: Dict[str, Any] = None) -> FailureAnalysisResult:
        """
        Analyze a tracking failure and provide intelligent recommendations
        
        Args:
            error_message: The error message from tracking attempt
            carrier: Carrier name
            technical_details: Additional technical information
            
        Returns:
            FailureAnalysisResult with analysis and recommendations
        """
        if technical_details is None:
            technical_details = {}
        
        # Determine failure category
        failure_category, confidence_score = self._categorize_failure(error_message, technical_details)
        
        # Generate root cause analysis
        root_cause = self._determine_root_cause(failure_category, error_message, technical_details)
        
        # Create user-friendly explanation
        user_explanation = self._create_user_explanation(failure_category, carrier, root_cause)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(failure_category, carrier, technical_details)
        
        # Get manual tracking guide
        manual_guide = self.contact_db.get_manual_tracking_guide(carrier) if carrier else None
        
        # Generate next steps
        next_steps = self._generate_next_steps(failure_category, carrier, recommendations)
        
        return FailureAnalysisResult(
            failure_category=failure_category,
            confidence_score=confidence_score,
            root_cause=root_cause,
            user_friendly_explanation=user_explanation,
            recommendations=recommendations,
            manual_tracking_guide=manual_guide,
            technical_details=technical_details,
            next_steps=next_steps
        )
    
    def _categorize_failure(self, error_message: str, technical_details: Dict[str, Any]) -> Tuple[FailureCategory, float]:
        """Categorize the type of failure"""
        error_lower = error_message.lower()
        
        # Check for specific indicators in technical details
        if technical_details.get('status_code') == 429:
            return FailureCategory.RATE_LIMITING, 0.9
        
        if technical_details.get('status_code') == 401:
            return FailureCategory.AUTHENTICATION_REQUIRED, 0.8
        
        if technical_details.get('status_code') == 503:
            return FailureCategory.SYSTEM_MAINTENANCE, 0.7
        
        # Pattern matching
        best_category = FailureCategory.UNKNOWN
        best_score = 0.0
        
        for category, config in self.failure_patterns.items():
            score = 0.0
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, error_lower):
                    score += 0.3
            
            # Check indicators
            for indicator in config.get('indicators', []):
                if indicator in technical_details:
                    score += 0.4
            
            # Special case for infrastructure blocking
            if category == FailureCategory.INFRASTRUCTURE_BLOCKING:
                if technical_details.get('uniform_failure_rate', 0) > 0.9:
                    score += 0.5
            
            if score > best_score:
                best_category = category
                best_score = score
        
        return best_category, min(best_score, 1.0)
    
    def _determine_root_cause(self, failure_category: FailureCategory, 
                            error_message: str, technical_details: Dict[str, Any]) -> str:
        """Determine the root cause of the failure"""
        if failure_category == FailureCategory.INFRASTRUCTURE_BLOCKING:
            return "Streamlit Cloud IP addresses are being blocked by carrier websites"
        
        elif failure_category == FailureCategory.CARRIER_PROTECTION:
            return "Carrier has implemented anti-automation protection (CAPTCHA, bot detection)"
        
        elif failure_category == FailureCategory.RATE_LIMITING:
            return "Too many requests sent to carrier website in short timeframe"
        
        elif failure_category == FailureCategory.AUTHENTICATION_REQUIRED:
            return "Carrier requires user login or authentication for tracking access"
        
        elif failure_category == FailureCategory.SYSTEM_MAINTENANCE:
            return "Carrier website is temporarily down for maintenance"
        
        elif failure_category == FailureCategory.NETWORK_ERROR:
            return "Network connectivity issues between cloud service and carrier website"
        
        elif failure_category == FailureCategory.INVALID_PRO:
            return "PRO number format is invalid or shipment not found in carrier system"
        
        else:
            return "Unknown tracking failure - requires manual investigation"
    
    def _create_user_explanation(self, failure_category: FailureCategory, 
                               carrier: str, root_cause: str) -> str:
        """Create user-friendly explanation"""
        carrier_name = carrier.title() if carrier else "the carrier"
        
        if failure_category == FailureCategory.INFRASTRUCTURE_BLOCKING:
            return f"""
            🚫 **Automatic tracking blocked by {carrier_name}**
            
            The carrier's website is blocking our automated tracking system. This is common with cloud-based 
            services like Streamlit Cloud, as carriers implement strict anti-automation measures to protect 
            their websites from excessive requests.
            
            **This is not an error with your PRO number** - it's a limitation of automated tracking from 
            cloud environments.
            """
        
        elif failure_category == FailureCategory.CARRIER_PROTECTION:
            return f"""
            🛡️ **{carrier_name} has anti-automation protection**
            
            The carrier's website detected our automated request and blocked it with security measures like 
            CAPTCHA or bot detection. This is designed to prevent automated systems from accessing their 
            tracking system.
            
            **Your PRO number is likely valid** - you'll need to track it manually or contact the carrier 
            directly.
            """
        
        elif failure_category == FailureCategory.RATE_LIMITING:
            return f"""
            ⏱️ **Too many tracking requests to {carrier_name}**
            
            The carrier's website is temporarily limiting our requests because we've exceeded their rate 
            limits. This is a protective measure to prevent their servers from being overwhelmed.
            
            **This is temporary** - you can try again later or use manual tracking methods.
            """
        
        elif failure_category == FailureCategory.AUTHENTICATION_REQUIRED:
            return f"""
            🔐 **{carrier_name} requires account login**
            
            The carrier requires users to sign in to their website to access detailed tracking information. 
            Our automated system cannot log in to carrier accounts.
            
            **You can still track your shipment** by logging into your carrier account or calling their 
            customer service.
            """
        
        elif failure_category == FailureCategory.SYSTEM_MAINTENANCE:
            return f"""
            🔧 **{carrier_name} website is under maintenance**
            
            The carrier's website is temporarily unavailable due to scheduled maintenance or technical issues. 
            This affects both automated and manual tracking.
            
            **This is temporary** - try again later or contact customer service for updates.
            """
        
        elif failure_category == FailureCategory.NETWORK_ERROR:
            return f"""
            🌐 **Network connectivity issues**
            
            There's a temporary network connectivity problem preventing our system from reaching the 
            carrier's website. This could be due to internet connectivity issues or carrier website problems.
            
            **Try again in a few minutes** or use manual tracking methods.
            """
        
        elif failure_category == FailureCategory.INVALID_PRO:
            return f"""
            ❓ **PRO number not found**
            
            The PRO number might be invalid, incorrectly formatted, or the shipment may not yet be in the 
            carrier's system. New shipments can take 2-4 hours to appear in tracking systems.
            
            **Double-check your PRO number** and try again, or contact the carrier directly.
            """
        
        else:
            return f"""
            ❓ **Unknown tracking issue**
            
            We encountered an unexpected issue while trying to track your shipment with {carrier_name}. 
            This could be due to various factors including website changes or technical issues.
            
            **We recommend manual tracking** or contacting the carrier directly for assistance.
            """
    
    def _generate_recommendations(self, failure_category: FailureCategory, 
                                carrier: str, technical_details: Dict[str, Any]) -> List[TrackingRecommendation]:
        """Generate specific recommendations based on failure type"""
        recommendations = []
        
        if failure_category == FailureCategory.INFRASTRUCTURE_BLOCKING:
            recommendations.extend([
                TrackingRecommendation(
                    title="Contact Carrier Directly",
                    description="Call or email the carrier's customer service for immediate tracking information",
                    priority=RecommendationPriority.CRITICAL,
                    action_type="contact",
                    estimated_time="2-5 minutes",
                    success_probability=0.95,
                    instructions=[
                        "Have your PRO number ready",
                        "Call during business hours for faster service",
                        "Ask for detailed tracking information and delivery estimates"
                    ]
                ),
                TrackingRecommendation(
                    title="Use Carrier's Official Website",
                    description="Track manually on the carrier's official website",
                    priority=RecommendationPriority.HIGH,
                    action_type="manual",
                    estimated_time="1-2 minutes",
                    success_probability=0.85,
                    instructions=[
                        "Visit the carrier's official tracking page",
                        "Enter your PRO number manually",
                        "Try variations (with/without spaces, leading zeros)"
                    ]
                ),
                TrackingRecommendation(
                    title="Contact Your Shipper",
                    description="Ask the shipper for tracking updates or alternative tracking methods",
                    priority=RecommendationPriority.MEDIUM,
                    action_type="contact",
                    estimated_time="5-10 minutes",
                    success_probability=0.80,
                    instructions=[
                        "Contact the person/company who shipped your item",
                        "Ask for tracking updates or delivery estimates",
                        "Request alternative tracking numbers if available"
                    ]
                )
            ])
        
        elif failure_category == FailureCategory.CARRIER_PROTECTION:
            recommendations.extend([
                TrackingRecommendation(
                    title="Try Manual Website Tracking",
                    description="Use the carrier's website directly in your browser",
                    priority=RecommendationPriority.HIGH,
                    action_type="manual",
                    estimated_time="2-3 minutes",
                    success_probability=0.90,
                    instructions=[
                        "Open the carrier's website in your browser",
                        "Navigate to the tracking page",
                        "Enter your PRO number manually",
                        "Complete any CAPTCHA if required"
                    ]
                ),
                TrackingRecommendation(
                    title="Use Mobile App",
                    description="Try the carrier's mobile app if available",
                    priority=RecommendationPriority.MEDIUM,
                    action_type="manual",
                    estimated_time="3-5 minutes",
                    success_probability=0.75,
                    instructions=[
                        "Download the carrier's mobile app",
                        "Enter your PRO number in the app",
                        "Mobile apps sometimes have different tracking systems"
                    ]
                )
            ])
        
        elif failure_category == FailureCategory.RATE_LIMITING:
            recommendations.extend([
                TrackingRecommendation(
                    title="Wait and Retry",
                    description="Wait 10-15 minutes before trying automatic tracking again",
                    priority=RecommendationPriority.MEDIUM,
                    action_type="wait",
                    estimated_time="10-15 minutes",
                    success_probability=0.70,
                    instructions=[
                        "Wait at least 10 minutes before retrying",
                        "Try again during off-peak hours",
                        "Consider manual tracking if urgent"
                    ]
                ),
                TrackingRecommendation(
                    title="Use Manual Tracking",
                    description="Track manually to avoid rate limits",
                    priority=RecommendationPriority.HIGH,
                    action_type="manual",
                    estimated_time="2-3 minutes",
                    success_probability=0.90
                )
            ])
        
        elif failure_category == FailureCategory.AUTHENTICATION_REQUIRED:
            recommendations.extend([
                TrackingRecommendation(
                    title="Create Free Account",
                    description="Create a free account on the carrier's website for detailed tracking",
                    priority=RecommendationPriority.MEDIUM,
                    action_type="manual",
                    estimated_time="5-10 minutes",
                    success_probability=0.85,
                    instructions=[
                        "Visit the carrier's website",
                        "Look for 'Sign Up' or 'Register' options",
                        "Create a free account",
                        "Log in and try tracking again"
                    ]
                ),
                TrackingRecommendation(
                    title="Try Guest Tracking",
                    description="Look for guest tracking options that don't require login",
                    priority=RecommendationPriority.HIGH,
                    action_type="manual",
                    estimated_time="2-3 minutes",
                    success_probability=0.70
                )
            ])
        
        elif failure_category == FailureCategory.SYSTEM_MAINTENANCE:
            recommendations.extend([
                TrackingRecommendation(
                    title="Wait for Maintenance to Complete",
                    description="Check carrier's website for maintenance schedules and try again later",
                    priority=RecommendationPriority.MEDIUM,
                    action_type="wait",
                    estimated_time="1-4 hours",
                    success_probability=0.90
                ),
                TrackingRecommendation(
                    title="Call Customer Service",
                    description="Customer service can provide tracking information even during website maintenance",
                    priority=RecommendationPriority.HIGH,
                    action_type="contact",
                    estimated_time="3-10 minutes",
                    success_probability=0.95
                )
            ])
        
        elif failure_category == FailureCategory.INVALID_PRO:
            recommendations.extend([
                TrackingRecommendation(
                    title="Verify PRO Number",
                    description="Double-check your PRO number for accuracy",
                    priority=RecommendationPriority.CRITICAL,
                    action_type="manual",
                    estimated_time="1-2 minutes",
                    success_probability=0.60,
                    instructions=[
                        "Check for typos in the PRO number",
                        "Try with and without spaces or dashes",
                        "Try with and without leading zeros",
                        "Verify the number with your shipper"
                    ]
                ),
                TrackingRecommendation(
                    title="Wait for System Update",
                    description="New shipments take 2-4 hours to appear in tracking systems",
                    priority=RecommendationPriority.MEDIUM,
                    action_type="wait",
                    estimated_time="2-4 hours",
                    success_probability=0.80
                )
            ])
        
        # Add carrier-specific contact info
        if carrier:
            carrier_info = self.contact_db.get_carrier_info(carrier)
            if carrier_info:
                for rec in recommendations:
                    if rec.action_type == "contact":
                        rec.contact_info = {
                            'phone': carrier_info.get('phone'),
                            'email': carrier_info.get('email'),
                            'website': carrier_info.get('website'),
                            'hours': carrier_info.get('hours')
                        }
        
        return recommendations
    
    def _generate_next_steps(self, failure_category: FailureCategory, 
                           carrier: str, recommendations: List[TrackingRecommendation]) -> List[str]:
        """Generate prioritized next steps"""
        next_steps = []
        
        # Sort recommendations by priority
        priority_order = [
            RecommendationPriority.CRITICAL,
            RecommendationPriority.HIGH,
            RecommendationPriority.MEDIUM,
            RecommendationPriority.LOW
        ]
        
        sorted_recommendations = sorted(recommendations, key=lambda x: priority_order.index(x.priority))
        
        for i, rec in enumerate(sorted_recommendations[:3]):  # Top 3 recommendations
            if rec.estimated_time:
                next_steps.append(f"{i+1}. {rec.title} (estimated time: {rec.estimated_time})")
            else:
                next_steps.append(f"{i+1}. {rec.title}")
        
        return next_steps
    
    def bulk_analyze_failures(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze multiple failures to identify patterns"""
        if not failures:
            return {"error": "No failures to analyze"}
        
        # Analyze each failure
        analyses = []
        for failure in failures:
            analysis = self.analyze_failure(
                failure.get('error_message', ''),
                failure.get('carrier'),
                failure.get('technical_details', {})
            )
            analyses.append(analysis)
        
        # Generate bulk report
        report = {
            "timestamp": datetime.now(),
            "total_failures": len(failures),
            "failure_categories": {},
            "success_probability_by_carrier": {},
            "recommended_actions": [],
            "system_health": {
                "infrastructure_blocking_rate": 0,
                "carrier_protection_rate": 0,
                "rate_limiting_rate": 0,
                "authentication_rate": 0,
                "system_maintenance_rate": 0
            }
        }
        
        # Analyze patterns
        for analysis in analyses:
            category = analysis.failure_category.value
            if category not in report["failure_categories"]:
                report["failure_categories"][category] = 0
            report["failure_categories"][category] += 1
        
        # Calculate rates
        total = len(analyses)
        for category, count in report["failure_categories"].items():
            if category in report["system_health"]:
                report["system_health"][f"{category}_rate"] = count / total
        
        # Generate system-wide recommendations
        if report["system_health"]["infrastructure_blocking_rate"] > 0.8:
            report["recommended_actions"].append(
                "🚨 CRITICAL: Infrastructure-level blocking detected - consider alternative tracking methods"
            )
        
        if report["system_health"]["carrier_protection_rate"] > 0.5:
            report["recommended_actions"].append(
                "⚠️ High carrier protection rate - optimize user agent and request patterns"
            )
        
        if report["system_health"]["rate_limiting_rate"] > 0.3:
            report["recommended_actions"].append(
                "⏱️ Significant rate limiting - implement longer delays between requests"
            )
        
        return report


def analyze_tracking_failure(error_message: str, carrier: str = None, 
                           technical_details: Dict[str, Any] = None) -> FailureAnalysisResult:
    """
    Convenience function to analyze a tracking failure
    """
    analyzer = FailureAnalyzer()
    return analyzer.analyze_failure(error_message, carrier, technical_details)


def get_manual_tracking_guide(carrier: str) -> Optional[ManualTrackingGuide]:
    """
    Convenience function to get manual tracking guide
    """
    contact_db = CarrierContactDatabase()
    return contact_db.get_manual_tracking_guide(carrier)


def generate_failure_report(failures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to generate failure report
    """
    analyzer = FailureAnalyzer()
    return analyzer.bulk_analyze_failures(failures)


if __name__ == "__main__":
    # Example usage
    analyzer = FailureAnalyzer()
    
    # Test failure analysis
    failure_result = analyzer.analyze_failure(
        "All cloud-native tracking methods failed for FedEx",
        "fedex",
        {"uniform_failure_rate": 1.0, "status_code": 403}
    )
    
    print(f"Failure category: {failure_result.failure_category}")
    print(f"Root cause: {failure_result.root_cause}")
    print(f"User explanation: {failure_result.user_friendly_explanation}")
    print(f"Recommendations: {len(failure_result.recommendations)}")
    
    # Test manual tracking guide
    guide = get_manual_tracking_guide("fedex")
    if guide:
        print(f"\nManual tracking guide for {guide.carrier_name}:")
        print(f"Phone: {guide.phone_number}")
        print(f"Website: {guide.website_url}")
        print(f"Steps: {len(guide.step_by_step_instructions)}") 