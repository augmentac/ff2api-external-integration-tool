#!/usr/bin/env python3
"""
Connectivity Test for LTL Tracking Endpoints

This module tests basic connectivity to carrier tracking endpoints
to verify they are reachable from the cloud environment.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ConnectivityTester:
    """Test connectivity to carrier tracking endpoints"""
    
    def __init__(self):
        self.test_endpoints = {
            'fedex': [
                'https://www.fedex.com/apps/fedextrack/',
                'https://www.fedex.com/fedextrack/',
                'https://www.fedex.com/trackingCal/track'
            ],
            'estes': [
                'https://www.estes-express.com/shipment-tracking/track-shipment',
                'https://www.estes-express.com/track',
                'https://www.estes-express.com/'
            ],
            'peninsula': [
                'https://www.peninsulatrucklines.com/tracking',
                'https://peninsulatrucklines.azurewebsites.net/',
                'https://www.peninsulatrucklines.com/'
            ],
            'rl': [
                'https://www.rlcarriers.com/tracking',
                'https://www.rlcarriers.com/',
                'https://www.rlcarriers.com/shipment-tracking'
            ]
        }
    
    async def test_connectivity(self) -> Dict[str, List[Dict]]:
        """Test connectivity to all carrier endpoints"""
        results = {}
        
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for carrier, endpoints in self.test_endpoints.items():
                carrier_results = []
                
                for endpoint in endpoints:
                    try:
                        async with session.get(endpoint) as response:
                            carrier_results.append({
                                'endpoint': endpoint,
                                'status': response.status,
                                'success': response.status in [200, 301, 302],
                                'headers': dict(response.headers)
                            })
                    except asyncio.TimeoutError:
                        carrier_results.append({
                            'endpoint': endpoint,
                            'status': 'TIMEOUT',
                            'success': False,
                            'error': 'Request timed out'
                        })
                    except Exception as e:
                        carrier_results.append({
                            'endpoint': endpoint,
                            'status': 'ERROR',
                            'success': False,
                            'error': str(e)
                        })
                
                results[carrier] = carrier_results
        
        return results
    
    async def test_single_endpoint(self, url: str, method: str = 'GET', data: dict = None) -> Dict:
        """Test a single endpoint with specific parameters"""
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                if method == 'GET':
                    async with session.get(url) as response:
                        content = await response.text()
                        return {
                            'url': url,
                            'method': method,
                            'status': response.status,
                            'success': response.status in [200, 301, 302],
                            'content_length': len(content),
                            'headers': dict(response.headers)
                        }
                elif method == 'POST':
                    async with session.post(url, data=data) as response:
                        content = await response.text()
                        return {
                            'url': url,
                            'method': method,
                            'status': response.status,
                            'success': response.status in [200, 301, 302],
                            'content_length': len(content),
                            'headers': dict(response.headers)
                        }
            except Exception as e:
                return {
                    'url': url,
                    'method': method,
                    'status': 'ERROR',
                    'success': False,
                    'error': str(e)
                }


async def run_connectivity_test():
    """Run basic connectivity test"""
    tester = ConnectivityTester()
    results = await tester.test_connectivity()
    
    print("=== LTL Tracking Endpoint Connectivity Test ===")
    
    for carrier, endpoints in results.items():
        print(f"\n{carrier.upper()} Carrier:")
        for result in endpoints:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['endpoint']} - {result['status']}")
            if not result['success'] and 'error' in result:
                print(f"      Error: {result['error']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_connectivity_test())