#!/usr/bin/env python3
"""
Network Diagnostics System for LTL Tracking
Comprehensive analysis of network connectivity issues, blocking patterns, and infrastructure limitations
"""

import asyncio
import aiohttp
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta
import random
from urllib.parse import urlparse
import socket

logger = logging.getLogger(__name__)


class BlockingType(Enum):
    """Types of blocking mechanisms detected"""
    CLOUDFLARE = "cloudflare"
    CAPTCHA = "captcha"
    IP_BLOCKING = "ip_blocking"
    RATE_LIMITING = "rate_limiting"
    GEOGRAPHIC = "geographic"
    USER_AGENT = "user_agent"
    AUTHENTICATION = "authentication"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class NetworkDiagnosticResult:
    """Result of network diagnostic test"""
    carrier: str
    test_type: str
    success: bool
    response_time: float
    status_code: Optional[int] = None
    blocking_type: Optional[BlockingType] = None
    error_message: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = None
    response_content: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NetworkDiagnostics:
    """
    Comprehensive network diagnostics system
    Tests connectivity, analyzes blocking patterns, and provides actionable insights
    """
    
    def __init__(self):
        self.session = None
        self.user_agents = [
            # Desktop browsers
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            
            # Mobile browsers
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
            
            # Legitimate crawlers
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            
            # Business/corporate user agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        ]
        
        self.carrier_endpoints = {
            'fedex': {
                'homepage': 'https://www.fedex.com',
                'tracking': 'https://www.fedex.com/fedextrack/',
                'mobile': 'https://m.fedex.com',
                'api_discovery': [
                    'https://www.fedex.com/trackingCal/track',
                    'https://www.fedex.com/apps/fedextrack/',
                    'https://api.fedex.com/track/v1',
                    'https://www.fedex.com/en-us/tracking.html'
                ]
            },
            'estes': {
                'homepage': 'https://www.estes-express.com',
                'tracking': 'https://www.estes-express.com/myestes/shipment-tracking',
                'mobile': 'https://m.estes-express.com',
                'api_discovery': [
                    'https://www.estes-express.com/api/shipment/track',
                    'https://www.estes-express.com/resources/tracking',
                    'https://www.estes-express.com/myestes/api/tracking'
                ]
            },
            'peninsula': {
                'homepage': 'https://www.peninsulatrucklines.com',
                'tracking': 'https://www.peninsulatrucklines.com/track-shipment',
                'mobile': 'https://m.peninsulatrucklines.com',
                'api_discovery': [
                    'https://www.peninsulatrucklines.com/wp-json/wp/v2',
                    'https://www.peninsulatrucklines.com/api/track',
                    'https://www.peninsulatrucklines.com/tracking-api'
                ]
            },
            'rl': {
                'homepage': 'https://www.rlcarriers.com',
                'tracking': 'https://www.rlcarriers.com/tracking',
                'mobile': 'https://m.rlcarriers.com',
                'api_discovery': [
                    'https://www.rlcarriers.com/api/shipment/track',
                    'https://www.rlcarriers.com/resources/api/tracking',
                    'https://api.rlcarriers.com/track'
                ]
            }
        }
        
        # Common blocking patterns
        self.blocking_patterns = {
            BlockingType.CLOUDFLARE: [
                'cloudflare',
                'cf-ray',
                'checking your browser',
                'ddos protection',
                'security check',
                'please wait while we verify',
                'ray id',
                'cloudflare-nginx'
            ],
            BlockingType.CAPTCHA: [
                'captcha',
                'recaptcha',
                'hcaptcha',
                'security verification',
                'prove you are human',
                'robot verification',
                'access denied',
                'suspicious activity'
            ],
            BlockingType.IP_BLOCKING: [
                'ip blocked',
                'ip address blocked',
                'access denied from your location',
                'banned ip',
                'blocked ip range',
                'unauthorized access',
                'forbidden access'
            ],
            BlockingType.RATE_LIMITING: [
                'rate limit',
                'too many requests',
                'request limit exceeded',
                'try again later',
                'rate exceeded',
                'throttled',
                'slow down'
            ],
            BlockingType.GEOGRAPHIC: [
                'not available in your region',
                'geographic restriction',
                'location blocked',
                'country blocked',
                'region blocked',
                'vpn detected',
                'proxy detected'
            ],
            BlockingType.USER_AGENT: [
                'invalid user agent',
                'user agent blocked',
                'bot detected',
                'automated request',
                'script detected',
                'crawler blocked'
            ],
            BlockingType.AUTHENTICATION: [
                'login required',
                'authentication required',
                'please sign in',
                'unauthorized',
                'access denied',
                'authentication failed',
                'session expired'
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            enable_cleanup_closed=True,
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def run_full_diagnostics(self, carriers: List[str] = None) -> Dict[str, Any]:
        """
        Run comprehensive network diagnostics for all or specified carriers
        """
        if carriers is None:
            carriers = list(self.carrier_endpoints.keys())
        
        logger.info(f"🔍 Running full network diagnostics for carriers: {carriers}")
        
        results = {
            'timestamp': datetime.now(),
            'carriers': {},
            'summary': {
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'blocking_types': {},
                'recommendations': []
            }
        }
        
        for carrier in carriers:
            logger.info(f"📡 Diagnosing {carrier}...")
            carrier_results = await self._diagnose_carrier(carrier)
            results['carriers'][carrier] = carrier_results
            
            # Update summary
            for test_result in carrier_results['tests']:
                results['summary']['total_tests'] += 1
                if test_result.success:
                    results['summary']['successful_tests'] += 1
                else:
                    results['summary']['failed_tests'] += 1
                    if test_result.blocking_type:
                        blocking_type = test_result.blocking_type.value
                        if blocking_type not in results['summary']['blocking_types']:
                            results['summary']['blocking_types'][blocking_type] = 0
                        results['summary']['blocking_types'][blocking_type] += 1
        
        # Generate recommendations
        results['summary']['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    async def _diagnose_carrier(self, carrier: str) -> Dict[str, Any]:
        """
        Diagnose network connectivity issues for a specific carrier
        """
        if carrier not in self.carrier_endpoints:
            return {
                'carrier': carrier,
                'error': f'Unknown carrier: {carrier}',
                'tests': []
            }
        
        endpoints = self.carrier_endpoints[carrier]
        tests = []
        
        # Test 1: Basic connectivity to homepage
        test_result = await self._test_basic_connectivity(carrier, endpoints['homepage'])
        tests.append(test_result)
        
        # Test 2: Tracking page accessibility
        test_result = await self._test_tracking_page(carrier, endpoints['tracking'])
        tests.append(test_result)
        
        # Test 3: Mobile endpoint accessibility
        test_result = await self._test_mobile_endpoint(carrier, endpoints['mobile'])
        tests.append(test_result)
        
        # Test 4: User agent variation
        test_results = await self._test_user_agent_variation(carrier, endpoints['homepage'])
        tests.extend(test_results)
        
        # Test 5: API discovery
        test_results = await self._test_api_discovery(carrier, endpoints['api_discovery'])
        tests.extend(test_results)
        
        # Test 6: DNS resolution
        test_result = await self._test_dns_resolution(carrier, endpoints['homepage'])
        tests.append(test_result)
        
        return {
            'carrier': carrier,
            'tests': tests,
            'success_rate': sum(1 for t in tests if t.success) / len(tests) if tests else 0,
            'primary_blocking_type': self._identify_primary_blocking_type(tests),
            'recommendations': self._generate_carrier_recommendations(carrier, tests)
        }
    
    async def _test_basic_connectivity(self, carrier: str, url: str) -> NetworkDiagnosticResult:
        """Test basic HTTP connectivity to carrier homepage"""
        start_time = time.time()
        
        try:
            async with self.session.get(
                url,
                headers={'User-Agent': random.choice(self.user_agents)},
                allow_redirects=True
            ) as response:
                response_time = time.time() - start_time
                content = await response.text()
                
                # Analyze response for blocking patterns
                blocking_type = self._analyze_blocking_patterns(content, response.headers)
                
                return NetworkDiagnosticResult(
                    carrier=carrier,
                    test_type='basic_connectivity',
                    success=response.status == 200 and blocking_type is None,
                    response_time=response_time,
                    status_code=response.status,
                    blocking_type=blocking_type,
                    response_headers=dict(response.headers),
                    response_content=content[:1000] if len(content) > 1000 else content
                )
        
        except Exception as e:
            response_time = time.time() - start_time
            return NetworkDiagnosticResult(
                carrier=carrier,
                test_type='basic_connectivity',
                success=False,
                response_time=response_time,
                blocking_type=BlockingType.NETWORK_ERROR,
                error_message=str(e)
            )
    
    async def _test_tracking_page(self, carrier: str, url: str) -> NetworkDiagnosticResult:
        """Test access to tracking page"""
        start_time = time.time()
        
        try:
            async with self.session.get(
                url,
                headers={'User-Agent': random.choice(self.user_agents)},
                allow_redirects=True
            ) as response:
                response_time = time.time() - start_time
                content = await response.text()
                
                # Check for tracking-specific blocking
                blocking_type = self._analyze_tracking_blocking(content, response.headers)
                
                return NetworkDiagnosticResult(
                    carrier=carrier,
                    test_type='tracking_page',
                    success=response.status == 200 and blocking_type is None,
                    response_time=response_time,
                    status_code=response.status,
                    blocking_type=blocking_type,
                    response_headers=dict(response.headers),
                    response_content=content[:1000] if len(content) > 1000 else content
                )
        
        except Exception as e:
            response_time = time.time() - start_time
            return NetworkDiagnosticResult(
                carrier=carrier,
                test_type='tracking_page',
                success=False,
                response_time=response_time,
                blocking_type=BlockingType.NETWORK_ERROR,
                error_message=str(e)
            )
    
    async def _test_mobile_endpoint(self, carrier: str, url: str) -> NetworkDiagnosticResult:
        """Test mobile endpoint accessibility"""
        start_time = time.time()
        mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
        
        try:
            async with self.session.get(
                url,
                headers={'User-Agent': mobile_ua},
                allow_redirects=True
            ) as response:
                response_time = time.time() - start_time
                content = await response.text()
                
                blocking_type = self._analyze_blocking_patterns(content, response.headers)
                
                return NetworkDiagnosticResult(
                    carrier=carrier,
                    test_type='mobile_endpoint',
                    success=response.status == 200 and blocking_type is None,
                    response_time=response_time,
                    status_code=response.status,
                    blocking_type=blocking_type,
                    response_headers=dict(response.headers),
                    response_content=content[:1000] if len(content) > 1000 else content,
                    user_agent=mobile_ua
                )
        
        except Exception as e:
            response_time = time.time() - start_time
            return NetworkDiagnosticResult(
                carrier=carrier,
                test_type='mobile_endpoint',
                success=False,
                response_time=response_time,
                blocking_type=BlockingType.NETWORK_ERROR,
                error_message=str(e),
                user_agent=mobile_ua
            )
    
    async def _test_user_agent_variation(self, carrier: str, url: str) -> List[NetworkDiagnosticResult]:
        """Test different user agents to identify UA-based blocking"""
        results = []
        
        # Test with 3 different user agents
        test_user_agents = random.sample(self.user_agents, min(3, len(self.user_agents)))
        
        for ua in test_user_agents:
            start_time = time.time()
            
            try:
                async with self.session.get(
                    url,
                    headers={'User-Agent': ua},
                    allow_redirects=True
                ) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    
                    blocking_type = self._analyze_blocking_patterns(content, response.headers)
                    
                    results.append(NetworkDiagnosticResult(
                        carrier=carrier,
                        test_type='user_agent_variation',
                        success=response.status == 200 and blocking_type is None,
                        response_time=response_time,
                        status_code=response.status,
                        blocking_type=blocking_type,
                        response_headers=dict(response.headers),
                        response_content=content[:500] if len(content) > 500 else content,
                        user_agent=ua
                    ))
            
            except Exception as e:
                response_time = time.time() - start_time
                results.append(NetworkDiagnosticResult(
                    carrier=carrier,
                    test_type='user_agent_variation',
                    success=False,
                    response_time=response_time,
                    blocking_type=BlockingType.NETWORK_ERROR,
                    error_message=str(e),
                    user_agent=ua
                ))
            
            # Rate limiting between tests
            await asyncio.sleep(0.5)
        
        return results
    
    async def _test_api_discovery(self, carrier: str, api_urls: List[str]) -> List[NetworkDiagnosticResult]:
        """Test API endpoint discovery"""
        results = []
        
        for api_url in api_urls:
            start_time = time.time()
            
            try:
                async with self.session.get(
                    api_url,
                    headers={
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'application/json, text/plain, */*',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    allow_redirects=True
                ) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    
                    # API endpoints may return different status codes
                    success = response.status in [200, 201, 202, 400, 401, 403, 404, 405, 422]
                    blocking_type = self._analyze_blocking_patterns(content, response.headers) if not success else None
                    
                    results.append(NetworkDiagnosticResult(
                        carrier=carrier,
                        test_type='api_discovery',
                        success=success,
                        response_time=response_time,
                        status_code=response.status,
                        blocking_type=blocking_type,
                        response_headers=dict(response.headers),
                        response_content=content[:500] if len(content) > 500 else content
                    ))
            
            except Exception as e:
                response_time = time.time() - start_time
                results.append(NetworkDiagnosticResult(
                    carrier=carrier,
                    test_type='api_discovery',
                    success=False,
                    response_time=response_time,
                    blocking_type=BlockingType.NETWORK_ERROR,
                    error_message=str(e)
                ))
            
            # Rate limiting between API tests
            await asyncio.sleep(0.3)
        
        return results
    
    async def _test_dns_resolution(self, carrier: str, url: str) -> NetworkDiagnosticResult:
        """Test DNS resolution"""
        start_time = time.time()
        
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            
            # Test DNS resolution
            ip_addresses = socket.gethostbyname_ex(hostname)
            response_time = time.time() - start_time
            
            return NetworkDiagnosticResult(
                carrier=carrier,
                test_type='dns_resolution',
                success=True,
                response_time=response_time,
                response_content=f"Resolved to: {ip_addresses[2]}"
            )
        
        except Exception as e:
            response_time = time.time() - start_time
            return NetworkDiagnosticResult(
                carrier=carrier,
                test_type='dns_resolution',
                success=False,
                response_time=response_time,
                blocking_type=BlockingType.NETWORK_ERROR,
                error_message=str(e)
            )
    
    def _analyze_blocking_patterns(self, content: str, headers: dict) -> Optional[BlockingType]:
        """Analyze response content and headers for blocking patterns"""
        content_lower = content.lower()
        
        # Check headers first
        for header, value in headers.items():
            header_lower = header.lower()
            value_lower = str(value).lower()
            
            if 'cf-ray' in header_lower or 'cloudflare' in value_lower:
                return BlockingType.CLOUDFLARE
            
            if 'x-rate-limit' in header_lower or 'retry-after' in header_lower:
                return BlockingType.RATE_LIMITING
        
        # Check content patterns
        for blocking_type, patterns in self.blocking_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    return blocking_type
        
        return None
    
    def _analyze_tracking_blocking(self, content: str, headers: dict) -> Optional[BlockingType]:
        """Analyze tracking-specific blocking patterns"""
        # First check general blocking patterns
        blocking_type = self._analyze_blocking_patterns(content, headers)
        if blocking_type:
            return blocking_type
        
        # Check for tracking-specific issues
        content_lower = content.lower()
        
        # Check for authentication walls
        auth_indicators = [
            'please log in',
            'sign in to track',
            'account required',
            'registration required',
            'customer login'
        ]
        
        for indicator in auth_indicators:
            if indicator in content_lower:
                return BlockingType.AUTHENTICATION
        
        return None
    
    def _identify_primary_blocking_type(self, tests: List[NetworkDiagnosticResult]) -> Optional[BlockingType]:
        """Identify the primary blocking type affecting a carrier"""
        blocking_counts = {}
        
        for test in tests:
            if test.blocking_type:
                blocking_type = test.blocking_type
                if blocking_type not in blocking_counts:
                    blocking_counts[blocking_type] = 0
                blocking_counts[blocking_type] += 1
        
        if not blocking_counts:
            return None
        
        # Return the most common blocking type
        return max(blocking_counts, key=blocking_counts.get)
    
    def _generate_carrier_recommendations(self, carrier: str, tests: List[NetworkDiagnosticResult]) -> List[str]:
        """Generate specific recommendations for a carrier based on test results"""
        recommendations = []
        
        # Analyze test results
        success_rate = sum(1 for t in tests if t.success) / len(tests) if tests else 0
        primary_blocking = self._identify_primary_blocking_type(tests)
        
        if success_rate == 0:
            recommendations.append(f"❌ Complete blocking detected for {carrier}")
            recommendations.append("🔧 Immediate action required - consider alternative tracking methods")
        elif success_rate < 0.3:
            recommendations.append(f"⚠️ Severe blocking detected for {carrier} (success rate: {success_rate:.1%})")
            recommendations.append("🔧 Major intervention required")
        elif success_rate < 0.7:
            recommendations.append(f"⚠️ Moderate blocking detected for {carrier} (success rate: {success_rate:.1%})")
            recommendations.append("🔧 Optimization recommended")
        
        # Specific recommendations based on blocking type
        if primary_blocking:
            if primary_blocking == BlockingType.CLOUDFLARE:
                recommendations.append("🌐 CloudFlare protection detected")
                recommendations.append("💡 Try: Different IP ranges, browser fingerprinting, slower request patterns")
            elif primary_blocking == BlockingType.RATE_LIMITING:
                recommendations.append("⏱️ Rate limiting detected")
                recommendations.append("💡 Try: Longer delays between requests, distributed request patterns")
            elif primary_blocking == BlockingType.USER_AGENT:
                recommendations.append("🤖 User agent blocking detected")
                recommendations.append("💡 Try: Rotate user agents, use legitimate browser signatures")
            elif primary_blocking == BlockingType.IP_BLOCKING:
                recommendations.append("🚫 IP blocking detected")
                recommendations.append("💡 Try: Proxy rotation, different cloud providers, residential IPs")
            elif primary_blocking == BlockingType.AUTHENTICATION:
                recommendations.append("🔐 Authentication required")
                recommendations.append("💡 Try: Guest endpoints, mobile APIs, alternative tracking methods")
        
        return recommendations
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on diagnostic results"""
        recommendations = []
        
        summary = results['summary']
        success_rate = summary['successful_tests'] / summary['total_tests'] if summary['total_tests'] > 0 else 0
        
        # Overall assessment
        if success_rate == 0:
            recommendations.append("🚨 CRITICAL: 100% failure rate - infrastructure-level blocking detected")
            recommendations.append("🔧 Priority: Immediate investigation of IP blocking, CloudFlare protection")
        elif success_rate < 0.1:
            recommendations.append("🚨 SEVERE: <10% success rate - systematic blocking")
            recommendations.append("🔧 Priority: Alternative IP ranges, proxy rotation, API discovery")
        elif success_rate < 0.3:
            recommendations.append("⚠️ MODERATE: <30% success rate - significant blocking")
            recommendations.append("🔧 Priority: User agent optimization, request pattern changes")
        elif success_rate < 0.7:
            recommendations.append("⚠️ MINOR: <70% success rate - some blocking")
            recommendations.append("🔧 Priority: Fine-tuning, carrier-specific optimizations")
        else:
            recommendations.append("✅ GOOD: >70% success rate - manageable blocking")
            recommendations.append("🔧 Priority: Monitor and maintain current approach")
        
        # Blocking type specific recommendations
        blocking_types = summary['blocking_types']
        if blocking_types:
            most_common = max(blocking_types, key=blocking_types.get)
            recommendations.append(f"🎯 Primary issue: {most_common.replace('_', ' ').title()}")
            
            if most_common == 'cloudflare':
                recommendations.append("🌐 CloudFlare bypass priority - try residential proxies, slower patterns")
            elif most_common == 'ip_blocking':
                recommendations.append("🚫 IP rotation priority - change cloud provider IP ranges")
            elif most_common == 'rate_limiting':
                recommendations.append("⏱️ Rate limiting - implement 3-5 second delays between requests")
        
        return recommendations


async def run_quick_diagnostic(carriers: List[str] = None) -> Dict[str, Any]:
    """
    Run a quick diagnostic test
    Convenience function for easy testing
    """
    async with NetworkDiagnostics() as diagnostics:
        return await diagnostics.run_full_diagnostics(carriers)


async def test_single_carrier(carrier: str) -> Dict[str, Any]:
    """
    Test a single carrier
    Convenience function for focused testing
    """
    async with NetworkDiagnostics() as diagnostics:
        return await diagnostics._diagnose_carrier(carrier)


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        # Test all carriers
        results = await run_quick_diagnostic()
        print(json.dumps(results, indent=2, default=str))
        
        # Test specific carrier
        fedex_results = await test_single_carrier('fedex')
        print(json.dumps(fedex_results, indent=2, default=str))
    
    asyncio.run(main()) 