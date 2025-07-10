#!/usr/bin/env python3
"""
Cloud Compatible Tracking System
Now uses the improved tracking system that actually works
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from .improved_cloud_tracking import ImprovedCloudTracker, track_shipment_improved

logger = logging.getLogger(__name__)

class CloudCompatibleTracker:
    """
    Cloud-compatible tracking system that uses the improved working methods
    """
    
    def __init__(self):
        self.improved_tracker = ImprovedCloudTracker()
        
    async def track_shipment(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Main tracking method that uses the improved working system
        """
        logger.info(f"🌐 Cloud compatible tracking: {carrier} - {tracking_number}")
        
        try:
            # Use the improved tracker that actually works
            result = await self.improved_tracker.track_shipment(tracking_number, carrier)
            
            # Ensure cloud compatibility flag is set
            result['cloud_compatible'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error in cloud compatible tracking: {e}")
            return {
                'success': False,
                'error': f'Cloud compatible tracking error: {str(e)}',
                'status': 'No status available',
                'location': 'No location available',
                'events': [],
                'carrier': carrier,
                'tracking_number': tracking_number,
                'timestamp': time.time(),
                'cloud_compatible': True
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        status = self.improved_tracker.get_system_status()
        status['cloud_compatible'] = True
        return status
    
    # Legacy compatibility methods
    async def track_estes_cloud(self, tracking_number: str) -> Dict[str, Any]:
        """Legacy compatibility for Estes tracking"""
        return await self.track_shipment(tracking_number, "Estes Express")
    
    async def track_fedex_cloud(self, tracking_number: str) -> Dict[str, Any]:
        """Legacy compatibility for FedEx tracking"""
        return await self.track_shipment(tracking_number, "FedEx Freight")
    
    async def track_peninsula_cloud(self, tracking_number: str) -> Dict[str, Any]:
        """Legacy compatibility for Peninsula tracking"""
        return await self.track_shipment(tracking_number, "Peninsula Truck Lines")
    
    async def track_rl_cloud(self, tracking_number: str) -> Dict[str, Any]:
        """Legacy compatibility for R&L tracking"""
        return await self.track_shipment(tracking_number, "R&L Carriers")

# Main async function for cloud tracking
async def track_cloud_compatible(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """
    Main async function for cloud compatible tracking
    Now uses the improved working system
    """
    tracker = CloudCompatibleTracker()
    return await tracker.track_shipment(tracking_number, carrier)

# Synchronous wrapper
def track_cloud_compatible_sync(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for cloud compatible tracking
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(track_cloud_compatible(tracking_number, carrier))
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(track_cloud_compatible(tracking_number, carrier))
        finally:
            loop.close() 