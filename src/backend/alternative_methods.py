#!/usr/bin/env python3
"""
Alternative Methods System for LTL Tracking
Implements proxy rotation, API discovery, and third-party integrations to bypass blocking mechanisms
"""

import asyncio
import aiohttp
import random
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse, parse_qs
import base64
import hashlib

logger = logging.getLogger(__name__)


class AlternativeMethodType(Enum):
    """Types of alternative methods"""
    PROXY_ROTATION = "proxy_rotation"
    API_DISCOVERY = "api_discovery"
    THIRD_PARTY_AGGREGATOR = "third_party_aggregator"
    MOBILE_ENDPOINT = "mobile_endpoint"
    GUEST_FORM = "guest_form"
    LEGACY_ENDPOINT = "legacy_endpoint"
    HEADER_SPOOFING = "header_spoofing"
    REQUEST_TIMING = "request_timing"


@dataclass
class AlternativeMethodResult:
    """Result of alternative method attempt"""
    method_type: AlternativeMethodType
    success: bool
    response_time: float
    tracking_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    method_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ProxyProvider:
    """Base class for proxy providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.proxies: List[Dict[str, str]] = []
        self.current_index = 0
        self.last_rotation = datetime.now()
    
    async def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy in rotation"""
        if not self.proxies:
            await self.refresh_proxies()
        
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return proxy
    
    async def refresh_proxies(self):
        """Refresh proxy list - implemented by subclasses"""
        pass
    
    async def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """Validate proxy connectivity"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    'https://httpbin.org/ip',
                    proxy=proxy.get('url'),
                    timeout=timeout
                ) as response:
                    return response.status == 200
        except Exception:
            return False


class FreeProxyProvider(ProxyProvider):
    """Free proxy provider using public proxy lists"""
    
    def __init__(self):
        super().__init__("FreeProxy")
        self.proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=US&ssl=all&anonymity=all',
            'https://www.proxy-list.download/api/v1/get?type=http&anon=elite&country=US',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
        ]
    
    async def refresh_proxies(self):
        """Fetch proxies from public sources"""
        new_proxies = []
        
        for source in self.proxy_sources:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(source, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            content = await response.text()
                            proxies = self._parse_proxy_list(content)
                            new_proxies.extend(proxies)
            except Exception as e:
                logger.warning(f"Failed to fetch proxies from {source}: {e}")
        
        # Validate a subset of proxies
        if new_proxies:
            sample_proxies = random.sample(new_proxies, min(10, len(new_proxies)))
            validated_proxies = []
            
            for proxy in sample_proxies:
                if await self.validate_proxy(proxy):
                    validated_proxies.append(proxy)
            
            self.proxies = validated_proxies
            logger.info(f"Refreshed {len(self.proxies)} validated free proxies")
    
    def _parse_proxy_list(self, content: str) -> List[Dict[str, str]]:
        """Parse proxy list from various formats"""
        proxies = []
        
        # Common formats: IP:PORT, protocol://IP:PORT
        patterns = [
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})',
            r'https?://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                ip, port = match
                proxies.append({
                    'url': f'http://{ip}:{port}',
                    'ip': ip,
                    'port': port
                })
        
        return proxies


class ResidentialProxyProvider(ProxyProvider):
    """Residential proxy provider (requires API key)"""
    
    def __init__(self, api_key: str = None):
        super().__init__("ResidentialProxy")
        self.api_key = api_key
        self.endpoint = "http://rotating-residential.proxymesh.com:31280"
    
    async def refresh_proxies(self):
        """Use rotating residential proxy endpoint"""
        if not self.api_key:
            logger.warning("No API key provided for residential proxy")
            return
        
        # Residential proxies typically use a single rotating endpoint
        self.proxies = [{
            'url': self.endpoint,
            'auth': aiohttp.BasicAuth('username', self.api_key)
        }]


class APIDiscoveryEngine:
    """Engine for discovering undocumented APIs"""
    
    def __init__(self):
        self.discovered_apis = {}
        self.common_api_patterns = [
            '/api/v1/track',
            '/api/v2/track',
            '/api/track',
            '/api/shipment/track',
            '/api/tracking',
            '/track/api',
            '/services/track',
            '/rest/track',
            '/graphql',
            '/wp-json/wp/v2',
            '/ajax/track',
            '/mobile/api/track',
            '/m/api/track'
        ]
        
        self.api_methods = ['GET', 'POST', 'PUT']
        self.payload_templates = {
            'json': {
                'pro_number': '{pro_number}',
                'tracking_number': '{pro_number}',
                'shipment_id': '{pro_number}',
                'reference': '{pro_number}'
            },
            'form': {
                'pro': '{pro_number}',
                'tracking': '{pro_number}',
                'shipment': '{pro_number}',
                'reference': '{pro_number}'
            }
        }
    
    async def discover_apis(self, base_url: str, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Discover APIs for a given base URL"""
        discovered = []
        
        for pattern in self.common_api_patterns:
            api_url = urljoin(base_url, pattern)
            
            for method in self.api_methods:
                try:
                    # Test with dummy data
                    test_result = await self._test_api_endpoint(
                        api_url, method, session, 'TEST12345'
                    )
                    
                    if test_result['potentially_valid']:
                        discovered.append({
                            'url': api_url,
                            'method': method,
                            'response_info': test_result
                        })
                
                except Exception as e:
                    logger.debug(f"API discovery error for {api_url}: {e}")
                
                # Rate limiting
                await asyncio.sleep(0.2)
        
        return discovered
    
    async def _test_api_endpoint(self, url: str, method: str, session: aiohttp.ClientSession, 
                               test_pro: str) -> Dict[str, Any]:
        """Test an API endpoint with dummy data"""
        result = {
            'potentially_valid': False,
            'status_code': None,
            'response_size': 0,
            'content_type': None,
            'indicators': []
        }
        
        try:
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            data = None
            if method == 'POST':
                data = json.dumps({'pro_number': test_pro, 'tracking_number': test_pro})
            
            async with session.request(
                method, url, headers=headers, data=data, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result['status_code'] = response.status
                result['content_type'] = response.headers.get('content-type', '')
                
                content = await response.text()
                result['response_size'] = len(content)
                
                # Check for API indicators
                if response.status in [200, 201, 400, 401, 403, 422]:
                    result['potentially_valid'] = True
                    result['indicators'].append('valid_status_code')
                
                if 'application/json' in result['content_type']:
                    result['indicators'].append('json_response')
                
                # Check for tracking-related content
                tracking_indicators = [
                    'tracking', 'shipment', 'status', 'location', 'delivery',
                    'error', 'message', 'invalid', 'not found'
                ]
                
                content_lower = content.lower()
                for indicator in tracking_indicators:
                    if indicator in content_lower:
                        result['indicators'].append(f'contains_{indicator}')
                
                # Check for structured data
                try:
                    json.loads(content)
                    result['indicators'].append('valid_json')
                except:
                    pass
        
        except Exception as e:
            result['error'] = str(e)
        
        return result


class ThirdPartyAggregator:
    """Third-party tracking aggregator integration"""
    
    def __init__(self):
        self.aggregators = {
            'trackingmore': {
                'url': 'https://api.trackingmore.com/v3/trackings',
                'headers': {'Tracking-Api-Key': 'YOUR_API_KEY'},
                'method': 'POST',
                'payload_template': {
                    'tracking_number': '{pro_number}',
                    'carrier_code': '{carrier_code}'
                }
            },
            '17track': {
                'url': 'https://api.17track.net/track/v2.2/register',
                'headers': {'17token': 'YOUR_TOKEN'},
                'method': 'POST',
                'payload_template': [{
                    'number': '{pro_number}',
                    'carrier': '{carrier_code}'
                }]
            },
            'aftership': {
                'url': 'https://api.aftership.com/v4/trackings',
                'headers': {'aftership-api-key': 'YOUR_API_KEY'},
                'method': 'POST',
                'payload_template': {
                    'tracking': {
                        'tracking_number': '{pro_number}',
                        'slug': '{carrier_code}'
                    }
                }
            }
        }
        
        self.carrier_mappings = {
            'fedex': 'fedex',
            'estes': 'estes',
            'peninsula': 'peninsula',
            'rl': 'rl-carriers'
        }
    
    async def track_via_aggregator(self, aggregator_name: str, pro_number: str, 
                                 carrier: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Track via third-party aggregator"""
        if aggregator_name not in self.aggregators:
            return {'success': False, 'error': f'Unknown aggregator: {aggregator_name}'}
        
        config = self.aggregators[aggregator_name]
        carrier_code = self.carrier_mappings.get(carrier, carrier)
        
        # Prepare payload
        payload = config['payload_template']
        payload_str = json.dumps(payload)
        payload_str = payload_str.replace('{pro_number}', pro_number)
        payload_str = payload_str.replace('{carrier_code}', carrier_code)
        payload = json.loads(payload_str)
        
        try:
            async with session.request(
                config['method'],
                config['url'],
                headers=config['headers'],
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                result = await response.json()
                
                return {
                    'success': response.status == 200,
                    'status_code': response.status,
                    'data': result,
                    'aggregator': aggregator_name
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'aggregator': aggregator_name
            }


class AlternativeMethodsEngine:
    """Main engine for alternative tracking methods"""
    
    def __init__(self):
        self.proxy_providers = [
            FreeProxyProvider(),
            # ResidentialProxyProvider()  # Requires API key
        ]
        self.api_discovery = APIDiscoveryEngine()
        self.aggregator = ThirdPartyAggregator()
        self.session = None
        
        # Request timing patterns
        self.timing_patterns = {
            'human_like': [2, 3, 5, 4, 6, 3, 7, 2, 4, 5],
            'conservative': [10, 15, 20, 12, 18, 25, 14, 16, 22, 13],
            'aggressive': [0.5, 1, 1.5, 0.8, 1.2, 0.6, 1.8, 0.9, 1.3, 0.7]
        }
        
        # Mobile user agents
        self.mobile_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
        ]
        
        # Legitimate headers
        self.legitimate_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=3,
            enable_cleanup_closed=True,
            use_dns_cache=False  # Disable DNS cache for proxy rotation
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.legitimate_headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def track_with_alternatives(self, pro_number: str, carrier: str, 
                                    base_url: str) -> List[AlternativeMethodResult]:
        """Try multiple alternative methods for tracking"""
        results = []
        
        # Method 1: Proxy rotation
        proxy_result = await self._try_proxy_rotation(pro_number, carrier, base_url)
        results.append(proxy_result)
        
        # Method 2: API discovery
        api_result = await self._try_api_discovery(pro_number, carrier, base_url)
        results.append(api_result)
        
        # Method 3: Mobile endpoints
        mobile_result = await self._try_mobile_endpoints(pro_number, carrier, base_url)
        results.append(mobile_result)
        
        # Method 4: Header spoofing
        header_result = await self._try_header_spoofing(pro_number, carrier, base_url)
        results.append(header_result)
        
        # Method 5: Third-party aggregators
        aggregator_result = await self._try_aggregators(pro_number, carrier)
        results.append(aggregator_result)
        
        # Method 6: Intelligent timing
        timing_result = await self._try_intelligent_timing(pro_number, carrier, base_url)
        results.append(timing_result)
        
        return results
    
    async def _try_proxy_rotation(self, pro_number: str, carrier: str, base_url: str) -> AlternativeMethodResult:
        """Try tracking with proxy rotation"""
        start_time = time.time()
        
        try:
            # Get proxy
            proxy_provider = self.proxy_providers[0]  # Use first available
            proxy = await proxy_provider.get_next_proxy()
            
            if not proxy:
                return AlternativeMethodResult(
                    method_type=AlternativeMethodType.PROXY_ROTATION,
                    success=False,
                    response_time=time.time() - start_time,
                    error_message="No proxies available"
                )
            
            # Make request through proxy
            async with self.session.get(
                base_url,
                proxy=proxy.get('url'),
                headers={'User-Agent': random.choice(self.mobile_user_agents)}
            ) as response:
                content = await response.text()
                
                # Analyze response
                from .content_analysis import analyze_carrier_response
                analysis = analyze_carrier_response(content, dict(response.headers), carrier, pro_number)
                
                return AlternativeMethodResult(
                    method_type=AlternativeMethodType.PROXY_ROTATION,
                    success=not analysis.is_blocked,
                    response_time=time.time() - start_time,
                    status_code=response.status,
                    tracking_data=analysis.tracking_data,
                    method_details={
                        'proxy': proxy,
                        'blocking_mechanism': analysis.blocking_mechanism.value,
                        'confidence': analysis.confidence_score
                    }
                )
        
        except Exception as e:
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.PROXY_ROTATION,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _try_api_discovery(self, pro_number: str, carrier: str, base_url: str) -> AlternativeMethodResult:
        """Try API discovery"""
        start_time = time.time()
        
        try:
            # Discover APIs
            discovered_apis = await self.api_discovery.discover_apis(base_url, self.session)
            
            if not discovered_apis:
                return AlternativeMethodResult(
                    method_type=AlternativeMethodType.API_DISCOVERY,
                    success=False,
                    response_time=time.time() - start_time,
                    error_message="No APIs discovered"
                )
            
            # Try the most promising API
            best_api = max(discovered_apis, key=lambda x: len(x['response_info']['indicators']))
            
            # Test with real PRO number
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            data = json.dumps({'pro_number': pro_number, 'tracking_number': pro_number})
            
            async with self.session.request(
                best_api['method'],
                best_api['url'],
                headers=headers,
                data=data if best_api['method'] == 'POST' else None
            ) as response:
                content = await response.text()
                
                # Try to parse as JSON
                tracking_data = None
                try:
                    json_data = json.loads(content)
                    tracking_data = json_data
                except:
                    pass
                
                return AlternativeMethodResult(
                    method_type=AlternativeMethodType.API_DISCOVERY,
                    success=response.status == 200 and tracking_data is not None,
                    response_time=time.time() - start_time,
                    status_code=response.status,
                    tracking_data=tracking_data,
                    method_details={
                        'api_url': best_api['url'],
                        'method': best_api['method'],
                        'discovered_apis': len(discovered_apis)
                    }
                )
        
        except Exception as e:
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.API_DISCOVERY,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _try_mobile_endpoints(self, pro_number: str, carrier: str, base_url: str) -> AlternativeMethodResult:
        """Try mobile-specific endpoints"""
        start_time = time.time()
        
        try:
            # Generate mobile URLs
            parsed_url = urlparse(base_url)
            mobile_urls = [
                f"https://m.{parsed_url.netloc}",
                f"https://mobile.{parsed_url.netlify}",
                f"{parsed_url.scheme}://{parsed_url.netloc}/m/",
                f"{parsed_url.scheme}://{parsed_url.netloc}/mobile/"
            ]
            
            # Try each mobile URL
            for mobile_url in mobile_urls:
                try:
                    async with self.session.get(
                        mobile_url,
                        headers={'User-Agent': random.choice(self.mobile_user_agents)}
                    ) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Analyze response
                            from .content_analysis import analyze_carrier_response
                            analysis = analyze_carrier_response(content, dict(response.headers), carrier, pro_number)
                            
                            if not analysis.is_blocked:
                                return AlternativeMethodResult(
                                    method_type=AlternativeMethodType.MOBILE_ENDPOINT,
                                    success=True,
                                    response_time=time.time() - start_time,
                                    status_code=response.status,
                                    tracking_data=analysis.tracking_data,
                                    method_details={
                                        'mobile_url': mobile_url,
                                        'blocking_mechanism': analysis.blocking_mechanism.value
                                    }
                                )
                except Exception:
                    continue
            
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.MOBILE_ENDPOINT,
                success=False,
                response_time=time.time() - start_time,
                error_message="No mobile endpoints accessible"
            )
        
        except Exception as e:
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.MOBILE_ENDPOINT,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _try_header_spoofing(self, pro_number: str, carrier: str, base_url: str) -> AlternativeMethodResult:
        """Try sophisticated header spoofing"""
        start_time = time.time()
        
        try:
            # Generate sophisticated headers
            headers = self.legitimate_headers.copy()
            headers.update({
                'User-Agent': random.choice(self.mobile_user_agents),
                'Referer': base_url,
                'Origin': urlparse(base_url).netloc,
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Forwarded-Proto': 'https'
            })
            
            async with self.session.get(base_url, headers=headers) as response:
                content = await response.text()
                
                # Analyze response
                from .content_analysis import analyze_carrier_response
                analysis = analyze_carrier_response(content, dict(response.headers), carrier, pro_number)
                
                return AlternativeMethodResult(
                    method_type=AlternativeMethodType.HEADER_SPOOFING,
                    success=not analysis.is_blocked,
                    response_time=time.time() - start_time,
                    status_code=response.status,
                    tracking_data=analysis.tracking_data,
                    method_details={
                        'blocking_mechanism': analysis.blocking_mechanism.value,
                        'confidence': analysis.confidence_score
                    }
                )
        
        except Exception as e:
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.HEADER_SPOOFING,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _try_aggregators(self, pro_number: str, carrier: str) -> AlternativeMethodResult:
        """Try third-party aggregators"""
        start_time = time.time()
        
        try:
            # Try first available aggregator (would need API keys in production)
            aggregator_name = 'trackingmore'  # Example
            
            result = await self.aggregator.track_via_aggregator(
                aggregator_name, pro_number, carrier, self.session
            )
            
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.THIRD_PARTY_AGGREGATOR,
                success=result.get('success', False),
                response_time=time.time() - start_time,
                status_code=result.get('status_code'),
                tracking_data=result.get('data'),
                method_details={
                    'aggregator': aggregator_name,
                    'error': result.get('error')
                }
            )
        
        except Exception as e:
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.THIRD_PARTY_AGGREGATOR,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _try_intelligent_timing(self, pro_number: str, carrier: str, base_url: str) -> AlternativeMethodResult:
        """Try intelligent request timing"""
        start_time = time.time()
        
        try:
            # Use conservative timing pattern
            delay = random.choice(self.timing_patterns['conservative'])
            await asyncio.sleep(delay)
            
            # Make request with human-like timing
            async with self.session.get(
                base_url,
                headers={'User-Agent': random.choice(self.mobile_user_agents)}
            ) as response:
                content = await response.text()
                
                # Analyze response
                from .content_analysis import analyze_carrier_response
                analysis = analyze_carrier_response(content, dict(response.headers), carrier, pro_number)
                
                return AlternativeMethodResult(
                    method_type=AlternativeMethodType.REQUEST_TIMING,
                    success=not analysis.is_blocked,
                    response_time=time.time() - start_time,
                    status_code=response.status,
                    tracking_data=analysis.tracking_data,
                    method_details={
                        'delay_used': delay,
                        'timing_pattern': 'conservative',
                        'blocking_mechanism': analysis.blocking_mechanism.value
                    }
                )
        
        except Exception as e:
            return AlternativeMethodResult(
                method_type=AlternativeMethodType.REQUEST_TIMING,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def find_best_method(self, pro_number: str, carrier: str, base_url: str) -> Optional[AlternativeMethodResult]:
        """Find the best working alternative method"""
        results = await self.track_with_alternatives(pro_number, carrier, base_url)
        
        # Find successful methods
        successful_methods = [r for r in results if r.success]
        
        if not successful_methods:
            return None
        
        # Return the fastest successful method
        return min(successful_methods, key=lambda x: x.response_time)
    
    async def refresh_proxy_providers(self):
        """Refresh all proxy providers"""
        for provider in self.proxy_providers:
            try:
                await provider.refresh_proxies()
            except Exception as e:
                logger.warning(f"Failed to refresh {provider.name}: {e}")


async def test_alternative_methods(pro_number: str, carrier: str, base_url: str) -> List[AlternativeMethodResult]:
    """
    Convenience function to test alternative methods
    """
    async with AlternativeMethodsEngine() as engine:
        return await engine.track_with_alternatives(pro_number, carrier, base_url)


async def find_working_method(pro_number: str, carrier: str, base_url: str) -> Optional[AlternativeMethodResult]:
    """
    Convenience function to find a working method
    """
    async with AlternativeMethodsEngine() as engine:
        return await engine.find_best_method(pro_number, carrier, base_url)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Test alternative methods
        results = await test_alternative_methods("12345", "fedex", "https://www.fedex.com")
        
        for result in results:
            print(f"Method: {result.method_type.value}")
            print(f"Success: {result.success}")
            print(f"Response time: {result.response_time:.2f}s")
            if result.error_message:
                print(f"Error: {result.error_message}")
            print("---")
        
        # Find best method
        best_method = await find_working_method("12345", "fedex", "https://www.fedex.com")
        if best_method:
            print(f"Best method: {best_method.method_type.value}")
            print(f"Success: {best_method.success}")
            print(f"Response time: {best_method.response_time:.2f}s")
    
    asyncio.run(main()) 