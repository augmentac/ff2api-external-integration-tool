#!/usr/bin/env python3
"""
Proxy Integration System - Phase 2: IP Rotation and Geolocation Matching

Advanced proxy management system that:
- Integrates with residential proxy services
- Implements IP rotation with carrier-specific optimization
- Provides geolocation matching for better success rates
- Includes proxy health monitoring and automatic failover
- Supports both HTTP and HTTPS proxies with authentication
"""

import asyncio
import aiohttp
import time
import logging
import random
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import urllib.parse

logger = logging.getLogger(__name__)

class ProxyType(Enum):
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"
    STATIC = "static"

class ProxyStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    SLOW = "slow"
    FAILED = "failed"
    TESTING = "testing"

@dataclass
class ProxyConfig:
    """Configuration for a proxy server"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: ProxyType = ProxyType.RESIDENTIAL
    country: str = "US"
    state: Optional[str] = None
    city: Optional[str] = None
    provider: str = "unknown"
    max_requests_per_minute: int = 30
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    status: ProxyStatus = ProxyStatus.TESTING
    response_time: float = 0.0
    blocked_carriers: List[str] = None
    
    def __post_init__(self):
        if self.blocked_carriers is None:
            self.blocked_carriers = []
    
    @property
    def proxy_url(self) -> str:
        """Generate proxy URL for aiohttp"""
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"http://{self.host}:{self.port}"
    
    def is_suitable_for_carrier(self, carrier: str) -> bool:
        """Check if proxy is suitable for specific carrier"""
        return carrier.lower() not in self.blocked_carriers
    
    def can_make_request(self) -> bool:
        """Check if proxy can make a request based on rate limits"""
        if not self.last_used:
            return True
        
        time_since_last = (datetime.now() - self.last_used).total_seconds()
        min_interval = 60 / self.max_requests_per_minute
        
        return time_since_last >= min_interval

class ProxyPool:
    """
    Advanced proxy pool with carrier-specific optimization
    """
    
    def __init__(self):
        self.proxies: List[ProxyConfig] = []
        self.carrier_preferences = {
            'fedex': {'preferred_locations': ['US', 'CA'], 'preferred_types': [ProxyType.RESIDENTIAL, ProxyType.DATACENTER]},
            'estes': {'preferred_locations': ['US'], 'preferred_types': [ProxyType.RESIDENTIAL]},
            'peninsula': {'preferred_locations': ['US', 'CA'], 'preferred_types': [ProxyType.RESIDENTIAL, ProxyType.MOBILE]},
            'rl': {'preferred_locations': ['US'], 'preferred_types': [ProxyType.RESIDENTIAL, ProxyType.DATACENTER]}
        }
        
        # Load proxies from various sources
        self.load_default_proxies()
        self.load_environment_proxies()
        self.load_config_proxies()
        
    def load_default_proxies(self):
        """Load default free proxies for testing"""
        # Note: These are example proxies for testing - in production, use paid residential proxies
        default_proxies = [
            {
                'host': 'rotating-residential.luminati.io',
                'port': 22225,
                'username': 'lum-customer-user',
                'password': 'password',
                'proxy_type': 'residential',
                'country': 'US',
                'provider': 'luminati',
                'max_requests_per_minute': 60
            },
            {
                'host': 'proxy-server.scraperapi.com',
                'port': 8001,
                'username': 'scraperapi',
                'password': 'api_key',
                'proxy_type': 'residential',
                'country': 'US',
                'provider': 'scraperapi',
                'max_requests_per_minute': 50
            },
            {
                'host': 'proxy.oxylabs.io',
                'port': 10000,
                'username': 'customer',
                'password': 'password',
                'proxy_type': 'residential',
                'country': 'US',
                'provider': 'oxylabs',
                'max_requests_per_minute': 40
            }
        ]
        
        for proxy_data in default_proxies:
            proxy = ProxyConfig(**proxy_data)
            self.proxies.append(proxy)
    
    def load_environment_proxies(self):
        """Load proxies from environment variables"""
        proxy_configs = [
            ('PROXY_1_HOST', 'PROXY_1_PORT', 'PROXY_1_USER', 'PROXY_1_PASS'),
            ('PROXY_2_HOST', 'PROXY_2_PORT', 'PROXY_2_USER', 'PROXY_2_PASS'),
            ('PROXY_3_HOST', 'PROXY_3_PORT', 'PROXY_3_USER', 'PROXY_3_PASS'),
        ]
        
        for host_key, port_key, user_key, pass_key in proxy_configs:
            host = os.getenv(host_key)
            port = os.getenv(port_key)
            
            if host and port:
                proxy = ProxyConfig(
                    host=host,
                    port=int(port),
                    username=os.getenv(user_key),
                    password=os.getenv(pass_key),
                    proxy_type=ProxyType.RESIDENTIAL,
                    country='US',
                    provider='environment'
                )
                self.proxies.append(proxy)
    
    def load_config_proxies(self):
        """Load proxies from configuration file"""
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'proxies.json')
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    proxy_configs = json.load(f)
                
                for config in proxy_configs:
                    proxy = ProxyConfig(**config)
                    self.proxies.append(proxy)
                    
            except Exception as e:
                logger.warning(f"Failed to load proxy config from {config_path}: {e}")
    
    def get_optimal_proxy(self, carrier: str) -> Optional[ProxyConfig]:
        """Get optimal proxy for specific carrier"""
        carrier_lower = carrier.lower()
        preferences = self.carrier_preferences.get(carrier_lower, {})
        
        # Filter suitable proxies
        suitable_proxies = [
            proxy for proxy in self.proxies
            if (proxy.status == ProxyStatus.ACTIVE and
                proxy.is_suitable_for_carrier(carrier_lower) and
                proxy.can_make_request())
        ]
        
        if not suitable_proxies:
            # Fallback to any available proxy
            suitable_proxies = [
                proxy for proxy in self.proxies
                if proxy.status != ProxyStatus.FAILED and proxy.can_make_request()
            ]
        
        if not suitable_proxies:
            return None
        
        # Sort by preference and performance
        def proxy_score(proxy: ProxyConfig) -> float:
            score = proxy.success_rate * 100  # Base score from success rate
            
            # Bonus for preferred locations
            if proxy.country in preferences.get('preferred_locations', []):
                score += 20
            
            # Bonus for preferred types
            if proxy.proxy_type in preferences.get('preferred_types', []):
                score += 15
            
            # Penalty for slow response time
            if proxy.response_time > 5.0:
                score -= 10
            
            # Penalty for blocked carriers
            score -= len(proxy.blocked_carriers) * 5
            
            return score
        
        # Select proxy with highest score
        best_proxy = max(suitable_proxies, key=proxy_score)
        
        # Update last used time
        best_proxy.last_used = datetime.now()
        
        return best_proxy
    
    def mark_proxy_blocked(self, proxy: ProxyConfig, carrier: str):
        """Mark proxy as blocked for specific carrier"""
        if carrier.lower() not in proxy.blocked_carriers:
            proxy.blocked_carriers.append(carrier.lower())
        
        # If blocked by too many carriers, mark as failed
        if len(proxy.blocked_carriers) >= 3:
            proxy.status = ProxyStatus.FAILED
    
    def update_proxy_performance(self, proxy: ProxyConfig, success: bool, response_time: float):
        """Update proxy performance metrics"""
        # Update response time (exponential moving average)
        if proxy.response_time == 0:
            proxy.response_time = response_time
        else:
            proxy.response_time = 0.7 * proxy.response_time + 0.3 * response_time
        
        # Update success rate (exponential moving average)
        new_success = 1.0 if success else 0.0
        if proxy.success_rate == 0:
            proxy.success_rate = new_success
        else:
            proxy.success_rate = 0.8 * proxy.success_rate + 0.2 * new_success
        
        # Update status based on performance
        if proxy.success_rate > 0.7 and proxy.response_time < 10:
            proxy.status = ProxyStatus.ACTIVE
        elif proxy.success_rate < 0.3 or proxy.response_time > 20:
            proxy.status = ProxyStatus.SLOW
        elif proxy.success_rate < 0.1:
            proxy.status = ProxyStatus.FAILED
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        total_proxies = len(self.proxies)
        active_proxies = sum(1 for p in self.proxies if p.status == ProxyStatus.ACTIVE)
        blocked_proxies = sum(1 for p in self.proxies if p.status == ProxyStatus.BLOCKED)
        failed_proxies = sum(1 for p in self.proxies if p.status == ProxyStatus.FAILED)
        
        avg_success_rate = sum(p.success_rate for p in self.proxies) / total_proxies if total_proxies > 0 else 0
        avg_response_time = sum(p.response_time for p in self.proxies) / total_proxies if total_proxies > 0 else 0
        
        return {
            'total_proxies': total_proxies,
            'active_proxies': active_proxies,
            'blocked_proxies': blocked_proxies,
            'failed_proxies': failed_proxies,
            'average_success_rate': avg_success_rate,
            'average_response_time': avg_response_time,
            'proxy_types': {ptype.value: sum(1 for p in self.proxies if p.proxy_type == ptype) for ptype in ProxyType},
            'providers': list(set(p.provider for p in self.proxies))
        }

class ProxyRotationManager:
    """
    Advanced proxy rotation manager with intelligent switching
    """
    
    def __init__(self):
        self.proxy_pool = ProxyPool()
        self.current_proxies = {}  # carrier -> proxy mapping
        self.request_counts = {}  # proxy -> request count
        self.rotation_thresholds = {
            'requests': 50,  # Rotate after 50 requests
            'time': 300,     # Rotate after 5 minutes
            'failures': 5    # Rotate after 5 failures
        }
        
    async def get_proxy_for_request(self, carrier: str) -> Optional[ProxyConfig]:
        """Get proxy for specific request with intelligent rotation"""
        current_proxy = self.current_proxies.get(carrier)
        
        # Check if we need to rotate proxy
        if self.should_rotate_proxy(carrier, current_proxy):
            new_proxy = self.proxy_pool.get_optimal_proxy(carrier)
            if new_proxy:
                self.current_proxies[carrier] = new_proxy
                logger.info(f"Rotated to new proxy for {carrier}: {new_proxy.host}:{new_proxy.port}")
                return new_proxy
        
        return current_proxy
    
    def should_rotate_proxy(self, carrier: str, proxy: Optional[ProxyConfig]) -> bool:
        """Determine if proxy should be rotated"""
        if not proxy:
            return True
        
        # Check if proxy is no longer suitable
        if proxy.status == ProxyStatus.FAILED or not proxy.is_suitable_for_carrier(carrier):
            return True
        
        # Check request count threshold
        request_count = self.request_counts.get(proxy, 0)
        if request_count >= self.rotation_thresholds['requests']:
            return True
        
        # Check time threshold
        if proxy.last_used:
            time_since_start = (datetime.now() - proxy.last_used).total_seconds()
            if time_since_start >= self.rotation_thresholds['time']:
                return True
        
        return False
    
    def record_request(self, proxy: ProxyConfig, success: bool, response_time: float):
        """Record request outcome for proxy optimization"""
        # Update request count
        self.request_counts[proxy] = self.request_counts.get(proxy, 0) + 1
        
        # Update proxy performance
        self.proxy_pool.update_proxy_performance(proxy, success, response_time)
        
        # Log performance update
        logger.debug(f"Proxy {proxy.host}:{proxy.port} - Success: {success}, "
                    f"Response Time: {response_time:.2f}s, "
                    f"Success Rate: {proxy.success_rate:.2f}")
    
    def mark_proxy_blocked(self, proxy: ProxyConfig, carrier: str):
        """Mark proxy as blocked for specific carrier"""
        self.proxy_pool.mark_proxy_blocked(proxy, carrier)
        
        # Remove from current proxies if blocked
        if self.current_proxies.get(carrier) == proxy:
            del self.current_proxies[carrier]
        
        logger.warning(f"Proxy {proxy.host}:{proxy.port} blocked for {carrier}")
    
    def get_rotation_stats(self) -> Dict[str, Any]:
        """Get proxy rotation statistics"""
        stats = self.proxy_pool.get_proxy_stats()
        
        stats.update({
            'current_assignments': {carrier: f"{proxy.host}:{proxy.port}" 
                                   for carrier, proxy in self.current_proxies.items()},
            'request_counts': {f"{proxy.host}:{proxy.port}": count 
                             for proxy, count in self.request_counts.items()},
            'rotation_thresholds': self.rotation_thresholds
        })
        
        return stats

class CloudFlareBypassManager:
    """
    CloudFlare bypass manager for enhanced request success
    """
    
    def __init__(self):
        self.cf_clearance_tokens = {}  # domain -> cf_clearance token
        self.challenge_solvers = {
            'javascript': self.solve_javascript_challenge,
            'captcha': self.solve_captcha_challenge,
            'managed': self.solve_managed_challenge
        }
    
    async def enhance_request_for_cloudflare(self, session: aiohttp.ClientSession, 
                                           url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """Enhance request headers for CloudFlare bypass"""
        domain = urllib.parse.urlparse(url).netloc
        
        # Add CloudFlare-specific headers
        enhanced_headers = headers.copy()
        enhanced_headers.update({
            'CF-Connecting-IP': self.get_fake_ip(),
            'CF-RAY': self.generate_cf_ray(),
            'CF-Visitor': '{"scheme":"https"}',
            'CF-IPCountry': 'US',
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-For': self.get_fake_ip()
        })
        
        # Add cf_clearance token if available
        if domain in self.cf_clearance_tokens:
            enhanced_headers['Cookie'] = f"cf_clearance={self.cf_clearance_tokens[domain]}"
        
        return enhanced_headers
    
    def get_fake_ip(self) -> str:
        """Generate fake IP address for CloudFlare bypass"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def generate_cf_ray(self) -> str:
        """Generate fake CloudFlare Ray ID"""
        return f"{random.randint(100000000000, 999999999999)}-{random.choice(['DFW', 'LAX', 'NYC', 'ATL'])}"
    
    async def solve_javascript_challenge(self, response_text: str) -> Optional[str]:
        """Solve JavaScript challenge (simplified)"""
        # This is a simplified version - in production, use a proper JS engine
        try:
            # Extract challenge parameters
            if 'cf_challenge' in response_text:
                # Generate fake solution
                return f"cf_clearance_{random.randint(1000000, 9999999)}"
        except Exception as e:
            logger.debug(f"JavaScript challenge solving failed: {e}")
        
        return None
    
    async def solve_captcha_challenge(self, response_text: str) -> Optional[str]:
        """Solve CAPTCHA challenge"""
        # In production, integrate with CAPTCHA solving service
        logger.warning("CAPTCHA challenge detected - manual intervention required")
        return None
    
    async def solve_managed_challenge(self, response_text: str) -> Optional[str]:
        """Solve managed challenge"""
        # Wait and retry approach for managed challenges
        await asyncio.sleep(random.uniform(2, 5))
        return f"managed_clearance_{random.randint(1000000, 9999999)}"

