#!/usr/bin/env python3
"""
Alternative Data Sources for Tracking

This module implements alternative approaches to get tracking data when direct
carrier website access is blocked by anti-bot protections.
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AlternativeDataSources:
    """Alternative data sources for tracking information"""
    
    def __init__(self):
        self.alternative_apis = {
            'fedex': [
                'https://api.trackingmore.com/v3/trackings/fedex',
                'https://api.aftership.com/v4/trackings/fedex',
                'https://api.packagetrackr.com/v1/track/fedex'
            ],
            'estes': [
                'https://api.trackingmore.com/v3/trackings/estes',
                'https://api.packagetrackr.com/v1/track/estes'
            ],
            'peninsula': [
                'https://api.trackingmore.com/v3/trackings/peninsula',
                'https://api.packagetrackr.com/v1/track/peninsula'
            ],
            'rl': [
                'https://api.trackingmore.com/v3/trackings/rl',
                'https://api.packagetrackr.com/v1/track/rl'
            ]
        }
    
    async def get_tracking_via_proxy_services(self, session: aiohttp.ClientSession, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Get tracking data via proxy services"""
        
        # Try web-based proxy services that might have cached data
        proxy_services = [
            f"https://packagetrackr.com/track/{pro_number}",
            f"https://trackingmore.com/track/{carrier}/{pro_number}",
            f"https://17track.net/en/track#{pro_number}",
            f"https://parcelsapp.com/en/tracking/{pro_number}"
        ]
        
        for proxy_url in proxy_services:
            try:
                logger.info(f"🔄 Trying proxy service: {proxy_url}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(proxy_url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse the proxy service response
                        tracking_info = self.parse_proxy_service_response(content, pro_number, carrier)
                        if tracking_info:
                            logger.info(f"✅ Got tracking data from proxy service: {proxy_url}")
                            return tracking_info
                        
            except Exception as e:
                logger.debug(f"❌ Proxy service failed {proxy_url}: {e}")
                continue
        
        return None
    
    def parse_proxy_service_response(self, content: str, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Parse response from proxy tracking services"""
        
        # Look for JSON data in the response
        json_pattern = r'<script[^>]*>.*?({.*?"status".*?}[^<]*)</script>'
        json_matches = re.finditer(json_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in json_matches:
            try:
                json_str = match.group(1)
                data = json.loads(json_str)
                
                if isinstance(data, dict):
                    # Extract tracking information
                    status = data.get('status', data.get('deliveryStatus', 'Unknown'))
                    location = data.get('location', data.get('destination', 'Unknown'))
                    event = data.get('event', data.get('description', 'Tracking information found'))
                    
                    if status != 'Unknown' or location != 'Unknown':
                        return {
                            'status': status,
                            'location': location,
                            'event': event,
                            'timestamp': data.get('timestamp', datetime.now().isoformat())
                        }
            except:
                continue
        
        # Look for structured HTML patterns
        html_patterns = [
            r'<div[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</div>',
            r'<span[^>]*class="[^"]*delivery[^"]*"[^>]*>([^<]*)</span>',
            r'<td[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</td>'
        ]
        
        extracted_data = {}
        for pattern in html_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                text = match.group(1).strip()
                if text and len(text) > 3:  # Filter out empty or very short text
                    if 'status' in pattern.lower():
                        extracted_data['status'] = text
                    elif 'delivery' in pattern.lower():
                        extracted_data['location'] = text
                    elif 'location' in pattern.lower():
                        extracted_data['location'] = text
        
        if extracted_data:
            return {
                'status': extracted_data.get('status', 'Information Found'),
                'location': extracted_data.get('location', 'See details'),
                'event': 'Tracking information retrieved from proxy service',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    async def get_tracking_via_mobile_apis(self, session: aiohttp.ClientSession, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try mobile API endpoints that might be less protected"""
        
        mobile_endpoints = {
            'fedex': [
                'https://www.fedex.com/trackingCal/track',
                'https://mobileapi.fedex.com/track',
                'https://api.fedex.com/track/v1/trackingnumbers'
            ],
            'estes': [
                'https://www.estes-express.com/api/tracking',
                'https://mobile.estes-express.com/api/track'
            ],
            'peninsula': [
                'https://www.peninsulatrucklines.com/api/tracking',
                'https://mobile.peninsulatrucklines.com/track'
            ],
            'rl': [
                'https://www.rlcarriers.com/api/tracking',
                'https://mobile.rlcarriers.com/track'
            ]
        }
        
        endpoints = mobile_endpoints.get(carrier, [])
        
        for endpoint in endpoints:
            try:
                logger.info(f"📱 Trying mobile API: {endpoint}")
                
                # Mobile-specific headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                # Try POST request with JSON payload
                payload = {
                    'trackingNumber': pro_number,
                    'pro': pro_number,
                    'number': pro_number
                }
                
                timeout = aiohttp.ClientTimeout(total=8)
                async with session.post(endpoint, json=payload, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            tracking_info = self.parse_mobile_api_response(data, pro_number)
                            if tracking_info:
                                logger.info(f"✅ Got tracking data from mobile API: {endpoint}")
                                return tracking_info
                        except:
                            pass
                
                # Try GET request
                params = {'pro': pro_number, 'trackingNumber': pro_number}
                async with session.get(endpoint, params=params, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            tracking_info = self.parse_mobile_api_response(data, pro_number)
                            if tracking_info:
                                logger.info(f"✅ Got tracking data from mobile API: {endpoint}")
                                return tracking_info
                        except:
                            pass
                            
            except Exception as e:
                logger.debug(f"❌ Mobile API failed {endpoint}: {e}")
                continue
        
        return None
    
    def parse_mobile_api_response(self, data: Any, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse mobile API response"""
        
        if isinstance(data, dict):
            # Check for direct tracking fields
            if 'trackingStatus' in data or 'status' in data:
                return {
                    'status': data.get('trackingStatus', data.get('status', 'Unknown')),
                    'location': data.get('location', data.get('destination', 'Unknown')),
                    'event': data.get('event', data.get('description', 'Tracking information found')),
                    'timestamp': data.get('timestamp', data.get('lastUpdate', datetime.now().isoformat()))
                }
            
            # Check for nested tracking data
            if 'tracking' in data:
                tracking_data = data['tracking']
                if isinstance(tracking_data, dict):
                    return {
                        'status': tracking_data.get('status', 'Unknown'),
                        'location': tracking_data.get('location', 'Unknown'),
                        'event': tracking_data.get('event', 'Tracking information found'),
                        'timestamp': tracking_data.get('timestamp', datetime.now().isoformat())
                    }
            
            # Check for tracking results array
            if 'results' in data and isinstance(data['results'], list) and data['results']:
                result = data['results'][0]
                if isinstance(result, dict):
                    return {
                        'status': result.get('status', 'Unknown'),
                        'location': result.get('location', 'Unknown'),
                        'event': result.get('event', 'Tracking information found'),
                        'timestamp': result.get('timestamp', datetime.now().isoformat())
                    }
        
        return None
    
    async def get_tracking_via_rss_feeds(self, session: aiohttp.ClientSession, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try RSS feeds or XML endpoints that might have tracking data"""
        
        rss_endpoints = {
            'fedex': [
                'https://www.fedex.com/rss/trackingResult.xml',
                'https://api.fedex.com/track/v1/rss'
            ],
            'estes': [
                'https://www.estes-express.com/rss/tracking.xml'
            ]
        }
        
        endpoints = rss_endpoints.get(carrier, [])
        
        for endpoint in endpoints:
            try:
                logger.info(f"📡 Trying RSS feed: {endpoint}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader)',
                    'Accept': 'application/rss+xml, application/xml, text/xml'
                }
                
                params = {'pro': pro_number, 'trackingNumber': pro_number}
                timeout = aiohttp.ClientTimeout(total=8)
                
                async with session.get(endpoint, params=params, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        tracking_info = self.parse_rss_response(content, pro_number)
                        if tracking_info:
                            logger.info(f"✅ Got tracking data from RSS feed: {endpoint}")
                            return tracking_info
                            
            except Exception as e:
                logger.debug(f"❌ RSS feed failed {endpoint}: {e}")
                continue
        
        return None
    
    def parse_rss_response(self, content: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse RSS/XML response for tracking information"""
        
        # Look for XML tracking elements
        xml_patterns = [
            r'<status[^>]*>([^<]*)</status>',
            r'<location[^>]*>([^<]*)</location>',
            r'<description[^>]*>([^<]*)</description>',
            r'<title[^>]*>([^<]*)</title>'
        ]
        
        extracted_data = {}
        for pattern in xml_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                text = match.group(1).strip()
                if text and len(text) > 3:
                    if 'status' in pattern.lower():
                        extracted_data['status'] = text
                    elif 'location' in pattern.lower():
                        extracted_data['location'] = text
                    elif 'description' in pattern.lower() or 'title' in pattern.lower():
                        extracted_data['event'] = text
        
        if extracted_data:
            return {
                'status': extracted_data.get('status', 'Information Found'),
                'location': extracted_data.get('location', 'See details'),
                'event': extracted_data.get('event', 'Tracking information retrieved from RSS feed'),
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    async def get_tracking_comprehensive(self, session: aiohttp.ClientSession, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Try all alternative data sources comprehensively"""
        
        logger.info(f"🔄 Trying alternative data sources for {carrier} PRO {pro_number}")
        
        # Try methods in order of reliability
        methods = [
            self.get_tracking_via_mobile_apis,
            self.get_tracking_via_proxy_services,
            self.get_tracking_via_rss_feeds
        ]
        
        for method in methods:
            try:
                result = await method(session, pro_number, carrier)
                if result:
                    logger.info(f"✅ Alternative data source successful: {method.__name__}")
                    return result
            except Exception as e:
                logger.debug(f"❌ Alternative method failed {method.__name__}: {e}")
                continue
        
        logger.info(f"❌ All alternative data sources failed for {carrier} PRO {pro_number}")
        return None