"""
Barrier-Breaking Tracking System
Integrates Apple Silicon Estes client and CloudFlare bypass FedEx client
Solves the technical barriers preventing successful tracking
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .apple_silicon_estes_client import AppleSiliconEstesClient, track_estes_sync
from .cloudflare_bypass_fedex_client import CloudFlareBypassFedExClient, track_fedex_sync

# Import legacy system for fallback
ZeroCostCarrierTracking = None
try:
    from .zero_cost_carriers import ZeroCostCarrierTracking
except ImportError:
    pass

logger = logging.getLogger(__name__)

class BarrierBreakingTrackingSystem:
    """
    Main barrier-breaking tracking system that solves technical barriers
    - Apple Silicon CPU architecture barrier for Estes Express
    - CloudFlare protection barrier for FedEx Freight
    """
    
    def __init__(self):
        self.estes_client = AppleSiliconEstesClient()
        self.fedex_client = CloudFlareBypassFedExClient()
        self.legacy_client = ZeroCostCarrierTracking() if ZeroCostCarrierTracking else None
        
        # Carrier detection patterns
        self.carrier_patterns = {
            'estes': ['estes', 'est', 'estes-express'],
            'fedex': ['fedex', 'fdx', 'fedex-freight', 'fedexfreight'],
            'peninsula': ['peninsula', 'pen', 'peninsula-trucking'],
            'rl': ['rl', 'r&l', 'rl-carriers', 'r&l-carriers']
        }
    
    def detect_carrier(self, tracking_number: str) -> str:
        """Detect carrier from tracking number format"""
        tracking_number = tracking_number.upper().strip()
        
        # Estes Express patterns
        if (len(tracking_number) == 10 and tracking_number.isdigit()) or \
           (len(tracking_number) == 11 and tracking_number.startswith('0')):
            return 'estes'
        
        # FedEx patterns
        if len(tracking_number) == 12 and tracking_number.isdigit():
            return 'fedex'
        elif len(tracking_number) == 14 and tracking_number.isdigit():
            return 'fedex'
        elif tracking_number.startswith(('1001', '1002', '1003', '1004', '1005')):
            return 'fedex'
        
        # Peninsula patterns
        if len(tracking_number) == 8 and tracking_number.isdigit():
            return 'peninsula'
        elif tracking_number.startswith(('PEN', 'P')):
            return 'peninsula'
        
        # R&L patterns
        if len(tracking_number) == 9 and tracking_number.isdigit():
            return 'rl'
        elif tracking_number.startswith(('RL', 'R')):
            return 'rl'
        
        # Default to unknown
        return 'unknown'
    
    async def track_estes_with_barriers_solved(self, tracking_number: str) -> Dict:
        """Track Estes Express with Apple Silicon barriers solved"""
        try:
            logger.info(f"🔧 Solving Apple Silicon barriers for Estes: {tracking_number}")
            result = await self.estes_client.track_shipment(tracking_number)
            
            if result.get('success'):
                logger.info("✅ Apple Silicon barrier breakthrough successful for Estes")
                result['method'] = 'Apple Silicon Breakthrough'
                result['barrier_solved'] = 'ARM64 CPU Architecture'
                return result
            else:
                logger.warning(f"❌ Apple Silicon barrier breakthrough failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"Apple Silicon Estes tracking error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tracking_number': tracking_number,
                'carrier': 'Estes Express'
            }
    
    async def track_fedex_with_barriers_solved(self, tracking_number: str) -> Dict:
        """Track FedEx Freight with CloudFlare barriers solved"""
        try:
            logger.info(f"🔧 Solving CloudFlare barriers for FedEx: {tracking_number}")
            result = await self.fedex_client.track_shipment(tracking_number)
            
            if result.get('success'):
                logger.info("✅ CloudFlare barrier breakthrough successful for FedEx")
                result['method'] = 'CloudFlare Breakthrough'
                result['barrier_solved'] = 'CloudFlare Protection + TLS Fingerprinting'
                return result
            else:
                logger.warning(f"❌ CloudFlare barrier breakthrough failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"CloudFlare FedEx tracking error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tracking_number': tracking_number,
                'carrier': 'FedEx Freight'
            }
    
    def track_with_legacy_fallback(self, tracking_number: str, carrier: str) -> Dict:
        """Track using legacy system as fallback"""
        try:
            if self.legacy_client:
                logger.info(f"🔄 Using legacy fallback for {carrier}: {tracking_number}")
                result = self.legacy_client.track_shipment(tracking_number)
                
                if result.get('success'):
                    result['method'] = 'Legacy Fallback'
                    logger.info("✅ Legacy fallback successful")
                    return result
                else:
                    logger.warning(f"❌ Legacy fallback failed: {result.get('error')}")
                    return result
            else:
                return {
                    'success': False,
                    'error': 'Legacy system not available',
                    'tracking_number': tracking_number,
                    'carrier': carrier
                }
                
        except Exception as e:
            logger.error(f"Legacy fallback error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tracking_number': tracking_number,
                'carrier': carrier
            }
    
    async def track_single_shipment(self, tracking_number: str) -> Dict:
        """Track a single shipment with barrier-breaking capabilities"""
        start_time = time.time()
        
        # Detect carrier
        carrier = self.detect_carrier(tracking_number)
        logger.info(f"📦 Tracking {tracking_number} - Detected carrier: {carrier}")
        
        # Route to appropriate barrier-breaking method
        if carrier == 'estes':
            result = await self.track_estes_with_barriers_solved(tracking_number)
        elif carrier == 'fedex':
            result = await self.track_fedex_with_barriers_solved(tracking_number)
        elif carrier in ['peninsula', 'rl']:
            # These carriers don't have the same barriers, use legacy or direct methods
            result = self.track_with_legacy_fallback(tracking_number, carrier)
        else:
            # Unknown carrier, try all methods
            logger.info(f"🔍 Unknown carrier, trying all barrier-breaking methods...")
            
            # Try Estes first
            result = await self.track_estes_with_barriers_solved(tracking_number)
            if not result.get('success'):
                # Try FedEx
                result = await self.track_fedex_with_barriers_solved(tracking_number)
                if not result.get('success'):
                    # Try legacy
                    result = self.track_with_legacy_fallback(tracking_number, 'unknown')
        
        # If primary method failed, try fallback
        if not result.get('success') and carrier in ['estes', 'fedex']:
            logger.info(f"🔄 Primary method failed, trying legacy fallback...")
            fallback_result = self.track_with_legacy_fallback(tracking_number, carrier)
            if fallback_result.get('success'):
                result = fallback_result
        
        # Add timing information
        elapsed_time = time.time() - start_time
        result['elapsed_time'] = elapsed_time
        result['timestamp'] = time.time()
        
        return result
    
    async def track_multiple_shipments(self, tracking_numbers: List[str]) -> Dict:
        """Track multiple shipments with barrier-breaking capabilities"""
        logger.info(f"📦 Starting barrier-breaking tracking for {len(tracking_numbers)} shipments")
        
        start_time = time.time()
        results = []
        
        # Track all shipments concurrently
        tasks = []
        for tracking_number in tracking_numbers:
            task = asyncio.create_task(self.track_single_shipment(tracking_number))
            tasks.append(task)
        
        # Wait for all tasks to complete
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_tracks = 0
        failed_tracks = 0
        barriers_solved = []
        
        for i, result in enumerate(completed_results):
            if isinstance(result, Exception):
                result = {
                    'success': False,
                    'error': str(result),
                    'tracking_number': tracking_numbers[i],
                    'carrier': 'unknown'
                }
            
            results.append(result)
            
            if isinstance(result, dict) and result.get('success'):
                successful_tracks += 1
                if result.get('barrier_solved'):
                    barriers_solved.append(result['barrier_solved'])
            else:
                failed_tracks += 1
        
        # Calculate success rate
        total_tracks = len(tracking_numbers)
        success_rate = (successful_tracks / total_tracks) * 100 if total_tracks > 0 else 0
        
        elapsed_time = time.time() - start_time
        
        summary = {
            'total_shipments': total_tracks,
            'successful_tracks': successful_tracks,
            'failed_tracks': failed_tracks,
            'success_rate': success_rate,
            'barriers_solved': list(set(barriers_solved)),
            'elapsed_time': elapsed_time,
            'timestamp': time.time(),
            'results': results
        }
        
        logger.info(f"🎯 Barrier-breaking tracking complete: {success_rate:.1f}% success rate")
        logger.info(f"💪 Barriers solved: {', '.join(barriers_solved) if barriers_solved else 'None'}")
        
        return summary
    
    def track_shipments_sync(self, tracking_numbers: List[str]) -> Dict:
        """Synchronous wrapper for tracking multiple shipments"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.track_multiple_shipments(tracking_numbers))
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.track_multiple_shipments(tracking_numbers))
            finally:
                loop.close()
    
    def get_system_status(self) -> Dict:
        """Get the status of the barrier-breaking system"""
        return {
            'system_name': 'Barrier-Breaking Tracking System',
            'version': '1.0.0',
            'capabilities': {
                'apple_silicon_estes': True,
                'cloudflare_bypass_fedex': True,
                'legacy_fallback': self.legacy_client is not None,
                'concurrent_tracking': True
            },
            'barriers_solved': [
                'Apple Silicon ARM64 CPU Architecture (Estes Express)',
                'CloudFlare Protection + TLS Fingerprinting (FedEx Freight)',
                'Browser Detection and Anti-Scraping (All Carriers)',
                'JavaScript Challenge Solving (CloudFlare)',
                'Mobile API Endpoint Discovery (All Carriers)'
            ],
            'supported_carriers': ['Estes Express', 'FedEx Freight', 'Peninsula Trucking', 'R&L Carriers'],
            'success_rate_targets': {
                'estes_express': '75-85%',
                'fedex_freight': '60-75%',
                'peninsula_trucking': '90-95%',
                'rl_carriers': '90-95%'
            }
        }

# Convenience functions for direct usage
async def track_with_barriers_solved(tracking_numbers: List[str]) -> Dict:
    """Track shipments with all barriers solved"""
    system = BarrierBreakingTrackingSystem()
    return await system.track_multiple_shipments(tracking_numbers)

def track_sync_with_barriers_solved(tracking_numbers: List[str]) -> Dict:
    """Synchronous wrapper for barrier-breaking tracking"""
    system = BarrierBreakingTrackingSystem()
    return system.track_shipments_sync(tracking_numbers)

# Individual carrier functions
def track_estes_barrier_solved(tracking_number: str) -> Dict:
    """Track Estes Express with Apple Silicon barriers solved"""
    return track_estes_sync(tracking_number)

def track_fedex_barrier_solved(tracking_number: str) -> Dict:
    """Track FedEx Freight with CloudFlare barriers solved"""
    return track_fedex_sync(tracking_number) 