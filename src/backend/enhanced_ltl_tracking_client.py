#!/usr/bin/env python3
"""
Enhanced LTL Tracking Client with Zero-Cost Anti-Scraping

Integrates zero-cost anti-scraping system with existing LTL tracking infrastructure.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Graceful imports for production compatibility
try:
    from .zero_cost_anti_scraping import ZeroCostAntiScrapingSystem
    from .zero_cost_carriers import ZeroCostCarrierManager
    ZERO_COST_AVAILABLE = True
except ImportError as e:
    print(f"Zero-cost modules not available: {e}")
    ZERO_COST_AVAILABLE = False
    ZeroCostAntiScrapingSystem = None
    ZeroCostCarrierManager = None

from .ltl_tracking_client import LTLTrackingClient
from .carrier_detection import CarrierDetector


class EnhancedLTLTrackingClient:
    """Enhanced LTL tracking client with zero-cost anti-scraping capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        if ZERO_COST_AVAILABLE and ZeroCostCarrierManager:
            self.zero_cost_manager = ZeroCostCarrierManager()
            self.use_zero_cost_first = True
            self.logger.info("Enhanced LTL Tracking Client initialized with zero-cost anti-scraping")
        else:
            self.zero_cost_manager = None
            self.use_zero_cost_first = False
            self.logger.warning("Zero-cost modules not available - using legacy tracking only")
        
        self.legacy_client = LTLTrackingClient()
        self.carrier_detector = CarrierDetector()
        
        # Configuration
        self.fallback_to_legacy = True
    
    async def track_shipment(self, pro_number: str, carrier: Optional[str] = None) -> Dict[str, Any]:
        """
        Track shipment using zero-cost methods first, fallback to legacy if needed
        
        Args:
            pro_number: PRO number to track
            carrier: Optional carrier name (will be detected if not provided)
            
        Returns:
            Dictionary containing tracking results
        """
        try:
            # Detect carrier if not provided
            if not carrier:
                detected_carrier_info = self.carrier_detector.detect_carrier(pro_number)
                if not detected_carrier_info:
                    return {
                        'status': 'error',
                        'message': 'Unable to detect carrier from PRO number',
                        'pro_number': pro_number
                    }
                carrier = detected_carrier_info.get('name', 'Unknown')
            
            # Ensure carrier is a string
            if not isinstance(carrier, str):
                carrier = 'Unknown'
            
            self.logger.info(f"Tracking {pro_number} with carrier: {carrier}")
            
            # Try zero-cost method first
            if self.use_zero_cost_first and self.zero_cost_manager:
                result = await self._try_zero_cost_tracking(carrier, pro_number)
                if result and result.get('status') == 'success':
                    self.logger.info(f"Zero-cost tracking successful for {pro_number}")
                    return result
                else:
                    self.logger.info(f"Zero-cost tracking failed for {pro_number}: {result.get('message', 'Unknown error')}")
            
            # Fallback to legacy method
            if self.fallback_to_legacy:
                self.logger.info(f"Falling back to legacy tracking for {pro_number}")
                result = await self._try_legacy_tracking(carrier, pro_number)
                if result and result.get('status') == 'success':
                    self.logger.info(f"Legacy tracking successful for {pro_number}")
                    return result
            
            # If both methods fail
            return {
                'status': 'error',
                'message': 'Both zero-cost and legacy tracking methods failed',
                'pro_number': pro_number,
                'carrier': carrier
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced tracking failed for {pro_number}: {e}")
            return {
                'status': 'error',
                'message': f'Enhanced tracking error: {str(e)}',
                'pro_number': pro_number,
                'carrier': carrier or 'Unknown'
            }
    
    async def _try_zero_cost_tracking(self, carrier: str, pro_number: str) -> Dict[str, Any]:
        """Try zero-cost tracking method"""
        try:
            # Check if zero-cost manager is available
            if not self.zero_cost_manager:
                return {
                    'status': 'error',
                    'message': 'Zero-cost tracking not available in this environment',
                    'pro_number': pro_number
                }
            
            # Check if carrier is supported by zero-cost system
            supported_carriers = ['peninsula', 'fedex', 'estes']
            carrier_lower = carrier.lower()
            
            if not any(supported in carrier_lower for supported in supported_carriers):
                return {
                    'status': 'error',
                    'message': f'Zero-cost tracking not supported for carrier: {carrier}',
                    'pro_number': pro_number
                }
            
            # Use zero-cost tracking
            result = await self.zero_cost_manager.track_shipment(carrier, pro_number)
            
            # Enhance result with metadata
            if result.get('status') == 'success':
                result['tracking_method'] = 'zero_cost_anti_scraping'
                result['timestamp'] = datetime.now().isoformat()
                result['enhanced_client'] = True
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Zero-cost tracking attempt failed: {e}")
            return {
                'status': 'error',
                'message': f'Zero-cost tracking error: {str(e)}',
                'pro_number': pro_number
            }
    
    async def _try_legacy_tracking(self, carrier: str, pro_number: str) -> Dict[str, Any]:
        """Try legacy tracking method"""
        try:
            # Use legacy tracking client
            tracking_result = await asyncio.get_event_loop().run_in_executor(
                None, self.legacy_client.track_pro_number, pro_number
            )
            
            # Convert TrackingResult to dictionary
            if hasattr(tracking_result, 'scrape_success') and tracking_result.scrape_success:
                result = {
                    'status': 'success',
                    'pro_number': tracking_result.pro_number,
                    'carrier': tracking_result.carrier_name,
                    'tracking_status': tracking_result.tracking_status,
                    'tracking_location': tracking_result.tracking_location,
                    'tracking_event': tracking_result.tracking_event,
                    'tracking_timestamp': tracking_result.tracking_timestamp,
                    'tracking_method': 'legacy_client',
                    'timestamp': datetime.now().isoformat(),
                    'enhanced_client': True
                }
            else:
                result = {
                    'status': 'error',
                    'message': tracking_result.error_message or 'Legacy tracking failed',
                    'pro_number': tracking_result.pro_number,
                    'carrier': tracking_result.carrier_name,
                    'tracking_method': 'legacy_client',
                    'timestamp': datetime.now().isoformat(),
                    'enhanced_client': True
                }
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Legacy tracking attempt failed: {e}")
            return {
                'status': 'error',
                'message': f'Legacy tracking error: {str(e)}',
                'pro_number': pro_number
            }
    
    async def batch_track_shipments(self, shipments: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Track multiple shipments concurrently
        
        Args:
            shipments: List of dictionaries with 'pro_number' and optional 'carrier'
            
        Returns:
            List of tracking results
        """
        try:
            self.logger.info(f"Starting batch tracking for {len(shipments)} shipments")
            
            # Create tracking tasks
            tasks = []
            for shipment in shipments:
                pro_number = shipment.get('pro_number')
                carrier = shipment.get('carrier')
                
                if pro_number:
                    task = self.track_shipment(pro_number, carrier)
                    tasks.append(task)
                else:
                    tasks.append(asyncio.coroutine(lambda: {
                        'status': 'error',
                        'message': 'Missing PRO number',
                        'pro_number': None
                    })())
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'status': 'error',
                        'message': f'Batch tracking error: {str(result)}',
                        'pro_number': shipments[i].get('pro_number'),
                        'carrier': shipments[i].get('carrier')
                    })
                else:
                    processed_results.append(result)
            
            self.logger.info(f"Batch tracking completed: {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch tracking failed: {e}")
            return [{
                'status': 'error',
                'message': f'Batch tracking error: {str(e)}',
                'pro_number': None,
                'carrier': None
            }]
    
    def get_supported_carriers(self) -> List[str]:
        """Get list of supported carriers"""
        return [
            'Peninsula Truck Lines',
            'FedEx Freight',
            'Estes Express Lines',
            'R+L Carriers',  # From legacy system
            'Old Dominion',  # From legacy system
            'YRC Freight',   # From legacy system
            'XPO Logistics', # From legacy system
            'Saia',          # From legacy system
            'ABF Freight'    # From legacy system
        ]
    
    def get_zero_cost_carriers(self) -> List[str]:
        """Get list of carriers supported by zero-cost system"""
        return [
            'Peninsula Truck Lines',
            'FedEx Freight',
            'Estes Express Lines'
        ]
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """Get tracking statistics and system status"""
        try:
            return {
                'zero_cost_system': {
                    'enabled': self.use_zero_cost_first,
                    'supported_carriers': self.get_zero_cost_carriers(),
                    'features': [
                        'TOR IP rotation',
                        'Local CAPTCHA solving',
                        'JavaScript rendering',
                        'Browser fingerprinting',
                        'Session warming',
                        'Human behavior simulation'
                    ]
                },
                'legacy_system': {
                    'enabled': self.fallback_to_legacy,
                    'supported_carriers': self.get_supported_carriers()
                },
                'configuration': {
                    'zero_cost_first': self.use_zero_cost_first,
                    'fallback_enabled': self.fallback_to_legacy
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get tracking statistics: {e}")
            return {
                'error': f'Statistics error: {str(e)}'
            }
    
    async def test_zero_cost_system(self) -> Dict[str, Any]:
        """Test zero-cost system functionality"""
        try:
            self.logger.info("Testing zero-cost system functionality")
            
            # Check if zero-cost manager is available
            if not self.zero_cost_manager:
                return {
                    'status': 'error',
                    'message': 'Zero-cost system not available in this environment',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Test each carrier
            test_results = {}
            test_pros = {
                'peninsula': '536246546',  # User's test PRO
                'fedex': '1234567890',     # Test PRO
                'estes': '0987654321'      # Test PRO
            }
            
            for carrier, pro in test_pros.items():
                try:
                    result = await self.zero_cost_manager.track_shipment(carrier, pro)
                    test_results[carrier] = {
                        'status': result.get('status'),
                        'message': result.get('message', 'No message'),
                        'pro_number': pro
                    }
                except Exception as e:
                    test_results[carrier] = {
                        'status': 'error',
                        'message': f'Test failed: {str(e)}',
                        'pro_number': pro
                    }
            
            return {
                'status': 'completed',
                'test_results': test_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Zero-cost system test failed: {e}")
            return {
                'status': 'error',
                'message': f'Test error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def configure_system(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure enhanced tracking system"""
        try:
            # Update configuration
            if 'use_zero_cost_first' in config:
                self.use_zero_cost_first = bool(config['use_zero_cost_first'])
            
            if 'fallback_to_legacy' in config:
                self.fallback_to_legacy = bool(config['fallback_to_legacy'])
            
            self.logger.info(f"System configured: zero_cost_first={self.use_zero_cost_first}, fallback={self.fallback_to_legacy}")
            
            return {
                'status': 'success',
                'message': 'System configured successfully',
                'configuration': {
                    'use_zero_cost_first': self.use_zero_cost_first,
                    'fallback_to_legacy': self.fallback_to_legacy
                }
            }
            
        except Exception as e:
            self.logger.error(f"System configuration failed: {e}")
            return {
                'status': 'error',
                'message': f'Configuration error: {str(e)}'
            }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.zero_cost_manager:
                self.zero_cost_manager.cleanup()
            self.logger.info("Enhanced LTL Tracking Client cleaned up")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass


# Convenience function for backward compatibility
async def track_shipment_enhanced(pro_number: str, carrier: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for enhanced tracking
    
    Args:
        pro_number: PRO number to track
        carrier: Optional carrier name
        
    Returns:
        Dictionary containing tracking results
    """
    client = EnhancedLTLTrackingClient()
    try:
        result = await client.track_shipment(pro_number, carrier)
        return result
    finally:
        client.cleanup()


# Convenience function for batch tracking
async def batch_track_shipments_enhanced(shipments: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convenience function for enhanced batch tracking
    
    Args:
        shipments: List of dictionaries with 'pro_number' and optional 'carrier'
        
    Returns:
        List of tracking results
    """
    client = EnhancedLTLTrackingClient()
    try:
        results = await client.batch_track_shipments(shipments)
        return results
    finally:
        client.cleanup() 