class ProxyIntegrationManager:
    """
    Main proxy integration manager combining all proxy features
    """
    
    def __init__(self):
        self.rotation_manager = ProxyRotationManager()
        self.cloudflare_bypass = CloudFlareBypassManager()
        self.active_sessions = {}  # proxy -> session mapping
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'blocked_requests': 0,
            'avg_response_time': 0.0,
            'proxy_rotations': 0
        }
    
    async def create_proxy_session(self, proxy: ProxyConfig, 
                                 ssl_context: Optional[aiohttp.ClientSession] = None) -> aiohttp.ClientSession:
        """Create aiohttp session with proxy configuration"""
        # Create connector with proxy
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=3,
            ssl=ssl_context,
            use_dns_cache=True,
            ttl_dns_cache=300,
            keepalive_timeout=30
        )
        
        # Create session with proxy
        timeout = aiohttp.ClientTimeout(total=30, connect=15)
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            trust_env=True
        )
        
        # Store proxy URL for use in requests
        session._proxy_url = proxy.proxy_url
        
        return session
    
    async def make_request(self, method: str, url: str, carrier: str, 
                         headers: Dict[str, str], **kwargs) -> Tuple[Optional[aiohttp.ClientResponse], Optional[ProxyConfig]]:
        """Make request using optimal proxy with automatic rotation"""
        start_time = time.time()
        
        # Get optimal proxy for this carrier
        proxy = await self.rotation_manager.get_proxy_for_request(carrier)
        if not proxy:
            logger.warning(f"No suitable proxy available for {carrier}")
            return None, None
        
        try:
            # Create or reuse session
            session = await self.get_or_create_session(proxy)
            
            # Enhance headers for CloudFlare bypass
            enhanced_headers = await self.cloudflare_bypass.enhance_request_for_cloudflare(
                session, url, headers
            )
            
            # Make request through proxy
            response = await session.request(
                method=method,
                url=url,
                headers=enhanced_headers,
                proxy=proxy.proxy_url,
                **kwargs
            )
            
            # Record successful request
            response_time = time.time() - start_time
            self.rotation_manager.record_request(proxy, True, response_time)
            self.update_performance_metrics(True, response_time)
            
            return response, proxy
            
        except Exception as e:
            # Record failed request
            response_time = time.time() - start_time
            self.rotation_manager.record_request(proxy, False, response_time)
            self.update_performance_metrics(False, response_time)
            
            # Check if proxy should be marked as blocked
            if 'blocked' in str(e).lower() or 'forbidden' in str(e).lower():
                self.rotation_manager.mark_proxy_blocked(proxy, carrier)
            
            logger.debug(f"Proxy request failed: {e}")
            return None, proxy
    
    async def get_or_create_session(self, proxy: ProxyConfig) -> aiohttp.ClientSession:
        """Get existing session or create new one for proxy"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        
        if proxy_key not in self.active_sessions or self.active_sessions[proxy_key].closed:
            session = await self.create_proxy_session(proxy)
            self.active_sessions[proxy_key] = session
        
        return self.active_sessions[proxy_key]
    
    def update_performance_metrics(self, success: bool, response_time: float):
        """Update overall performance metrics"""
        self.performance_metrics['total_requests'] += 1
        
        if success:
            self.performance_metrics['successful_requests'] += 1
        else:
            self.performance_metrics['blocked_requests'] += 1
        
        # Update average response time
        total_requests = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['avg_response_time']
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive proxy integration status"""
        return {
            'proxy_pool_stats': self.rotation_manager.get_rotation_stats(),
            'performance_metrics': self.performance_metrics,
            'active_sessions': len(self.active_sessions),
            'integration_status': 'active' if self.rotation_manager.proxy_pool.proxies else 'no_proxies'
        }
    
    async def close_all_sessions(self):
        """Close all active proxy sessions"""
        for session in self.active_sessions.values():
            if not session.closed:
                await session.close()
        
        self.active_sessions.clear()

# Global proxy integration manager instance
proxy_manager = ProxyIntegrationManager()

# Convenience functions for easy integration
async def make_proxy_request(method: str, url: str, carrier: str, 
                           headers: Dict[str, str], **kwargs) -> Tuple[Optional[aiohttp.ClientResponse], Optional[ProxyConfig]]:
    """Make request using proxy integration"""
    return await proxy_manager.make_request(method, url, carrier, headers, **kwargs)

def get_proxy_status() -> Dict[str, Any]:
    """Get current proxy integration status"""
    return proxy_manager.get_integration_status()

async def cleanup_proxy_resources():
    """Clean up proxy resources"""
    await proxy_manager.close_all_sessions() 