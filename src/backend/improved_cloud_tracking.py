#!/usr/bin/env python3
"""
Improved Cloud Tracking System
Uses working barrier-breaking methods when available, with cloud-compatible fallbacks
"""

import asyncio
import requests
import time
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Try to import working tracking systems
try:
    from .barrier_breaking_tracking_system import BarrierBreakingTrackingSystem
    BARRIER_BREAKING_AVAILABLE = True
except ImportError:
    BARRIER_BREAKING_AVAILABLE = False

try:
    from .apple_silicon_estes_client import AppleSiliconEstesClient
    APPLE_SILICON_AVAILABLE = True
except ImportError:
    APPLE_SILICON_AVAILABLE = False

try:
    from .cloud_browser_tracking import CloudBrowserTracker
    CLOUD_BROWSER_AVAILABLE = True
except ImportError:
    CLOUD_BROWSER_AVAILABLE = False

logger = logging.getLogger(__name__)

class ImprovedCloudTracker:
    """
    Improved cloud tracking system that uses working methods when available
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
        # Initialize available tracking systems
        self.barrier_breaking_system = None
        self.apple_silicon_system = None
        self.cloud_browser_system = None
        
        # Detect environment
        self.is_cloud = self.detect_cloud_environment()
        
        # Initialize systems based on availability and environment
        self.initialize_tracking_systems()
        
    def detect_cloud_environment(self) -> bool:
        """Detect if we're running in a cloud environment"""
        cloud_indicators = [
            'STREAMLIT_CLOUD',
            'HEROKU',
            'DYNO',
            'RAILWAY',
            'VERCEL',
            'NETLIFY',
            'AWS_LAMBDA',
            'GOOGLE_CLOUD_RUN'
        ]
        
        for indicator in cloud_indicators:
            if os.environ.get(indicator):
                return True
        
        hostname = os.environ.get('HOSTNAME', '').lower()
        if any(pattern in hostname for pattern in ['streamlit', 'heroku', 'railway', 'vercel']):
            return True
        
        return False
    
    def initialize_tracking_systems(self):
        """Initialize available tracking systems"""
        logger.info(f"Initializing tracking systems (cloud: {self.is_cloud})")
        
        if BARRIER_BREAKING_AVAILABLE:
            try:
                self.barrier_breaking_system = BarrierBreakingTrackingSystem()
                logger.info("✅ Barrier-breaking system initialized")
            except Exception as e:
                logger.warning(f"Barrier-breaking system initialization failed: {e}")
        
        if APPLE_SILICON_AVAILABLE and not self.is_cloud:
            try:
                self.apple_silicon_system = AppleSiliconEstesClient()
                logger.info("✅ Apple Silicon system initialized")
            except Exception as e:
                logger.warning(f"Apple Silicon system initialization failed: {e}")
        
        if CLOUD_BROWSER_AVAILABLE:
            try:
                self.cloud_browser_system = CloudBrowserTracker()
                logger.info("✅ Cloud browser system initialized")
            except Exception as e:
                logger.warning(f"Cloud browser system initialization failed: {e}")
    
    def setup_session(self):
        """Setup HTTP session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    async def track_shipment(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Main tracking method that uses the best available system
        """
        logger.info(f"🚀 Improved cloud tracking: {carrier} - {tracking_number}")
        
        # Method 1: Use barrier-breaking system if available (most reliable)
        if self.barrier_breaking_system:
            try:
                logger.info("🔧 Trying barrier-breaking system...")
                result = await self.barrier_breaking_system.track_single_shipment(tracking_number)
                
                if result.get('success'):
                    logger.info("✅ Barrier-breaking system successful!")
                    return self.format_result(result, tracking_number, carrier, "Barrier-Breaking System")
                else:
                    logger.warning(f"Barrier-breaking system failed: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Barrier-breaking system error: {e}")
        
        # Method 2: Use Apple Silicon system if available (local environment)
        if self.apple_silicon_system and not self.is_cloud:
            try:
                logger.info("🍎 Trying Apple Silicon system...")
                result = await self.apple_silicon_system.track_shipment(tracking_number)
                
                if result.get('success'):
                    logger.info("✅ Apple Silicon system successful!")
                    return self.format_result(result, tracking_number, carrier, "Apple Silicon System")
                else:
                    logger.warning(f"Apple Silicon system failed: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Apple Silicon system error: {e}")
        
        # Method 3: Use cloud browser system if available
        if self.cloud_browser_system:
            try:
                logger.info("🌐 Trying cloud browser system...")
                result = await self.cloud_browser_system.track_shipment(tracking_number, carrier)
                
                if result.get('success'):
                    logger.info("✅ Cloud browser system successful!")
                    return self.format_result(result, tracking_number, carrier, "Cloud Browser System")
                else:
                    logger.warning(f"Cloud browser system failed: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Cloud browser system error: {e}")
        
        # Method 4: Fallback to basic HTTP methods
        try:
            logger.info("🌐 Trying basic HTTP methods...")
            result = await self.track_basic_http(tracking_number, carrier)
            
            if result.get('success'):
                logger.info("✅ Basic HTTP methods successful!")
                return self.format_result(result, tracking_number, carrier, "Basic HTTP Methods")
            else:
                logger.warning(f"Basic HTTP methods failed: {result.get('error')}")
        except Exception as e:
            logger.warning(f"Basic HTTP methods error: {e}")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All tracking methods failed - modern carrier websites require browser automation',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time(),
            'system_used': 'None',
            'recommendation': self.get_recommendation(carrier)
        }
    
    def format_result(self, result: Dict[str, Any], tracking_number: str, carrier: str, system_used: str) -> Dict[str, Any]:
        """Format the result for consistent output"""
        return {
            'success': result.get('success', False),
            'status': result.get('status', 'No status available'),
            'location': result.get('location', 'No location available'),
            'events': result.get('events', []),
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time(),
            'system_used': system_used,
            'method': result.get('method', system_used),
            'barrier_solved': result.get('barrier_solved', ''),
            'duration': result.get('duration', 0),
            'error': result.get('error', '') if not result.get('success') else None
        }
    
    async def track_basic_http(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Basic HTTP tracking methods as fallback
        """
        try:
            if "estes" in carrier.lower():
                return await self.track_estes_http(tracking_number)
            elif "fedex" in carrier.lower():
                return await self.track_fedex_http(tracking_number)
            elif "peninsula" in carrier.lower():
                return await self.track_peninsula_http(tracking_number)
            elif "r&l" in carrier.lower():
                return await self.track_rl_http(tracking_number)
            else:
                return {'success': False, 'error': f'HTTP tracking not implemented for {carrier}'}
        except Exception as e:
            return {'success': False, 'error': f'HTTP tracking error: {str(e)}'}
    
    async def track_estes_http(self, tracking_number: str) -> Dict[str, Any]:
        """Basic HTTP tracking for Estes"""
        try:
            # Try to access the tracking page
            url = "https://www.estes-express.com/myestes/shipment-tracking/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200 and tracking_number in response.text:
                return {
                    'success': True,
                    'status': 'Tracking number found in system',
                    'location': 'Location data available',
                    'events': [],
                    'method': 'Basic HTTP'
                }
            else:
                return {'success': False, 'error': 'Tracking number not found via HTTP'}
        except Exception as e:
            return {'success': False, 'error': f'HTTP error: {str(e)}'}
    
    async def track_fedex_http(self, tracking_number: str) -> Dict[str, Any]:
        """Basic HTTP tracking for FedEx"""
        return {'success': False, 'error': 'FedEx HTTP tracking not implemented'}
    
    async def track_peninsula_http(self, tracking_number: str) -> Dict[str, Any]:
        """Basic HTTP tracking for Peninsula"""
        return {'success': False, 'error': 'Peninsula HTTP tracking not implemented'}
    
    async def track_rl_http(self, tracking_number: str) -> Dict[str, Any]:
        """Basic HTTP tracking for R&L"""
        return {'success': False, 'error': 'R&L HTTP tracking not implemented'}
    
    def get_recommendation(self, carrier: str) -> str:
        """Get recommendation for failed tracking"""
        recommendations = {
            'estes': 'Visit https://www.estes-express.com/myestes/shipment-tracking/ directly or use browser automation',
            'fedex': 'Visit https://www.fedex.com/fedextrack/ directly or use CloudFlare bypass methods',
            'peninsula': 'Visit https://www.peninsulatruck.com/shipment-tracking/ directly',
            'r&l': 'Visit https://www.rlcarriers.com/tracking directly'
        }
        
        for key, recommendation in recommendations.items():
            if key in carrier.lower():
                return recommendation
        
        return 'Use browser automation or visit carrier website directly'
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of available tracking systems"""
        return {
            'barrier_breaking_available': BARRIER_BREAKING_AVAILABLE,
            'apple_silicon_available': APPLE_SILICON_AVAILABLE,
            'cloud_browser_available': CLOUD_BROWSER_AVAILABLE,
            'is_cloud_environment': self.is_cloud,
            'barrier_breaking_initialized': self.barrier_breaking_system is not None,
            'apple_silicon_initialized': self.apple_silicon_system is not None,
            'cloud_browser_initialized': self.cloud_browser_system is not None
        }

# Async wrapper for compatibility
async def track_shipment_improved(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """
    Main async function for improved cloud tracking
    """
    tracker = ImprovedCloudTracker()
    return await tracker.track_shipment(tracking_number, carrier)

# Synchronous wrapper
def track_shipment_improved_sync(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for improved cloud tracking
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(track_shipment_improved(tracking_number, carrier))
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(track_shipment_improved(tracking_number, carrier))
        finally:
            loop.close() 